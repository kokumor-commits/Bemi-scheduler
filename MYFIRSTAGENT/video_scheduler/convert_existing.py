"""
Converts existing campaign JSON files (comeback_urls.json, onequestion_urls.json, etc.)
into master_schedule.json format used by the custom scheduler.
Run once to migrate. Edit CAMPAIGNS list to add new ones.
"""
import json
from pathlib import Path

BASE = Path(__file__).parent.parent
OUT  = Path(__file__).parent / "master_schedule.json"

PLATFORMS = ["facebook", "instagram", "youtube", "tiktok", "threads"]

# ── Define campaigns: (json_file, schedule_list) ─────────────────────────────
# schedule_list = [(key, "2026-MM-DDTHH:MM:SSZ"), ...]

CAMPAIGNS = [
    # One Question — 7:45 PM CST = 01:45 UTC next day
    (
        "onequestion_urls.json",
        [
            ("Reel01_WhoAreYouBecoming",        "2026-07-23T01:45:00Z"),
            ("Reel02_WhatAreYouTolerating",      "2026-07-24T01:45:00Z"),
            ("Reel03_IfFearDisappeared",         "2026-07-25T01:45:00Z"),
            ("Reel04_BusyOrProductive",          "2026-07-26T01:45:00Z"),
            ("Reel05_WhoBenefitsFromSelfDoubt",  "2026-07-27T01:45:00Z"),
            ("Reel06_WhatStoryAreYouRepeating",  "2026-07-28T01:45:00Z"),
            ("Reel07_WhatWouldFutureSelfSay",    "2026-07-29T01:45:00Z"),
            ("Reel08_WhatAreYouAvoiding",        "2026-07-30T01:45:00Z"),
            ("Reel09_WhatTrulyMatters",          "2026-07-31T01:45:00Z"),
            ("Reel10_WhatCanYouControl",         "2026-08-01T01:45:00Z"),
            ("Reel11_HabitsAndDreams",           "2026-08-02T01:45:00Z"),
            ("Reel12_WhoInspiresYou",            "2026-08-03T01:45:00Z"),
            ("Reel13_WhatWouldYouDoAgain",       "2026-08-04T01:45:00Z"),
            ("Reel14_WhatAreYouFeeding",         "2026-08-05T01:45:00Z"),
            ("Reel15_LivingIntentionally",       "2026-08-06T01:45:00Z"),
            ("Reel16_WhatWouldYouTellAFriend",   "2026-08-07T01:45:00Z"),
            ("Reel17_WhatAreYouGratefulFor",     "2026-08-08T01:45:00Z"),
            ("Reel18_GrowingOrAging",            "2026-08-09T01:45:00Z"),
            ("Reel19_WhatDoesSuccessMean",       "2026-08-10T01:45:00Z"),
            ("Reel20_WhatWillYouThankYourselfFor","2026-08-11T01:45:00Z"),
        ],
    ),
]

# ── Already-scheduled-in-Blotato (mark done=True to skip) ────────────────────
ALREADY_SCHEDULED_IN_BLOTATO = {
    # Comeback 1-20: all scheduled in Blotato
    "comeback_reel01", "comeback_reel02", "comeback_reel03", "comeback_reel04",
    "comeback_reel05", "comeback_reel06", "comeback_reel07", "comeback_reel08",
    "comeback_reel09", "comeback_reel10", "comeback_reel11", "comeback_reel12",
    "comeback_reel13", "comeback_reel14", "comeback_reel15", "comeback_reel16",
    "comeback_reel17", "comeback_reel18", "comeback_reel19", "comeback_reel20",
    # One Question 1-10: scheduled in Blotato
    "onequestion_reel01", "onequestion_reel02", "onequestion_reel03",
    "onequestion_reel04", "onequestion_reel05", "onequestion_reel06",
    "onequestion_reel07", "onequestion_reel08", "onequestion_reel09",
    "onequestion_reel10",
    # It Wasn't Love 2-12: scheduled in Blotato
    "itwasntlove_reel02", "itwasntlove_reel03", "itwasntlove_reel04",
    "itwasntlove_reel05", "itwasntlove_reel06", "itwasntlove_reel07",
    "itwasntlove_reel08", "itwasntlove_reel09", "itwasntlove_reel10",
    "itwasntlove_reel11", "itwasntlove_reel12",
}


def convert():
    posts = []

    for json_file, schedule in CAMPAIGNS:
        source = BASE / json_file
        if not source.exists():
            print(f"SKIP (not found): {json_file}")
            continue

        data = json.loads(source.read_text(encoding="utf-8"))
        campaign = json_file.replace("_urls.json", "").replace("_", "")

        for key, sched_time in schedule:
            if key not in data:
                print(f"  SKIP {key} — not in {json_file} yet")
                continue

            entry   = data[key]
            post_id = f"{campaign}_{key.lower()}"
            done    = post_id in ALREADY_SCHEDULED_IN_BLOTATO

            posts.append({
                "id":            post_id,
                "campaign":      campaign,
                "video_url":     entry["url"],
                "caption":       entry["caption"],
                "yt_title":      entry.get("yt_title", key),
                "scheduled_utc": sched_time,
                "platforms":     PLATFORMS,
                "done":          done,
            })

    out = {"posts": posts}
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    total   = len(posts)
    pending = sum(1 for p in posts if not p["done"])
    print(f"master_schedule.json written: {total} posts, {pending} pending")


if __name__ == "__main__":
    convert()
