"""
Direct platform posting — no Blotato, no post limits.
Platforms: Facebook, Instagram, YouTube, TikTok, Threads
All env vars loaded from GitHub Secrets (or local .env).
"""
import os, time, httpx
from typing import Optional

# Env vars can pick up a trailing newline/whitespace depending on how they were
# pasted into Railway/GitHub Secrets -- harmless in form-data params, but an
# HTTP header value with a newline gets rejected outright ("Illegal header
# value"). Strip every token at load time so this can't silently break a
# header-based call again (bit us on the FB Reels transfer phase, 2026-08-23).
_env = lambda k, d="": os.environ.get(k, d).strip()

# ── Meta: Facebook, Instagram, Threads ───────────────────────────────────────
META_TOKEN    = _env("META_PAGE_TOKEN")
FB_PAGE_ID    = _env("FB_PAGE_ID")
IG_ACCT_ID    = _env("IG_ACCOUNT_ID")
TH_USER_ID    = _env("THREADS_USER_ID")
THREADS_TOKEN = _env("THREADS_TOKEN", META_TOKEN) or META_TOKEN

# ── YouTube ───────────────────────────────────────────────────────────────────
YT_CLIENT_ID     = _env("YT_CLIENT_ID")
YT_CLIENT_SECRET = _env("YT_CLIENT_SECRET")
YT_REFRESH_TOKEN = _env("YT_REFRESH_TOKEN")

# ── TikTok ───────────────────────────────────────────────────────────────────
TK_ACCESS_TOKEN  = _env("TIKTOK_ACCESS_TOKEN")
TK_REFRESH_TOKEN = _env("TIKTOK_REFRESH_TOKEN")
TK_CLIENT_KEY    = _env("TIKTOK_CLIENT_KEY")
TK_CLIENT_SECRET = _env("TIKTOK_CLIENT_SECRET")


def _is_placeholder(val: str) -> bool:
    return not val or val.strip().lower() == "placeholder"

GRAPH = "https://graph.facebook.com/v19.0"


# ── Facebook ──────────────────────────────────────────────────────────────────
def post_facebook(video_url: str, caption: str, thumbnail_url: str = "") -> dict:
    """Publish via the Reels Publishing API (video_reels), not the plain /videos
    upload. Meta has shifted organic distribution heavily toward Reels since
    2023 -- a plain Page video post gets a fraction of the reach a Reel does,
    even at identical 9:16 spec. See project_amazon_affiliate-adjacent audit,
    2026-08-22: this was the primary reach-suppression fix alongside removing
    outbound links from captions."""
    # Phase 1: start
    start = httpx.post(
        f"{GRAPH}/{FB_PAGE_ID}/video_reels",
        data={"upload_phase": "start", "access_token": META_TOKEN},
        timeout=30,
    )
    if not start.is_success:
        raise Exception(f"FB reels start {start.status_code}: {start.text[:500]}")
    start_data = start.json()
    video_id = start_data["video_id"]
    upload_url = start_data.get("upload_url") or f"https://rupload.facebook.com/video-upload/v19.0/{video_id}"

    # Phase 2: transfer -- pass file_url directly, Facebook pulls from R2 itself
    print(f"  FB: transferring video (video_id={video_id})...", flush=True)
    transfer = httpx.post(
        upload_url,
        headers={"Authorization": f"OAuth {META_TOKEN}"},
        data={"file_url": video_url},
        timeout=180,
    )
    if not transfer.is_success:
        body = transfer.text[:500]
        print(f"  FB transfer error body: {body}", flush=True)
        raise Exception(f"FB reels transfer {transfer.status_code}: {body}")

    # Phase 3: finish/publish
    finish = httpx.post(
        f"{GRAPH}/{FB_PAGE_ID}/video_reels",
        data={
            "upload_phase": "finish",
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": caption,
            "access_token": META_TOKEN,
        },
        timeout=60,
    )
    if not finish.is_success:
        body = finish.text[:500]
        print(f"  FB finish error body: {body}", flush=True)
        raise Exception(f"FB reels finish {finish.status_code}: {body}")

    if thumbnail_url:
        try:
            post_facebook_thumbnail(video_id, thumbnail_url)
        except Exception as e:
            print(f"  FB thumbnail set failed (non-fatal): {e}", flush=True)

    return {"id": video_id, **finish.json()}


