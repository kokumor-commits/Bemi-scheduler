import asyncio, httpx, json, os

DAWN = "https://videoai-studio-production.up.railway.app"
OUT_JSON = r"c:\Users\orits\OneDrive\Apps\Documents\01_WORK\IT-Training-Materials\bemi files\MYFIRSTAGENT\notwasntlove_urls.json"

DAYS = [
    {
        "key": "Reel13_ForgiveYourself",
        "prompt": "You may find it easier to forgive them than to forgive yourself. You forgave their lies. Their disrespect. Their broken promises. But you haven't forgiven yourself for staying. For believing. For loving someone who wasn't ready to receive it. Your love wasn't the mistake. Staying past your own warnings was the lesson. Forgive yourself. You were learning.",
        "caption": "You may find it easier to forgive them than to forgive yourself.\n\nYou forgave their lies.\nTheir disrespect.\nTheir broken promises.\n\nBut you haven't forgiven yourself for staying.\nFor believing.\nFor loving someone who wasn't ready to receive it.\n\nYour love wasn't the mistake.\n\nStaying past your own warnings was the lesson.\n\nForgive yourself. You were learning.\n\n#ForgiveYourself #HealingJourney #YouWereLearning",
        "yt_title": "You Forgave Them Already — Now It's Time To Forgive Yourself #Shorts",
    },
    {
        "key": "Reel14_LovingWrong",
        "prompt": "Some people don't know how to receive love. They were never taught that love could be consistent. Safe. Without conditions. When you showed up consistently, they became suspicious. When you gave without expecting, they felt indebted. When you were kind, they mistook it for weakness. You weren't loving the wrong person. You were loving someone who hadn't healed enough to receive it.",
        "caption": "Some people don't know how to receive love.\n\nThey were never taught that love could be consistent.\nSafe. Without conditions.\n\nWhen you showed up consistently — they became suspicious.\nWhen you gave without expecting — they felt indebted.\nWhen you were kind — they mistook it for weakness.\n\nYou weren't loving the wrong person.\n\nYou were loving someone who hadn't healed enough to receive it.\n\n#LoveWithoutHealing #HealingJourney #YouDeserveMore",
        "yt_title": "Some People Don't Know How To Receive Love — It Wasn't Your Fault #Shorts",
    },
    {
        "key": "Reel15_TooMuch",
        "prompt": "They told you that you weren't enough. But the truth is something different. You were too much awareness for someone who wanted comfort in ignorance. Too much honesty for someone who relied on pretending. Too much depth for someone who only wanted the surface. You were not too little. You were too evolved for where they were.",
        "caption": "They told you that you weren't enough.\n\nBut the truth is something different.\n\nYou were too much awareness for someone who wanted comfort in ignorance.\nToo much honesty for someone who relied on pretending.\nToo much depth for someone who only wanted the surface.\n\nYou were not too little.\n\nYou were too evolved for where they were.\n\n#YouWereEnough #TooMuch #HealingJourney",
        "yt_title": "You Weren't Not Enough — You Were Too Much For Where They Were #Shorts",
    },
    {
        "key": "Reel16_BeforeLovingAgain",
        "prompt": "Before you love someone new, love yourself back. The relationship you lost took pieces of you. Your confidence. Your trust. Your sense of self. Before you invite someone else in, rebuild what was taken. You cannot give from an empty place. Healing isn't selfish. It is how you protect the next person you love and the love they deserve.",
        "caption": "Before you love someone new — love yourself back.\n\nThe relationship you lost took pieces of you.\nYour confidence.\nYour trust.\nYour sense of self.\n\nBefore you invite someone else in —\nrebuild what was taken.\n\nYou cannot give from an empty place.\n\nHealing isn't selfish.\nIt is how you protect the next person you love.\n\n#LoveYourselfFirst #BeforeLovingAgain #HealingJourney",
        "yt_title": "Before Loving Again — Rebuild What The Last Relationship Took From You #Shorts",
    },
    {
        "key": "Reel17_EmotionalMaturity",
        "prompt": "You cannot build a future with someone who is still at war with their past. Emotional immaturity looks like this. They misread kindness as weakness. They punish vulnerability. They confuse love with control. It isn't something you can love them out of. Emotional growth only happens when someone chooses it for themselves. You deserve someone who has already done their work.",
        "caption": "You cannot build a future with someone who is still at war with their past.\n\nEmotional immaturity looks like this:\n\nThey misread kindness as weakness.\nThey punish vulnerability.\nThey confuse love with control.\n\nIt isn't something you can love them out of.\n\nEmotional growth only happens when someone chooses it for themselves.\n\nYou deserve someone who has already done their work.\n\n#EmotionalMaturity #HealingJourney #DoYourWork",
        "yt_title": "You Can't Build A Future With Someone Still At War With Their Past #Shorts",
    },
    {
        "key": "Reel18_BreakingPatterns",
        "prompt": "Notice the pattern before you repeat it. Same person. Different name. You chose someone emotionally unavailable again. Someone who needed fixing. Someone who confused intensity with love. Patterns don't break on their own. They break when you do the inner work to understand why you chose them in the first place. Break the cycle before the cycle breaks you.",
        "caption": "Notice the pattern before you repeat it.\n\nSame person. Different name.\n\nYou chose someone emotionally unavailable again.\nSomeone who needed fixing.\nSomeone who confused intensity with love.\n\nPatterns don't break on their own.\n\nThey break when you do the inner work to understand\nwhy you chose them in the first place.\n\nBreak the cycle before the cycle breaks you.\n\n#BreakThePattern #HealingJourney #CycleBreaker",
        "yt_title": "Notice The Pattern Before You Repeat It — Same Person Different Name #Shorts",
    },
    {
        "key": "Reel19_NotYourJob",
        "prompt": "It was never your job to fix them. You poured your energy into someone who wasn't doing the same. You researched. You adjusted. You communicated. You hoped. But healing someone else is not your responsibility. Their growth must come from within. The most loving thing you ever did was let go of someone who wasn't ready to grow.",
        "caption": "It was never your job to fix them.\n\nYou poured your energy into someone who wasn't doing the same.\n\nYou researched.\nYou adjusted.\nYou communicated.\nYou hoped.\n\nBut healing someone else is not your responsibility.\n\nTheir growth must come from within.\n\nThe most loving thing you ever did was let go of someone who wasn't ready to grow.\n\n#NotYourJob #LetGo #HealingJourney",
        "yt_title": "It Was Never Your Job To Fix Them — Let That Weight Go #Shorts",
    },
    {
        "key": "Reel20_WhatComesNext",
        "prompt": "Real love feels different. You'll notice it in how you breathe when they're near. There will be no anxiety. No second guessing. No walking on eggshells. Real love feels like exhaling after years of holding your breath. It feels like safety. Like home. Like rest. It is coming. Keep healing. Keep becoming. What comes next is worth it.",
        "caption": "Real love feels different.\n\nYou'll notice it in how you breathe when they're near.\n\nThere will be no anxiety.\nNo second-guessing.\nNo walking on eggshells.\n\nReal love feels like exhaling after years of holding your breath.\n\nIt feels like safety.\nLike home.\nLike rest.\n\nIt is coming.\nKeep healing. Keep becoming.\n\nWhat comes next is worth it.\n\n#RealLoveFeelsDifferent #HealingJourney #WhatComesNext",
        "yt_title": "Real Love Feels Like Exhaling — Here's How You'll Know When It Arrives #Shorts",
    },
]

