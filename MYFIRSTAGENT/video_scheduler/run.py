"""
Scheduler runner — checks master_schedule.json for due posts and fires them.
Run every 15 min via GitHub Actions cron (or manually).
Posts within ±20 min of scheduled time are fired.
Partial-success posts (e.g. YouTube OK, FB fail) track retry_platforms for re-fire.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

from post import post_facebook, post_instagram, post_youtube, post_tiktok, post_threads

SCHEDULE_FILE = Path(__file__).parent / "master_schedule.json"
WINDOW_SEC    = 20 * 60   # fire if within ±20 min of scheduled time
RETRY_COOLDOWN = 60 * 60  # retry failed platforms at most once per hour


def is_due(scheduled_utc: str) -> bool:
    sched = datetime.fromisoformat(scheduled_utc.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    diff = abs((sched - now).total_seconds())
    return diff <= WINDOW_SEC


def needs_retry(post: dict) -> list:
    """Return platforms to retry, respecting hourly cooldown to avoid hammering APIs."""
    now = datetime.now(timezone.utc)

    # cooldown check — don't retry more than once per hour
    last_retry = post.get("last_retry_at")
    if last_retry:
        elapsed = (now - datetime.fromisoformat(last_retry.replace("Z", "+00:00"))).total_seconds()
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
    url      = post["video_url"]
    caption  = post["caption"]
    yt_title = post.get("yt_title", caption[:100])
    results  = {}

    for platform in platforms:
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
        retry_platforms = needs_retry(post)
        due = is_due(post["scheduled_utc"])

        if post.get("done") and not retry_platforms:
            continue
        if not post.get("done") and not due and not retry_platforms:
            continue

        platforms_to_fire = retry_platforms if retry_platforms else post.get("platforms", [])

        if retry_platforms and post.get("done"):
            print(f"\n↻ RETRY pending platforms {retry_platforms} for {post['id']}", flush=True)
        elif retry_platforms and not due:
            print(f"\n↻ RETRY (prev all-failed) {post['id']}", flush=True)
        else:
            print(f"\n▶ FIRING {post['id']} @ {post['scheduled_utc']}", flush=True)

        results = fire_platforms(post, platforms_to_fire)
        successes = [p for p, r in results.items() if "error" not in r]
        failures  = [p for p, r in results.items() if "error" in r]

        # merge into existing results (preserve results from prior runs)
        existing = post.get("results", {})
        existing.update(results)
        post["results"] = existing
        post["last_retry_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        changed = True

        if successes:
            fired += 1
            print(f"  Posted to: {', '.join(successes)}", flush=True)

        if failures:
            print(f"  Failed: {', '.join(failures)}", flush=True)

        # update done + retry_platforms
        all_platforms = post.get("platforms", [])
        current_results = post["results"]
        succeeded_ever = [p for p in all_platforms if p in current_results and "error" not in current_results[p]]
        still_failing  = [p for p in all_platforms if p not in current_results or "error" in current_results[p]]
        # exclude "skipped" platforms (placeholder tokens) from retry
        still_failing  = [p for p in still_failing if "not configured" not in str(current_results.get(p, {}).get("error", ""))]

        post["done"] = len(succeeded_ever) > 0
        post["retry_platforms"] = still_failing if succeeded_ever and still_failing else []

        if not succeeded_ever:
            print(f"  ALL PLATFORMS FAILED — will retry every run until token fixed", flush=True)
        elif still_failing:
            print(f"  Partial: {', '.join(still_failing)} still pending — will retry", flush=True)
        else:
            post.pop("retry_platforms", None)  # clean up when all done

    if changed:
        SCHEDULE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    if fired:
        print(f"\n{fired} post(s) fired. Schedule updated.", flush=True)
    else:
        print("No posts due.", flush=True)


if __name__ == "__main__":
    run()
