"""
Persistent Railway worker — replaces GitHub Actions cron.
Reads/writes schedule via GitHub API. Fires posts every 15 min, guaranteed.
"""
import os, sys, json, base64, time, logging
from datetime import datetime, timezone
from pathlib import Path

import httpx

# import platform posting functions from sibling video_scheduler/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "video_scheduler"))
from post import post_facebook, post_facebook_comment, post_instagram, post_youtube, post_tiktok, post_threads

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
)
log = logging.getLogger(__name__)

# ── config ─────────────────────────────────────────────────────────────────────
GITHUB_TOKEN   = os.environ["GITHUB_TOKEN"]
SCHEDULE_REPO  = os.environ.get("SCHEDULE_REPO", "kokumor-commits/Bemi-scheduler")
SCHEDULE_PATH  = "MYFIRSTAGENT/video_scheduler/master_schedule.json"
INTERVAL_SEC   = 15 * 60
WINDOW_SEC     = 20 * 60
RETRY_COOLDOWN = 60 * 60  # min gap between retries per post


# ── GitHub API ─────────────────────────────────────────────────────────────────
def _gh():
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }


def read_schedule():
    r = httpx.get(
        f"https://api.github.com/repos/{SCHEDULE_REPO}/contents/{SCHEDULE_PATH}",
        headers=_gh(), timeout=30,
    )
    r.raise_for_status()
    meta = r.json()
    content = base64.b64decode(meta["content"]).decode("utf-8")
    return json.loads(content), meta["sha"]


def write_schedule(data: dict, sha: str) -> bool:
    encoded = base64.b64encode(
        json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
    ).decode()
    r = httpx.put(
        f"https://api.github.com/repos/{SCHEDULE_REPO}/contents/{SCHEDULE_PATH}",
        headers=_gh(),
        json={
            "message": "chore: mark posted items done [skip ci]",
            "content": encoded,
            "sha": sha,
            "committer": {"name": "Scheduler Bot", "email": "scheduler-bot@noreply"},
        },
        timeout=30,
    )
    if r.status_code == 409:
        log.warning("SHA conflict — schedule changed externally, will re-read next tick")
        return False
    r.raise_for_status()
    return True


# ── scheduling logic ───────────────────────────────────────────────────────────
def is_due(scheduled_utc: str) -> bool:
    sched = datetime.fromisoformat(scheduled_utc.replace("Z", "+00:00"))
    diff = abs((sched - datetime.now(timezone.utc)).total_seconds())
    return diff <= WINDOW_SEC


def needs_retry(post: dict) -> list:
    """Platforms to retry, respecting cooldown so we don't hammer APIs."""
    last = post.get("last_retry_at")
    if last:
        elapsed = (
            datetime.now(timezone.utc)
            - datetime.fromisoformat(last.replace("Z", "+00:00"))
        ).total_seconds()
        if elapsed < RETRY_COOLDOWN:
            return []

    if post.get("done"):
        return post.get("retry_platforms", [])

    results = post.get("results", {})
    if not results:
        return []
    if all("error" in r for r in results.values()):
        return post.get("platforms", [])
    return []


def fire_platforms(post: dict, platforms: list) -> dict:
    url, caption = post["video_url"], post["caption"]
    yt_title = post.get("yt_title", caption[:100])
    thumb = post.get("thumbnail_url", "")
    results = {}
    for platform in platforms:
        try:
            if platform == "facebook":
                results["facebook"] = post_facebook(url, caption, thumbnail_url=thumb)
                affiliate_comment = post.get("affiliate_comment")
                if affiliate_comment and "id" in results["facebook"]:
                    try:
                        post_facebook_comment(results["facebook"]["id"], affiliate_comment)
                        log.info(f"  ✓ facebook affiliate comment")
                    except Exception as ce:
                        log.error(f"  ✗ facebook affiliate comment: {ce}")
            elif platform == "instagram":
                results["instagram"] = post_instagram(url, caption, thumbnail_url=thumb)
            elif platform == "youtube":
                results["youtube"] = post_youtube(url, yt_title, caption, thumbnail_url=thumb)
            elif platform == "tiktok":
                results["tiktok"] = post_tiktok(url, caption, yt_title)
            elif platform == "threads":
                results["threads"] = post_threads(url, caption)
            log.info(f"  ✓ {platform}")
        except Exception as e:
            log.error(f"  ✗ {platform}: {e}")
            results[platform] = {"error": str(e)}
    return results


# ── main tick ──────────────────────────────────────────────────────────────────
def tick():
    log.info("── tick ──────────────────────────────────────────────")
    try:
        data, sha = read_schedule()
    except Exception as e:
        log.error(f"Read schedule failed: {e}")
        return

    posts = data["posts"]
    changed = False
    fired = 0

    for post in posts:
        retry_platforms = needs_retry(post)
        due = is_due(post["scheduled_utc"])

        if post.get("done") and not retry_platforms:
            continue
        if not post.get("done") and not due and not retry_platforms:
            continue

        platforms_to_fire = retry_platforms if retry_platforms else post.get("platforms", [])

        if retry_platforms and post.get("done"):
            log.info(f"↻ RETRY pending {retry_platforms} → {post['id']}")
        elif retry_platforms and not due:
            log.info(f"↻ RETRY (prev all-failed) {post['id']}")
        else:
            log.info(f"▶ FIRING {post['id']} @ {post['scheduled_utc']}")

        results = fire_platforms(post, platforms_to_fire)
        successes = [p for p, r in results.items() if "error" not in r]
        failures  = [p for p, r in results.items() if "error" in r]

        # merge results — preserve successes from prior runs
        existing = post.get("results", {})
        existing.update(results)
        post["results"] = existing
        post["last_retry_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        changed = True

        if successes:
            fired += 1
            log.info(f"  Posted to: {', '.join(successes)}")
        if failures:
            log.info(f"  Failed: {', '.join(failures)}")

        # recompute done + retry_platforms
        all_plats = post.get("platforms", [])
        curr = post["results"]
        succeeded_ever = [p for p in all_plats if p in curr and "error" not in curr[p]]
        still_failing  = [p for p in all_plats if p not in curr or "error" in curr[p]]
        # skip placeholder-token platforms from retry
        still_failing  = [
            p for p in still_failing
            if "not configured" not in str(curr.get(p, {}).get("error", ""))
        ]

        post["done"] = len(succeeded_ever) > 0
        post["retry_platforms"] = still_failing if succeeded_ever and still_failing else []
        if not still_failing:
            post.pop("retry_platforms", None)

    if changed:
        ok = write_schedule(data, sha)
        if ok:
            log.info(f"{fired} post(s) fired — schedule updated on GitHub.")
        else:
            log.warning("GitHub write failed — results not saved this tick, will retry next.")
    else:
        log.info("No posts due.")


def main():
    log.info("═══ Bemi Scheduler (Railway) starting ═══")
    log.info(f"Repo: {SCHEDULE_REPO} | Interval: {INTERVAL_SEC//60}min")
    while True:
        try:
            tick()
        except Exception as e:
            log.error(f"Unhandled tick error: {e}", exc_info=True)
        log.info(f"Sleeping {INTERVAL_SEC // 60} min…")
        time.sleep(INTERVAL_SEC)


if __name__ == "__main__":
    main()
