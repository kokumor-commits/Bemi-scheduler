"""
GitHub API — read/write master_schedule.json without local git.
Railway DAWN app uses this to add posts to the schedule.
"""
import base64, json, os
import httpx

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO  = os.environ.get("GITHUB_REPO", "kokumor-commits/Bemi-scheduler")
SCHEDULE_FILE = "video_scheduler/master_schedule.json"
GH_BASE = "https://api.github.com"

def _headers():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }


def get_schedule() -> tuple[dict, str]:
    """Returns (schedule_data, sha)."""
    r = httpx.get(
        f"{GH_BASE}/repos/{GITHUB_REPO}/contents/{SCHEDULE_FILE}",
        headers=_headers(), timeout=30,
    )
    r.raise_for_status()
    body = r.json()
    content = base64.b64decode(body["content"]).decode("utf-8")
    return json.loads(content), body["sha"]


def add_post(post: dict, commit_msg: str = None) -> dict:
    """Append one post to master_schedule.json via GitHub API. Returns updated file info."""
    data, sha = get_schedule()

    # Prevent duplicates
    if any(p["id"] == post["id"] for p in data["posts"]):
        return {"status": "already_exists", "id": post["id"]}

    data["posts"].append(post)
    updated = json.dumps(data, indent=2, ensure_ascii=False)
    encoded = base64.b64encode(updated.encode()).decode()

    msg = commit_msg or f"feat: schedule {post['id']} via DAWN"
    r = httpx.put(
        f"{GH_BASE}/repos/{GITHUB_REPO}/contents/{SCHEDULE_FILE}",
        headers=_headers(),
        json={"message": msg, "content": encoded, "sha": sha},
        timeout=30,
    )
    r.raise_for_status()
    return {"status": "scheduled", "id": post["id"], "commit": r.json()["commit"]["sha"][:7]}