def post_facebook_thumbnail(video_id: str, thumbnail_url: str) -> dict:
    """Upload a custom thumbnail and mark it preferred. FB's thumbnails
    endpoint wants the image bytes, not a URL, so fetch then upload."""
    img = httpx.get(thumbnail_url, timeout=30, follow_redirects=True)
    img.raise_for_status()
    r = httpx.post(
        f"{GRAPH}/{video_id}/thumbnails",
        data={"is_preferred": "true", "access_token": META_TOKEN},
        files={"source": ("thumb.jpg", img.content, "image/jpeg")},
        timeout=30,
    )
    if not r.is_success:
        raise Exception(f"FB thumbnail {r.status_code}: {r.text[:500]}")
    return r.json()


def post_facebook_comment(video_post_id: str, message: str) -> dict:
    """Post a comment on an existing FB video post -- used for Amazon affiliate
    links, which per Associates Program rules should not be the primary caption
    and always need the 'As an Amazon Associate I earn from qualifying
    purchases' disclosure attached."""
    r = httpx.post(
        f"{GRAPH}/{video_post_id}/comments",
        data={"message": message, "access_token": META_TOKEN},
        timeout=30,
    )
    if not r.is_success:
        raise Exception(f"FB comment {r.status_code}: {r.text[:500]}")
    return r.json()


# ── Instagram Reels ───────────────────────────────────────────────────────────
def post_instagram(video_url: str, caption: str, thumbnail_url: str = "") -> dict:
    # Step 1: create container
    data = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": META_TOKEN,
    }
    if thumbnail_url:
        data["cover_url"] = thumbnail_url  # takes precedence over auto-picked frame
    r = httpx.post(
        f"{GRAPH}/{IG_ACCT_ID}/media",
        data=data,
        timeout=180,
    )
    if not r.is_success:
        body = r.text[:500]
        print(f"  IG container error: {body}", flush=True)
        raise Exception(f"IG {r.status_code}: {body}")
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
    if _is_placeholder(THREADS_TOKEN) or _is_placeholder(TH_USER_ID):
        raise RuntimeError("THREADS_TOKEN/THREADS_USER_ID not configured — skipping")
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


def _yt_tags(title: str, description: str) -> list[str]:
    """Real keyword tags for search/suggested discovery, not just '#Shorts'."""
    import re
    text = f"{title} {description}".lower()
    words = re.findall(r"[a-z']{4,}", text)
    stop = {"this", "that", "with", "your", "have", "will", "from", "they",
            "them", "what", "when", "there", "their", "about", "which", "shorts"}
    seen, tags = set(), []
    for w in words:
        if w in stop or w in seen:
            continue
        seen.add(w)
        tags.append(w)
        if len(tags) >= 12:
            break
    return ["#Shorts"] + tags


def post_youtube(video_url: str, title: str, description: str = "", thumbnail_url: str = "") -> dict:
    access_token = _yt_token()

    # #Shorts must appear in the title or description text itself (not just
    # metadata tags) to reliably trigger Shorts shelf/algorithm treatment.
    if "#shorts" not in description.lower() and "#shorts" not in title.lower():
        description = f"{description}\n\n#Shorts" if description else "#Shorts"

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
                "tags": _yt_tags(title, description),
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
    result = up.json()

    if thumbnail_url and result.get("id"):
        try:
            post_youtube_thumbnail(result["id"], access_token, thumbnail_url)
        except Exception as e:
            print(f"  YT thumbnail set failed (non-fatal, needs phone-verified channel): {e}", flush=True)

    return result


def post_youtube_thumbnail(video_id: str, access_token: str, thumbnail_url: str) -> dict:
    img = httpx.get(thumbnail_url, timeout=30, follow_redirects=True)
    img.raise_for_status()
    r = httpx.post(
        f"https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId={video_id}",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "image/jpeg"},
        content=img.content,
        timeout=60,
    )
    r.raise_for_status()
    return r.json()


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
    if _is_placeholder(TK_ACCESS_TOKEN):
        raise RuntimeError("TIKTOK_ACCESS_TOKEN not configured — skipping")
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
