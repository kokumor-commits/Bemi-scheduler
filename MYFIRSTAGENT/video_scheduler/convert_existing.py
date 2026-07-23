"""
Converts existing campaign JSON files into master_schedule.json used by the custom scheduler.
Run anytime to add new campaigns. Preserves done=True for already-fired posts.
"""
import json
from pathlib import Path

BASE = Path(__file__).parent.parent
OUT  = Path(__file__).parent / "master_schedule.json"

PLATFORMS = ["facebook", "instagram", "youtube", "tiktok", "threads"]

# ── Campaigns: (json_file, [(key, "2026-MM-DDTHH:MM:SSZ"), ...]) ─────────────
# All new campaigns: 23:00 UTC = 5 PM CST, one post/day starting Aug 12
CAMPAIGNS = [
    # ── Comeback Season — 5 PM CST = 23:00 UTC — Jul 24-Aug 12 ──────────────
    (
        "comeback_urls.json",
        [
            ("Reel01_ComebackStartsToday",      "2026-07-24T23:00:00Z"),
            ("Reel02_NotStartingOver",           "2026-07-25T23:00:00Z"),
            ("Reel03_StopWaitingReady",          "2026-07-26T23:00:00Z"),
            ("Reel04_OneDecision",               "2026-07-27T23:00:00Z"),
            ("Reel05_PainHasPurpose",            "2026-07-28T23:00:00Z"),
            ("Reel06_ProtectYourMind",           "2026-07-29T23:00:00Z"),
            ("Reel07_StopComparing",             "2026-07-30T23:00:00Z"),
            ("Reel08_DisciplineBeatsMotivation", "2026-07-31T23:00:00Z"),
            ("Reel09_StoryNotFinished",          "2026-08-01T23:00:00Z"),
            ("Reel10_FailureIsntFinal",          "2026-08-02T23:00:00Z"),
            ("Reel11_SmallWins",                 "2026-08-03T23:00:00Z"),
            ("Reel12_MindBelievesWhatYouRepeat", "2026-08-04T23:00:00Z"),
            ("Reel13_StopAutopilot",             "2026-08-05T23:00:00Z"),
            ("Reel14_DontNeedEveryone",          "2026-08-06T23:00:00Z"),
            ("Reel15_KeepGoing",                 "2026-08-07T23:00:00Z"),
            ("Reel16_BuildDaily",                "2026-08-08T23:00:00Z"),
            ("Reel17_LetGo",                     "2026-08-09T23:00:00Z"),
            ("Reel18_ChooseProgress",            "2026-08-10T23:00:00Z"),
            ("Reel19_BecomeWhoYouAdmire",        "2026-08-11T23:00:00Z"),
            ("Reel20_MirrorTest",                "2026-08-12T23:00:00Z"),
        ],
    ),

    # ── It Wasn't Love — 1 PM CST = 19:00 UTC — Jul 24-Aug 3 ────────────────
    (
        "notwasntlove_urls.json",
        [
            ("Reel02_StopExplaining",      "2026-07-24T19:00:00Z"),
            ("Reel03_GutWasRight",         "2026-07-25T19:00:00Z"),
            ("Reel04_DidntChangeOvernight","2026-07-26T19:00:00Z"),
            ("Reel05_DontNeedClosure",     "2026-07-27T19:00:00Z"),
            ("Reel06_StopChasing",         "2026-07-28T19:00:00Z"),
            ("Reel07_SilentTreatment",     "2026-07-29T19:00:00Z"),
            ("Reel08_ReadThisTwice",       "2026-07-30T19:00:00Z"),
            ("Reel09_Boundaries",          "2026-07-31T19:00:00Z"),
            ("Reel10_Healing",             "2026-08-01T19:00:00Z"),
            ("Reel11_RedFlag",             "2026-08-02T19:00:00Z"),
            ("Reel12_StopSettling",        "2026-08-03T19:00:00Z"),
        ],
    ),

    # ── One Question — 7:45 PM CST = 01:45 UTC next day ──────────────────────
    (
        "onequestion_urls.json",
        [
            ("Reel01_WhoAreYouBecoming",         "2026-07-23T01:45:00Z"),
            ("Reel02_WhatAreYouTolerating",       "2026-07-24T01:45:00Z"),
            ("Reel03_IfFearDisappeared",          "2026-07-25T01:45:00Z"),
            ("Reel04_BusyOrProductive",           "2026-07-26T01:45:00Z"),
            ("Reel05_WhoBenefitsFromSelfDoubt",   "2026-07-27T01:45:00Z"),
            ("Reel06_WhatStoryAreYouRepeating",   "2026-07-28T01:45:00Z"),
            ("Reel07_WhatWouldFutureSelfSay",     "2026-07-29T01:45:00Z"),
            ("Reel08_WhatAreYouAvoiding",         "2026-07-30T01:45:00Z"),
            ("Reel09_WhatTrulyMatters",           "2026-07-31T01:45:00Z"),
            ("Reel10_WhatCanYouControl",          "2026-08-01T01:45:00Z"),
            ("Reel11_HabitsAndDreams",            "2026-08-02T01:45:00Z"),
            ("Reel12_WhoInspiresYou",             "2026-08-03T01:45:00Z"),
            ("Reel13_WhatWouldYouDoAgain",        "2026-08-04T01:45:00Z"),
            ("Reel14_WhatAreYouFeeding",          "2026-08-05T01:45:00Z"),
            ("Reel15_LivingIntentionally",        "2026-08-06T01:45:00Z"),
            ("Reel16_WhatWouldYouTellAFriend",    "2026-08-07T01:45:00Z"),
            ("Reel17_WhatAreYouGratefulFor",      "2026-08-08T01:45:00Z"),
            ("Reel18_GrowingOrAging",             "2026-08-09T01:45:00Z"),
            ("Reel19_WhatDoesSuccessMean",        "2026-08-10T01:45:00Z"),
            ("Reel20_WhatWillYouThankYourselfFor","2026-08-11T01:45:00Z"),
        ],
    ),

    # ── Abracadabra — Aug 12-16 ───────────────────────────────────────────────
    (
        "abracadabra_urls.json",
        [
            ("Day1_NoCreds",             "2026-08-12T23:00:00Z"),
            ("Day2_SixYears",            "2026-08-13T23:00:00Z"),
            ("Day3_NeverDoneIt",         "2026-08-14T23:00:00Z"),
            ("Day4_ComfortableCritics",  "2026-08-15T23:00:00Z"),
            ("Day5_WhatItFeels",         "2026-08-16T23:00:00Z"),
        ],
    ),

    # ── Lion in Rain — Aug 17-20 ──────────────────────────────────────────────
    (
        "lionrain_urls.json",
        [
            ("Day1_LionInRain",         "2026-08-17T23:00:00Z"),
            ("Day2_StormDoesntChange",  "2026-08-18T23:00:00Z"),
            ("Day3_LowPosture",         "2026-08-19T23:00:00Z"),
            ("Day4_Miscalculated",      "2026-08-20T23:00:00Z"),
        ],
    ),

    # ── Wolf — Aug 21-24 ──────────────────────────────────────────────────────
    (
        "wolf_urls.json",
        [
            ("Day4_WorldApplaudsYourLimits", "2026-08-21T23:00:00Z"),
            ("Day5_HungerIsAGift",           "2026-08-22T23:00:00Z"),
            ("Day6_YouChoseThis",            "2026-08-23T23:00:00Z"),
            ("Day7_DecideAndBuild",          "2026-08-24T23:00:00Z"),
        ],
    ),

    # ── Disappear — Aug 25-31 ─────────────────────────────────────────────────
    (
        "disappear_urls.json",
        [
            ("Day1_FourWords",          "2026-08-25T23:00:00Z"),
            ("Day2_ValidationIsALeash", "2026-08-26T23:00:00Z"),
            ("Day3_MostDangerousMan",   "2026-08-27T23:00:00Z"),
            ("Day4_SilenceIsAnxiety",   "2026-08-28T23:00:00Z"),
            ("Day5_ReturnWithResults",  "2026-08-29T23:00:00Z"),
            ("Day6_TalkLessBuildMore",  "2026-08-30T23:00:00Z"),
            ("Day7_NeverExplainTheDark","2026-08-31T23:00:00Z"),
        ],
    ),

    # ── Truth — Sep 1-7 ───────────────────────────────────────────────────────
    (
        "truth_urls.json",
        [
            ("Day1_DiscomfortIsTheSignal","2026-09-01T23:00:00Z"),
            ("Day2_SilenceIsSelfish",     "2026-09-02T23:00:00Z"),
            ("Day3_KindnessVsNiceness",   "2026-09-03T23:00:00Z"),
            ("Day4_TheFriendWhoSpeaksUp", "2026-09-04T23:00:00Z"),
            ("Day5_AudienceVsTribe",      "2026-09-05T23:00:00Z"),
            ("Day6_TruthTakesCourage",    "2026-09-06T23:00:00Z"),
            ("Day7_RaiseYourStandard",    "2026-09-07T23:00:00Z"),
        ],
    ),

    # ── Unseen — Sep 8-14 ─────────────────────────────────────────────────────
    (
        "unseen_urls.json",
        [
            ("Day1_CarriesTheHouse",             "2026-09-08T23:00:00Z"),
            ("Day2_The364Days",                  "2026-09-09T23:00:00Z"),
            ("Day3_NoCreditRequired",            "2026-09-10T23:00:00Z"),
            ("Day4_NobodyAsksHowHeIsDoing",      "2026-09-11T23:00:00Z"),
            ("Day5_PresenceIsTheLove",           "2026-09-12T23:00:00Z"),
            ("Day6_SilenceAroundTheSacrifice",   "2026-09-13T23:00:00Z"),
            ("Day7_SomebodyFinallySaysThankYou", "2026-09-14T23:00:00Z"),
        ],
    ),

    # ── RunThePlay (original series) — Sep 15-21 ──────────────────────────────
    (
        "video_urls.json",
        [
            ("Day1_RunThePlay",          "2026-09-15T23:00:00Z"),
            ("Day2_StealFromFuture",     "2026-09-16T23:00:00Z"),
            ("Day3_CEOMove",             "2026-09-17T23:00:00Z"),
            ("Day4_GodRemoved",          "2026-09-18T23:00:00Z"),
            ("Day5_HardTruth",           "2026-09-19T23:00:00Z"),
            ("Day6_TheyLeft",            "2026-09-20T23:00:00Z"),
            ("Day7_WeekCloser",          "2026-09-21T23:00:00Z"),
        ],
    ),

    # ── RunThePlay (extended) — Sep 22-28 ────────────────────────────────────
    (
        "runtheplay_urls.json",
        [
            ("Day1_SkillVsLiking",              "2026-09-22T23:00:00Z"),
            ("Day2_YouSeeAgendas",              "2026-09-23T23:00:00Z"),
            ("Day3_ConversationHasPrice",       "2026-09-24T23:00:00Z"),
            ("Day4_StopOperatingDeficit",       "2026-09-25T23:00:00Z"),
            ("Day5_EnergyIsResource",           "2026-09-26T23:00:00Z"),
            ("Day6_JesusFedThousands",          "2026-09-27T23:00:00Z"),
            ("Day7_StewardshipNotBitterness",   "2026-09-28T23:00:00Z"),
        ],
    ),

    # ── Both Were You — Sep 29 - Oct 8 ───────────────────────────────────────
    (
        "bothwereyou_urls.json",
        [
            ("Day1_GreatestBattleIsInternal",          "2026-09-29T23:00:00Z"),
            ("Day2_PublicWinsPrivateLoss",              "2026-09-30T23:00:00Z"),
            ("Day3_WhoAreYouWhenNobodysWatching",      "2026-10-01T23:00:00Z"),
            ("Day4_SameManWhoWonAlsoFell",             "2026-10-02T23:00:00Z"),
            ("Day5_PrivateFailuresDontEraseVictories", "2026-10-03T23:00:00Z"),
            ("Day6_WhatYouDoAfterTheFall",             "2026-10-04T23:00:00Z"),
            ("Day7_TheMirrorIsTheRealBattle",          "2026-10-05T23:00:00Z"),
            ("Day8_SurvivingAloneIsStrength",          "2026-10-06T23:00:00Z"),
            ("Day9_YourHardestMomentsCount",           "2026-10-07T23:00:00Z"),
            ("Day10_YouAreBoth",                       "2026-10-08T23:00:00Z"),
        ],
    ),

    # ── First No — Oct 9-18 ───────────────────────────────────────────────────
    (
        "firstno_urls.json",
        [
            ("Day1_NoRevealsEverything",         "2026-10-09T23:00:00Z"),
            ("Day2_YourYesBecameTheirGuarantee", "2026-10-10T23:00:00Z"),
            ("Day3_AlwaysAvailableMeansInvisible","2026-10-11T23:00:00Z"),
            ("Day4_TheFirstNoIsData",            "2026-10-12T23:00:00Z"),
            ("Day5_TheSuddenList",               "2026-10-13T23:00:00Z"),
            ("Day6_NotMadAtNo",                  "2026-10-14T23:00:00Z"),
            ("Day7_TheUnsignedContract",         "2026-10-15T23:00:00Z"),
            ("Day8_RealFriendsRespectNo",        "2026-10-16T23:00:00Z"),
            ("Day9_IfTheyLeaveOverNo",           "2026-10-17T23:00:00Z"),
            ("Day10_StopFeelingGuilty",          "2026-10-18T23:00:00Z"),
        ],
    ),

    # ── Decisions — Oct 19-28 ─────────────────────────────────────────────────
    (
        "decisions_urls.json",
        [
            ("Day1_ConditionsVsDecisions",  "2026-10-19T23:00:00Z"),
            ("Day2_StressIsLossOfControl",  "2026-10-20T23:00:00Z"),
            ("Day3_InfoWithoutWisdom",      "2026-10-21T23:00:00Z"),
            ("Day4_CertaintyKillsOpportunity","2026-10-22T23:00:00Z"),
            ("Day5_NotDecidingIsDeciding",  "2026-10-23T23:00:00Z"),
            ("Day6_DecideCommitResolve",    "2026-10-24T23:00:00Z"),
            ("Day7_BurnTheBoats",           "2026-10-25T23:00:00Z"),
            ("Day8_ActInTheMomentOrLoseIt", "2026-10-26T23:00:00Z"),
            ("Day9_ProblemsAreProofOfLife", "2026-10-27T23:00:00Z"),
            ("Day10_WhenInCommandTakeCharge","2026-10-28T23:00:00Z"),
        ],
    ),

    # ── Envy — Oct 29 - Nov 11 ───────────────────────────────────────────────
    (
        "envy_urls.json",
        [
            ("Day1_TheirConfession",           "2026-10-29T23:00:00Z"),
            ("Day2_MakesTheirStillnessLouder", "2026-10-30T23:00:00Z"),
            ("Day3_YouAreTheMirror",           "2026-10-31T23:00:00Z"),
            ("Day4_DontDimYourLight",          "2026-11-01T23:00:00Z"),
            ("Day5_DiscernmentNotHiding",      "2026-11-02T23:00:00Z"),
            ("Day6_BoundariesAreDoors",        "2026-11-03T23:00:00Z"),
            ("Day7_FamilyAndAccess",           "2026-11-04T23:00:00Z"),
            ("Day8_NotEverySafeToBeOpen",      "2026-11-05T23:00:00Z"),
            ("Day9_CelebrateYourself",         "2026-11-06T23:00:00Z"),
            ("Day10_FreedomFromApproval",      "2026-11-07T23:00:00Z"),
            ("Day11_BuiltInTheGap",            "2026-11-08T23:00:00Z"),
            ("Day12_JealousyRedirects",        "2026-11-09T23:00:00Z"),
            ("Day13_GrowAnyway",               "2026-11-10T23:00:00Z"),
            ("Day14_PurposeIsLouder",          "2026-11-11T23:00:00Z"),
        ],
    ),

    # ── Betrayal — Nov 12-25 ──────────────────────────────────────────────────
    (
        "betrayal_urls.json",
        [
            ("Day1_WhatTheyDid",      "2026-11-12T23:00:00Z"),
            ("Day2_AlreadyCracked",   "2026-11-13T23:00:00Z"),
            ("Day3_NotYourWorth",     "2026-11-14T23:00:00Z"),
            ("Day4_ComeSharper",      "2026-11-15T23:00:00Z"),
            ("Day5_BetrayalTaught",   "2026-11-16T23:00:00Z"),
            ("Day6_HarderToBreak",    "2026-11-17T23:00:00Z"),
            ("Day7_PremiumLoyalty",   "2026-11-18T23:00:00Z"),
            ("Day8_CarryIt",          "2026-11-19T23:00:00Z"),
            ("Day9_RaiseStandards",   "2026-11-20T23:00:00Z"),
            ("Day10_StrengthUnlocked","2026-11-21T23:00:00Z"),
            ("Day11_RecoveryRevealed","2026-11-22T23:00:00Z"),
            ("Day12_ClosedChapter",   "2026-11-23T23:00:00Z"),
            ("Day13_ReadTheMessage",  "2026-11-24T23:00:00Z"),
            ("Day14_NowMove",         "2026-11-25T23:00:00Z"),
        ],
    ),
]

