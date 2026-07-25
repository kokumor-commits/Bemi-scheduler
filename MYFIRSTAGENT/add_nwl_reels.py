"""
After gen_notwasntlove_p2.py completes, run this to add reel13-20 to master_schedule.json.
Slot 3: 22:00 UTC (5 PM CDT), starting Aug 4 through Aug 11.
"""
import json
from datetime import datetime, timedelta, timezone

SCHEDULE_PATH = r"c:\Users\orits\OneDrive\Apps\Documents\01_WORK\IT-Training-Materials\bemi files\MYFIRSTAGENT\video_scheduler\master_schedule.json"
URLS_PATH = r"c:\Users\orits\OneDrive\Apps\Documents\01_WORK\IT-Training-Materials\bemi files\MYFIRSTAGENT\notwasntlove_urls.json"

PLATFORMS = ["facebook", "instagram", "youtube", "tiktok", "threads"]

NEW_KEYS = [
    ("Reel13_ForgiveYourself",   "notwasntlove_reel13_forgiveyourself"),
    ("Reel14_LovingWrong",       "notwasntlove_reel14_lovingwrong"),
    ("Reel15_TooMuch",           "notwasntlove_reel15_toomuch"),
    ("Reel16_BeforeLovingAgain", "notwasntlove_reel16_beforelovingagain"),
    ("Reel17_EmotionalMaturity", "notwasntlove_reel17_emotionalmaturity"),
    ("Reel18_BreakingPatterns",  "notwasntlove_reel18_breakingpatterns"),
    ("Reel19_NotYourJob",        "notwasntlove_reel19_notyourjob"),
    ("Reel20_WhatComesNext",     "notwasntlove_reel20_whatcomesnext"),
]

with open(URLS_PATH, encoding="utf-8") as f:
    urls = json.load(f)

with open(SCHEDULE_PATH, encoding="utf-8") as f:
    data = json.load(f)

posts = data["posts"]
existing_ids = {p["id"] for p in posts}

base_date = datetime(2026, 8, 4, 22, 0, 0, tzinfo=timezone.utc)
added = 0

for i, (url_key, post_id) in enumerate(NEW_KEYS):
    if post_id in existing_ids:
        print(f"SKIP {post_id} (already in schedule)")
        continue
    if url_key not in urls or not urls[url_key].get("url"):
        print(f"MISSING {url_key} in notwasntlove_urls.json — run gen_notwasntlove_p2.py first")
        continue
    entry = urls[url_key]
    scheduled_utc = (base_date + timedelta(days=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
    new_post = {
        "id": post_id,
        "campaign": "notwasntlove",
        "video_url": entry["url"],
        "caption": entry["caption"],
        "yt_title": entry["yt_title"],
        "scheduled_utc": scheduled_utc,
        "platforms": PLATFORMS,
        "done": False,
    }
    # Insert after notwasntlove_reel12
    insert_after = "notwasntlove_reel12_stopsettling"
    if added == 0:
        for j, p in enumerate(posts):
            if p["id"] == insert_after:
                posts.insert(j + 1, new_post)
                break
    else:
        # insert after the last nwl reel we just added
        last_id = NEW_KEYS[i-1][1]
        for j, p in enumerate(posts):
            if p["id"] == last_id:
                posts.insert(j + 1, new_post)
                break
    print(f"ADD {post_id}: {scheduled_utc}")
    added += 1

with open(SCHEDULE_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\nAdded {added} new It Wasn't Love reels (Aug 4-11 @ 22:00 UTC).")
