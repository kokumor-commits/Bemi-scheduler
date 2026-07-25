"""
Reschedule three series at new slots:
  Slot 1 (11:45 UTC = 6:45 AM CDT): One Question reel13-20, Jul 25 - Aug 1
  Slot 2 (17:45 UTC = 12:45 PM CDT): Comeback reel01-20, Jul 25 - Aug 13
  Slot 3 (22:00 UTC = 5:00 PM CDT): It Wasn't Love reel03-12, Jul 25 - Aug 3
                                     (reel13-20 added separately after DAWN generates them)
"""
import json
from datetime import datetime, timedelta, timezone

SCHEDULE_PATH = r"c:\Users\orits\OneDrive\Apps\Documents\01_WORK\IT-Training-Materials\bemi files\MYFIRSTAGENT\video_scheduler\master_schedule.json"

with open(SCHEDULE_PATH, encoding="utf-8") as f:
    data = json.load(f)

posts = data["posts"]

# ── SLOT 1: One Question reel13-20 → 11:45 UTC, Jul 25 onwards ──
OQ_IDS = [
    "onequestion_reel13_whatwouldyoudoagain",
    "onequestion_reel14_whatareyoufeeding",
    "onequestion_reel15_livingintentionally",
    "onequestion_reel16_whatwouldyoutellafriend",
    "onequestion_reel17_whatareyougratefulfor",
    "onequestion_reel18_growingoraging",
    "onequestion_reel19_whatdoessuccessmean",
    "onequestion_reel20_whatwillyouthankyourselffor",
]
base_oq = datetime(2026, 7, 25, 11, 45, 0, tzinfo=timezone.utc)
for i, post_id in enumerate(OQ_IDS):
    for p in posts:
        if p["id"] == post_id:
            old = p["scheduled_utc"]
            p["scheduled_utc"] = (base_oq + timedelta(days=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
            print(f"OQ  {post_id}: {old} -> {p['scheduled_utc']}")
            break

# ── SLOT 2: Comeback reel01-20 → 17:45 UTC, Jul 25 onwards ──
base_cb = datetime(2026, 7, 25, 17, 45, 0, tzinfo=timezone.utc)
cb_posts = [p for p in posts if p["campaign"] == "comeback" and not p.get("done")]
cb_posts.sort(key=lambda p: p["id"])  # reel01, reel02, ...
for i, p in enumerate(cb_posts):
    old = p["scheduled_utc"]
    p["scheduled_utc"] = (base_cb + timedelta(days=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"CB  {p['id']}: {old} -> {p['scheduled_utc']}")

# ── SLOT 3: notwasntlove reel03-12 → 22:00 UTC, Jul 25 onwards ──
NWL_IDS = [
    "notwasntlove_reel03_gutwasright",
    "notwasntlove_reel04_didntchangeovernight",
    "notwasntlove_reel05_dontneedclosure",
    "notwasntlove_reel06_stopchasing",
    "notwasntlove_reel07_silenttreatment",
    "notwasntlove_reel08_readthistwice",
    "notwasntlove_reel09_boundaries",
    "notwasntlove_reel10_healing",
    "notwasntlove_reel11_redflag",
    "notwasntlove_reel12_stopsettling",
]
base_nwl = datetime(2026, 7, 25, 22, 0, 0, tzinfo=timezone.utc)
for i, post_id in enumerate(NWL_IDS):
    for p in posts:
        if p["id"] == post_id:
            old = p["scheduled_utc"]
            p["scheduled_utc"] = (base_nwl + timedelta(days=i)).strftime("%Y-%m-%dT%H:%M:%SZ")
            print(f"NWL {post_id}: {old} -> {p['scheduled_utc']}")
            break

with open(SCHEDULE_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("\nSchedule updated and saved.")
print("\nSummary:")
print(f"  One Question reel13-20: Jul 25 - Aug 1  @ 11:45 UTC (6:45 AM CDT)")
print(f"  Comeback     reel01-20: Jul 25 - Aug 13 @ 17:45 UTC (12:45 PM CDT)")
print(f"  It Wasn't Love reel03-12: Jul 25 - Aug 3 @ 22:00 UTC (5:00 PM CDT)")
print(f"  It Wasn't Love reel13-20: run gen_notwasntlove_p2.py then add_nwl_reels.py")
