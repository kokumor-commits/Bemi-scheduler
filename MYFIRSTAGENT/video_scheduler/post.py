"""
Direct platform posting — no Blotato, no post limits.
Platforms: Facebook, Instagram, YouTube, TikTok, Threads
All env vars loaded from GitHub Secrets (or local .env).
"""
import os, time, httpx
from typing import Optional

# ── Meta: Facebook, Instagram, Threads ───────────────────────────────────────
META_TOKEN   = os.environ["META_PAGE_TOKEN"]
FB_PAGE_ID   = os.environ["FB_PAGE_ID"]
IG_ACCT_ID   = os.environ["IG_ACCOUNT_ID"]
TH_USER_ID   = os.environ["THREADS_USER_ID"]
THREADS_TOKEN = os.environ.get("THREADS_TOKEN", os.environ.get("META_PAGE_TOKEN", ""))

# ── YouTube ───────────────────────────────────────────────────────────────────
YT_CLIENT_ID     = os.environ["YT_CLIENT_ID"]
YT_CLIENT_SECRET = os.environ["YT_CLIENT_SECRET"]
YT_REFRESH_TOKEN = os.environ["YT_REFRESH_TOKEN"]

# ── TikTok ───────────────────────────────────────────────────────────────────
TK_ACCESS_TOKEN  = os.environ["TIKTOK_ACCESS_TOKEN"]
TK_REFRESH_TOKEN = os.environ.get("TIKTOK_REFRESH_TOKEN", "")
TK_CLIENT_KEY    = os.environ.get("TIKTOK_CLIENT_KEY", "")
TK_CLIENT_SECRET = os.environ.get("TIKTOK_CLIENT_SECRET", "")

GRAPH = "https://graph.facebook.com/v19.0"


# ── Facebook ──────────────────────────────────────────────────────────────────
def post_facebook(video_url: str, caption: str) -> dict:
    r = httpx.post(
        f"{GRAPH}/{FB_PAGE_ID}/videos",
        data={"file_url": video_url, "description": caption, "access_token": META_TOKEN},
        timeout=180,
    )
    r.raise_for_status()
    return r.json()


# ── Instagram Reels ───────────────────────────────────────────────────────────
def post_instagram(video_url: str, caption: str) -> dict:
    # Step 1: create container
    r = httpx.post(
        f"{GRAPH}/{IG_ACCT_ID}/media",
        data={
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": META_TOKEN,
        },
        timeout=180,
    )
    r.raise_for_status()
    creation_id = r.json()["id"]

    # Step 2: poll until FINISHED (max 5 min)
    for _ in range(30):
        s = httpx.get(
            f"{GRAPH}/{creation_id}",
            params={"fields": "status_code", "access_token": META_TOKEN},
            timeout=30,
        ).json()
        if s.get("status_code") == "FINISHED":
            break
        time.sleep(10)

    # Step 3: publish
    pub = httpx.post(
        f"{GRAPH}/{IG_ACCT_ID}/media_publish",
        data={"creation_id": creation_id, "access_token": META_TOKEN},
        timeout=60,
    )
    pub.raise_for_status()
    return pub.json()


# ── Threads ───────────────────────────────────────────────────────────────────
def post_threads(video_url: str, caption: str) -> dict:
    base = "https://graph.threads.net/v1.0"
    caption = caption[:500]

    r = httpx.post(
        f"{base}/{TH_USER_ID}/threads",
        data={
            "media_type": "VIDEO",
            "video_url": video_url,
            "text": caption,
            "access_token": THREADS_TOKEN,
        },
        timeout=180,
    )
    r.raise_for_status()
    creation_id = r.json()["id"]

    # wait for processing
    time.sleep(30)

    pub = httpx.post(
        f"{base}/{TH_USER_ID}/threads_publish",
        data={"creation_id": creation_id, "access_token": THREADS_TOKEN},
        timeout=60,
    )
    pub.raise_for_status()
    return pub.json()


# ── YouTube Shorts ────────────────────────────────────────────────────────────
def _yt_token() -> str:
    r = httpx.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": YT_CLIENT_ID,
            "client_secret": YT_CLIENT_SECRET,
            "refresh_token": YT_REFRESH_TOKEN,
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def post_youtube(video_url: str, title: str, description: str = "") -> dict:
    access_token = _yt_token()

    # Download video from R2 (videos are ~5-10 MB at 30s)
    print(f"  Downloading video from R2...", flush=True)
    vid = httpx.get(video_url, timeout=300, follow_redirects=True)
    vid.raise_for_status()
    video_bytes = vid.content
    print(f"  Downloaded {len(video_bytes)//1024}KB", flush=True)

    # Initiate resumable upload
    init = httpx.post(
        "https://www.googleapis.com/upload/youtube/v3/videos"
        "?uploadType=resumable&part=snippet,status",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Upload-Content-Type": "video/mp4",
            "X-Upload-Content-Length": str(len(video_bytes)),
        },
        json={
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": ["#Shorts"],
                "categoryId": "22",
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
            },
        },
        timeout=60,
    )
    init.raise_for_status()
    upload_url = init.headers["Location"]

    # Upload bytes
    up = httpx.put(
        upload_url,
        headers={"Content-Type": "video/mp4", "Content-Length": str(len(video_bytes))},
        content=video_bytes,
        timeout=600,
    )
    up.raise_for_status()
    return up.json()


# ── TikTok ────────────────────────────────────────────────────────────────────
def _tk_token() -> str:
    if not TK_REFRESH_TOKEN or not TK_CLIENT_KEY:
        return TK_ACCESS_TOKEN
    r = httpx.post(
        "https://open.tiktokapis.com/v2/oauth/token/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": TK_CLIENT_KEY,
            "client_secret": TK_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": TK_REFRESH_TOKEN,
        },
        timeout=30,
    )
    if r.status_code == 200:
        return r.json()["data"]["access_token"]
    return TK_ACCESS_TOKEN


def post_tiktok(video_url: str, caption: str, title: Optional[str] = None) -> dict:
    token = _tk_token()
    r = httpx.post(
        "https://open.tiktokapis.com/v2/post/publish/video/init/",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "post_info": {
                "title": (title or caption)[:150],
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_duet": False,
                "disable_stitch": False,
                "disable_comment": False,
                "brand_content_toggle": False,
                "brand_organic_toggle": False,
                "is_ai_generated": True,
            },
            "source_info": {"source": "PULL_FROM_URL", "video_url": video_url},
        },
        timeout=180,
    )
    r.raise_for_status()
    return r.json()
