"""
Video generation pipeline:
  Script → ElevenLabs TTS → R2 (audio) → HeyGen avatar (lip-sync) → ffmpeg DAWN render → R2 (video)
"""
import asyncio, base64, os, shutil, subprocess, tempfile, time
import boto3, httpx

try:
    from faster_whisper import WhisperModel
    _WHISPER_AVAILABLE = True
except ImportError:
    _WHISPER_AVAILABLE = False

# ── Credentials ───────────────────────────────────────────────────────────────
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "")

HEYGEN_API_KEY = os.environ.get("HEYGEN_API_KEY", "sk_V2_hgu_k8CMGqOlNxd_Oylyh76WThldZ6wU4wqVBcZXNFIPdxy2")
HG_BASE = "https://api.heygen.com"
HG_HDR  = {"X-Api-Key": HEYGEN_API_KEY, "Content-Type": "application/json"}

R2_ACCOUNT_ID    = os.environ.get("R2_ACCOUNT_ID",    "e1f899a3de5ea5e4ca0128015a2d08db")
R2_ACCESS_KEY_ID = os.environ.get("R2_ACCESS_KEY_ID", "f970d8278aca3561b1bea5a30275ad0e")
R2_SECRET_KEY    = os.environ.get("R2_SECRET_KEY",    "c17a671765be585940aa56622344ba3ddc88858b9ce26ab850341d7cf92bba25")
R2_BUCKET        = os.environ.get("R2_BUCKET",        "videoai-studio")
R2_PUBLIC_URL    = os.environ.get("R2_PUBLIC_URL",    "https://pub-2ede32ed555b4f0a927b507e0379a7bb.r2.dev")

FONT = os.environ.get(
    "FFMPEG_FONT",
    "C\\:/Windows/Fonts/arialbd.ttf" if os.name == "nt"
    else "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
)

# ── Avatar look config ────────────────────────────────────────────────────────
AVATARS = {
    "hoodie": {"look_id": "bfa7bb87865046a7a6ce47681f72540f", "crop_y": 658, "crop_h": 603},
    "gym":    {"look_id": "37488c8677cc44e4b8c34bbe8304850b", "crop_y": 658, "crop_h": 603},
    "suit":   {"look_id": "565bc6afc9e5449db5d696cf8d82c401", "crop_y": 658, "crop_h": 603},
}
BG_COLOR = "#0A0F1E"


# ── R2 ────────────────────────────────────────────────────────────────────────
def _s3():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_KEY,
        region_name="auto",
    )

def upload_r2(local_path: str, key: str, content_type: str = "video/mp4") -> str:
    _s3().upload_file(local_path, R2_BUCKET, key, ExtraArgs={"ContentType": content_type})
    return f"{R2_PUBLIC_URL}/{key}"


# ── ElevenLabs TTS ────────────────────────────────────────────────────────────
async def tts(script: str, voice_id: str = None) -> bytes:
    vid = voice_id or ELEVENLABS_VOICE_ID
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{vid}",
            headers={"xi-api-key": ELEVENLABS_API_KEY, "Content-Type": "application/json"},
            json={
                "text": script,
                "model_id": "eleven_turbo_v2_5",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
            },
        )
        if not r.is_success:
            raise RuntimeError(f"ElevenLabs {r.status_code}: {r.text[:200]}")
        return r.content  # mp3 bytes


