"""
DAWN — AI video creation + Bemi-Scheduler integration
FastAPI backend + static frontend
"""
import asyncio, os, time, uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from pipeline import AVATARS, run_pipeline
from scheduler_api import add_post, get_schedule

app = FastAPI(title="DAWN", docs_url=None, redoc_url=None)

# In-memory job store (resets on redeploy — acceptable for MVP)
JOBS: dict[str, dict] = {}

STATIC = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


# ── Models ────────────────────────────────────────────────────────────────────
class GenerateRequest(BaseModel):
    script: str
    avatar: str = "hoodie"          # hoodie | gym | suit
    title: str
    subtitle: str
    voice_id: Optional[str] = None  # None = use ELEVENLABS_VOICE_ID env var

class ScheduleRequest(BaseModel):
    job_id: str
    campaign: str
    caption: str
    yt_title: str
    scheduled_utc: str              # ISO format: 2026-07-28T16:00:00Z
    platforms: list[str] = ["facebook", "instagram", "youtube"]


# ── Routes ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return FileResponse(str(STATIC / "index.html"))


@app.get("/api/avatars")
def avatars():
    return {"avatars": list(AVATARS.keys())}


@app.get("/api/voices")
def voices():
    voice_id = os.environ.get("ELEVENLABS_VOICE_ID", "")
    return {"voices": [{"id": voice_id, "name": "Ransford (Your Voice)", "default": True}]}


@app.post("/api/generate")
async def generate(req: GenerateRequest, bg: BackgroundTasks):
    if req.avatar not in AVATARS:
        raise HTTPException(400, f"Unknown avatar: {req.avatar}. Choose: {list(AVATARS)}")
    if not req.script.strip():
        raise HTTPException(400, "script is required")

    job_id = str(uuid.uuid4())[:8]
    JOBS[job_id] = {
        "id":        job_id,
        "status":    "queued",
        "log":       [],
        "video_url": None,
        "error":     None,
        "created":   datetime.now(timezone.utc).isoformat(),
        "request":   req.model_dump(),
    }
    bg.add_task(run_pipeline, job_id, req.script, req.avatar,
                req.title, req.subtitle, JOBS, req.voice_id)
    return {"job_id": job_id, "status": "queued"}


@app.get("/api/jobs/{job_id}")
def job_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@app.get("/api/jobs")
def list_jobs():
    return {"jobs": [
        {"id": j["id"], "status": j["status"], "created": j["created"]}
        for j in sorted(JOBS.values(), key=lambda x: x["created"], reverse=True)
    ]}


@app.post("/api/schedule")
def schedule(req: ScheduleRequest):
    job = JOBS.get(req.job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if job["status"] != "done":
        raise HTTPException(400, f"Job not complete — status: {job['status']}")

    post_id = f"{req.campaign}_{req.job_id}_{int(time.time())}"
    result = add_post({
        "id":            post_id,
        "campaign":      req.campaign,
        "video_url":     job["video_url"],
        "caption":       req.caption,
        "yt_title":      req.yt_title[:100],
        "scheduled_utc": req.scheduled_utc,
        "platforms":     req.platforms,
        "done":          False,
    }, commit_msg=f"feat: schedule {post_id} via DAWN")

    return result


@app.get("/api/schedule")
def view_schedule():
    try:
        data, _ = get_schedule()
        posts = data.get("posts", [])
        return {
            "total": len(posts),
            "pending": sum(1 for p in posts if not p.get("done")),
            "done": sum(1 for p in posts if p.get("done")),
            "upcoming": [p for p in posts if not p.get("done")][:10],
        }
    except Exception as e:
        raise HTTPException(500, str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), reload=False)