# ── Already-scheduled-in-Blotato (mark done=True to skip) ────────────────────
ALREADY_SCHEDULED_IN_BLOTATO = {
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
    # Load existing schedule to preserve done=True for already-fired posts
    existing_done: set[str] = set()
    if OUT.exists():
        existing = json.loads(OUT.read_text(encoding="utf-8"))
        existing_done = {p["id"] for p in existing["posts"] if p.get("done")}

    posts = []

    for json_file, schedule in CAMPAIGNS:
        source = BASE / json_file
        if not source.exists():
            print(f"SKIP (not found): {json_file}")
            continue

        data     = json.loads(source.read_text(encoding="utf-8"))
        campaign = json_file.replace("_urls.json", "").replace("_", "")

        for key, sched_time in schedule:
            if key not in data:
                print(f"  SKIP {key} — not in {json_file} yet")
                continue

            entry   = data[key]
            post_id = f"{campaign}_{key.lower()}"
            done    = (
                any(post_id.startswith(p) for p in ALREADY_SCHEDULED_IN_BLOTATO)
                or post_id in existing_done
            )

            posts.append({
                "id":            post_id,
                "campaign":      campaign,
                "video_url":     entry["url"],
                "caption":       entry.get("caption", entry.get("text", "")),
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
    for p in posts:
        status = "DONE" if p["done"] else "PENDING"
        print(f"  [{status}] {p['id']} @ {p['scheduled_utc']}")


if __name__ == "__main__":
    convert()