# ── HeyGen ────────────────────────────────────────────────────────────────────
async def hg_generate(audio_r2_url: str, look_id: str) -> str:
    payload = {
        "video_inputs": [{
            "character": {"type": "avatar", "avatar_id": look_id, "avatar_style": "normal"},
            "voice":     {"type": "audio", "audio_url": audio_r2_url},
            "background": {"type": "color", "value": BG_COLOR},
        }],
        "dimension": {"width": 1080, "height": 1920},
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{HG_BASE}/v2/video/generate", headers=HG_HDR, json=payload)
        if not r.is_success:
            raise RuntimeError(f"HeyGen {r.status_code}: {r.text[:200]}")
        return r.json()["data"]["video_id"]


async def hg_poll(video_id: str, on_status=None) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        for i in range(120):
            await asyncio.sleep(10)
            r = await client.get(f"{HG_BASE}/v1/video_status.get",
                                 headers=HG_HDR, params={"video_id": video_id})
            if r.status_code != 200:
                continue
            data = r.json().get("data", {})
            status = data.get("status")
            if on_status:
                on_status(f"HeyGen: {status} ({i*10}s)")
            if status == "completed":
                return data["video_url"]
            if status == "failed":
                raise RuntimeError(f"HeyGen render failed: {data.get('error')}")
    raise RuntimeError("HeyGen timeout after 20 min")


async def hg_download(url: str, path: str):
    async with httpx.AsyncClient(timeout=300) as client:
        async with client.stream("GET", url, follow_redirects=True) as r:
            with open(path, "wb") as f:
                async for chunk in r.aiter_bytes(65536):
                    f.write(chunk)


# ── Captions ──────────────────────────────────────────────────────────────────
def _fmt_ass(s: float) -> str:
    h = int(s) // 3600
    m = int(s) // 60 % 60
    sec = int(s) % 60
    cs = int((s % 1) * 100)
    return f"{h}:{m:02}:{sec:02}.{cs:02}"


def make_captions(mp4_path: str, ass_path: str):
    if not _WHISPER_AVAILABLE:
        open(ass_path, "w").close()
        return
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(mp4_path, word_timestamps=True)
    words = [(w.start, w.end, w.word.strip()) for seg in segments for w in seg.words]
    chunks = [(words[i][0], words[i+3 if i+3 < len(words) else -1][1],
               " ".join(w[2] for w in words[i:i+4]))
              for i in range(0, len(words), 4)]
    ass = (
        "[Script Info]\nPlayResX: 1080\nPlayResY: 1920\nScriptType: v4.00+\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, Bold, BorderStyle, Outline, Shadow, Alignment, MarginV\n"
        "Style: Default,Arial,52,&H00FFFFFF,&H00000000,1,1,3,2,2,100\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    for start, end, text in chunks:
        ass += f"Dialogue: 0,{_fmt_ass(start)},{_fmt_ass(end)},Default,,0,0,0,,{text}\n"
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass)


# ── ffmpeg render ─────────────────────────────────────────────────────────────
def render_final(raw_mp4: str, ass_path: str, out_mp4: str,
                 title: str, subtitle: str, crop_y: int, crop_h: int):
    tmpdir = tempfile.mkdtemp(prefix="dawn_render_")
    try:
        tmp_pass1 = os.path.join(tmpdir, "pass1.mp4")
        tmp_ass   = os.path.join(tmpdir, os.path.basename(ass_path))
        shutil.copy2(ass_path, tmp_ass)
        ass_name  = os.path.basename(tmp_ass)

        te = lambda s: s.replace("'", "\\'").replace(":", "\\:")

        vf1 = (
            f"crop=1080:{crop_h}:0:{crop_y},"
            f"scale=iw*(1920/ih):1920,crop=1080:1920:(iw-1080)/2:0,"
            f"drawtext=fontfile='{FONT}':text='{te(title)}':fontcolor=white:fontsize=80:"
            f"x=(w-text_w)/2:y=70:shadowcolor=black@0.9:shadowx=4:shadowy=4,"
            f"drawtext=fontfile='{FONT}':text='{te(subtitle)}':fontcolor=white@0.85:fontsize=38:"
            f"x=(w-text_w)/2:y=170:shadowcolor=black@0.7:shadowx=2:shadowy=2"
        )
        r1 = subprocess.run(
            ["ffmpeg", "-y", "-i", raw_mp4, "-vf", vf1,
             "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-c:a", "copy", tmp_pass1],
            capture_output=True, text=True,
        )
        if r1.returncode != 0:
            raise RuntimeError(f"ffmpeg pass1 failed:\n{r1.stderr[-500:]}")

        r2 = subprocess.run(
            ["ffmpeg", "-y", "-i", tmp_pass1, "-vf", f"ass={ass_name}",
             "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-c:a", "copy", out_mp4],
            capture_output=True, text=True, cwd=tmpdir,
        )
        if r2.returncode != 0:
            raise RuntimeError(f"ffmpeg pass2 failed:\n{r2.stderr[-500:]}")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# ── Full pipeline ─────────────────────────────────────────────────────────────
async def run_pipeline(job_id: str, script: str, avatar: str,
                       title: str, subtitle: str, jobs: dict,
                       voice_id: str = None):
    def log(msg: str):
        jobs[job_id]["log"].append(msg)
        jobs[job_id]["status"] = msg

    tmpdir = tempfile.mkdtemp(prefix=f"dawn_{job_id}_")
    try:
        log("ElevenLabs: generating voice...")
        audio_bytes = await tts(script, voice_id=voice_id)
        audio_path  = os.path.join(tmpdir, "audio.mp3")
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)

        log("Uploading audio to R2...")
        audio_key = f"tmp_audio_{job_id}_{int(time.time())}.mp3"
        audio_url = upload_r2(audio_path, audio_key, "audio/mpeg")

        cfg = AVATARS.get(avatar, AVATARS["hoodie"])
        log("HeyGen: submitting avatar render...")
        vid_id = await hg_generate(audio_url, cfg["look_id"])
        jobs[job_id]["heygen_id"] = vid_id

        hg_url = await hg_poll(vid_id, on_status=log)

        raw_mp4 = os.path.join(tmpdir, "raw.mp4")
        log("Downloading raw video...")
        await hg_download(hg_url, raw_mp4)

        log("Transcribing for captions...")
        ass_path = os.path.join(tmpdir, "captions.ass")
        make_captions(raw_mp4, ass_path)

        log("Rendering final video (DAWN layout)...")
        final_mp4 = os.path.join(tmpdir, "final.mp4")
        render_final(raw_mp4, ass_path, final_mp4, title, subtitle,
                     cfg["crop_y"], cfg["crop_h"])

        log("Uploading final video to R2...")
        video_key = f"{job_id}_{int(time.time())}.mp4"
        video_url = upload_r2(final_mp4, video_key)

        jobs[job_id]["status"]    = "done"
        jobs[job_id]["video_url"] = video_url
        jobs[job_id]["video_key"] = video_key

    except Exception as e:
        jobs[job_id]["status"] = f"error: {e}"
        jobs[job_id]["error"]  = str(e)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
