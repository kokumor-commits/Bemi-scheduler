"""
Scheduler runner — checks master_schedule.json for due posts and fires them.
Run every 15 min via GitHub Actions cron (or manually).
Posts within ±20 min of scheduled time are fired.
"""
import json, sys
from datetime import datetime, timezone
from pathlib import Path

from post import post_facebook, post_instagram, post_youtube, post_tiktok, post_threads

SCHEDULE_FILE = Path(__file__).parent / "master_schedule.json"
WINDOW_SEC = 20 * 60  # fire if within ±20 min of scheduled time


def is_due(scheduled_utc: str) -> bool:
    sched = datetime.fromisoformat(scheduled_utc.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    diff = abs((sched - now).total_seconds())
    return diff <= WINDOW_SEC


def fire_post(post: dict) -> dict:
    url      = post["video_url"]
    caption  = post["caption"]
    yt_title = post.get("yt_title", caption[:100])
    results  = {}

    for platform in post.get("platforms", []):
        try:
            if platform == "facebook":
                results["facebook"] = post_facebook(url, caption)
            elif platform == "instagram":
                results["instagram"] = post_instagram(url, caption)
            elif platform == "youtube":
                results["youtube"] = post_youtube(url, yt_title, caption)
            elif platform == "tiktok":
                results["tiktok"] = post_tiktok(url, caption, yt_title)
            elif platform == "threads":
                results["threads"] = post_threads(url, caption)
            print(f"  ✓ {platform}", flush=True)
        except Exception as e:
            print(f"  ✗ {platform}: {e}", flush=True)
            results[platform] = {"error": str(e)}

    return results


def run():
    data    = json.loads(SCHEDULE_FILE.read_text(encoding="utf-8"))
    posts   = data["posts"]
    fired   = 0
    changed = False

    for post in posts:
        if post.get("done"):
            continue
        if not is_due(post["scheduled_utc"]):
            continue

        print(f"\n▶ FIRING {post['id']} @ {post['scheduled_utc']}", flush=True)
        results = fire_post(post)
        successes = [p for p, r in results.items() if "error" not in r]
        failures  = [p for p, r in results.items() if "error" in r]
        post["results"] = results  # always store — lets us read errors from JSON next git pull
        changed = True
        if successes:
            post["done"] = True
            fired += 1
            print(f"  Posted to: {', '.join(successes)}", flush=True)
        else:
            print(f"  ALL PLATFORMS FAILED — not marking done, will retry next window", flush=True)
        if failures:
            print(f"  Failed: {', '.join(failures)}", flush=True)

    if changed:
        SCHEDULE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    if fired:
        print(f"\n{fired} post(s) fired. Schedule updated.", flush=True)
    else:
        print("No posts due.", flush=True)


if __name__ == "__main__":
    run()