SETTINGS = {
    "duration": "30",
    "style": "Cinematic emotional dark moody intimate close-ups raw vulnerability stark contrast dramatic pacing bold visuals",
    "tone": "Emotional",
    "hook": "Bold Statement",
    "media_source": "ai_images",
    "music_mood": "emotional",
    "export_formats": ["9:16"],
}


def load_json(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


async def submit_job(client, day):
    for attempt in range(20):
        try:
            r = await client.post(
                f"{DAWN}/api/generate",
                json={"prompt": day["prompt"], **SETTINGS},
                timeout=30,
            )
            r.raise_for_status()
            job_id = r.json().get("job_id")
            print(f"[{day['key']}] submitted {job_id}", flush=True)
            return job_id
        except Exception as e:
            print(f"[{day['key']}] attempt {attempt+1} failed: {str(e)[:60]}", flush=True)
            await asyncio.sleep(15)
    print(f"[{day['key']}] GAVE UP", flush=True)
    return None


async def poll_job(client, key, job_id):
    for attempt in range(360):
        await asyncio.sleep(5)
        try:
            r = await client.get(f"{DAWN}/api/jobs/{job_id}", timeout=15)
            if r.status_code != 200:
                continue
            data = r.json()
            status = data.get("status")
            url = data.get("output_url", "")
            if attempt % 12 == 0:
                print(f"[{key}] {attempt*5}s: {status}", flush=True)
            if status == "done" and url:
                print(f"[{key}] DONE -> {url}", flush=True)
                return url
            if status == "failed":
                print(f"[{key}] FAILED: {data.get('error')}", flush=True)
                return None
        except Exception:
            pass
    print(f"[{key}] timed out", flush=True)
    return None


async def main():
    results = load_json(OUT_JSON)

    async with httpx.AsyncClient(timeout=300) as client:
        for day in DAYS:
            if day["key"] in results and results[day["key"]].get("url"):
                print(f"[{day['key']}] already done, skipping", flush=True)
                continue
            job_id = await submit_job(client, day)
            if not job_id:
                continue
            await asyncio.sleep(5)
            url = await poll_job(client, day["key"], job_id)
            if url:
                results[day["key"]] = {
                    "url": url,
                    "caption": day["caption"],
                    "yt_title": day["yt_title"],
                }
                save_json(OUT_JSON, results)
                print(f"[{day['key']}] saved", flush=True)

    print("ALL DONE", flush=True)
    print_summary(results)


def print_summary(results):
    print("\n=== GENERATED URLS ===", flush=True)
    for day in DAYS:
        key = day["key"]
        if key in results and results[key].get("url"):
            print(f"{key}: {results[key]['url']}", flush=True)
        else:
            print(f"{key}: MISSING", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
