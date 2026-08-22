"""
20-video "Win... And Still Lose" series, v2 -- Les Brown-style delivery,
DISTINCT hook/body/CTA per variant (approved by user, replaces wonbutlost
which used one repeated hook and was rejected).

The "hook" here is the persistent on-screen banner (video_agent's single
7s-window banner, pulled from scene 1's onscreen_text) -- each video gets
its OWN hook line, not a shared one.

Schedules FB/IG/YT via Bemi Scheduler (master_schedule.json), and writes
matching TikTok payloads to lesbrown_tiktok_payloads.json for a follow-up
Blotato posting pass (standing rule: TikTok always pairs with Bemi
Scheduler content).
Daily 6pm CDT (23:00 UTC), starting today, for 20 days.
"""
import json, os, time
from datetime import datetime, timedelta, timezone
import httpx

API = "https://videoai-studio-production.up.railway.app"
VOICE_ID = "NxPNwIH7URVgZ9rWBH4P"  # Tega, high-tone default

DIR = os.path.dirname(__file__)
SCHEDULE_PATH = os.path.join(DIR, "video_scheduler", "master_schedule.json")
TIKTOK_PAYLOADS_PATH = os.path.join(DIR, "lesbrown_tiktok_payloads.json")
PLATFORMS = ["facebook", "instagram", "youtube"]
START_DATE = datetime(2026, 8, 22, tzinfo=timezone.utc)  # today
SLOT_HOUR_UTC = 23
SLOT_MIN_UTC = 0  # 6pm CDT

FB_TAGS = "#Motivation #Mindset #LesBrown"
TT_TAGS = "#MotivationTok #MindsetTok #Inspiration #Discipline"

ITEMS = [
    {"id": "lesbrown_d01", "title": "Winning the Argument, Losing the Person",
     "hook": "WINNING THE FIGHT CAN COST YOU THE PERSON.",
     "body": "Listen to me. You can win every single argument with the person you love, and still lose them. Being right doesn't warm an empty bed. Being right doesn't answer the phone when they stop calling. Somebody out there is winning every fight and losing their whole family one 'I told you so' at a time. Don't you dare trade a relationship for a debate you'll forget by next week.",
     "cta": "Choose the person over the point. Tag someone who needs to hear this."},
    {"id": "lesbrown_d02", "title": "Winning Likes, Losing Friends",
     "hook": "A THOUSAND LIKES CAN'T CALL YOU AT 2AM.",
     "body": "You can win a thousand likes today, and still be lonely tonight. That's the truth nobody wants to say out loud. A screen full of hearts will not sit with you in the hospital waiting room. It will not show up with food when life falls apart. Stop chasing applause from strangers and start investing in the three people who'd drop everything for you.",
     "cta": "Call a real friend today. Not a follower, a friend."},
    {"id": "lesbrown_d03", "title": "Winning Tonight, Losing Tomorrow",
     "hook": "YOU CAN WIN THE GAME AND LOSE TOMORROW.",
     "body": "I need you to hear this. You can stay up all night winning, and wake up defeated before the day even starts. Your body doesn't remember the score. It remembers whether you rested it. Champions protect their sleep like it's sacred, because it is. Put it down. Tomorrow is waiting on you to show up rested, not just entertained.",
     "cta": "Set it down tonight. Your future needs you sharp."},
    {"id": "lesbrown_d04", "title": "Winning at Busy, Losing the Day",
     "hook": "BUSY IS NOT THE SAME AS MOVING FORWARD.",
     "body": "Somebody's out here running around all day, checking boxes, answering messages, and going nowhere. Motion is not progress. You can be exhausted and still be standing in the exact same spot you started. Ask yourself tonight, did I just look productive, or did I actually build something today?",
     "cta": "Do one thing today that actually moves you forward."},
    {"id": "lesbrown_d05", "title": "Winning Approval, Losing Yourself",
     "hook": "APPROVAL FROM EVERYONE CAN COST YOU YOU.",
     "body": "You can win the approval of an entire room, and lose yourself completely in the process. Every time you shrink to keep the peace, a piece of you goes missing. And one day you'll look up surrounded by people who love a version of you that isn't even real. Stop performing. Start being.",
     "cta": "Be who you are. The right people will stay."},
    {"id": "lesbrown_d06", "title": "Winning the Grade, Losing the Lesson",
     "hook": "THE SHORTCUT STEALS THE LESSON.",
     "body": "You can win the grade by copying the answer, and lose the lesson that would've built you. That test in the classroom is nothing compared to the test life is going to give you later, and life doesn't hand out cheat sheets. Do the hard work now. The struggle is not your enemy, it's your training.",
     "cta": "Do the work. Your future self is counting on it."},
    {"id": "lesbrown_d07", "title": "Winning Comfort, Losing Growth",
     "hook": "COMFORT TODAY. REGRET TOMORROW.",
     "body": "You can win comfort every single day of your life, and lose the greatness you were capable of. Nothing, I said nothing, ever grew in that easy chair. Growth lives in the room you keep avoiding, in the conversation you keep postponing, in the workout you keep skipping. Get uncomfortable on purpose.",
     "cta": "Do the uncomfortable thing today. Growth is waiting on the other side."},
    {"id": "lesbrown_d08", "title": "Winning the Argument With Your Child, Losing Their Trust",
     "hook": "YOU WON THE ARGUMENT. DID YOU KEEP THEIR TRUST?",
     "body": "You can win the argument with your own child, and lose the one thing you actually needed, their trust. Being louder does not mean you were right. Being the parent does not mean you get to be cruel. That child is watching how you handle power, and they will remember. Choose connection over control.",
     "cta": "Repair it today if you have to. Trust is worth the humility."},
    {"id": "lesbrown_d09", "title": "Winning the Deal, Losing Your Name",
     "hook": "MONEY COMES BACK. YOUR NAME DOESN'T.",
     "body": "You can win the deal by cutting a corner, and lose your name in the process. And your name, your reputation, that's the one thing that follows you into every room for the rest of your life. People forget the price. They never forget how you made them feel while you took it. Protect your name like it's everything, because it is.",
     "cta": "Do business the right way. Your name is worth more than the deal."},
    {"id": "lesbrown_d10", "title": "Winning the Race, Losing Why You Started",
     "hook": "YOU WON THE RACE. WHERE'S THE JOY?",
     "body": "You can cross that finish line first, and still lose the reason you started running. Somewhere between the starting gun and the trophy, some of you forgot you used to love this. Winning without joy is just an expensive way of losing. Go back and remember why you started.",
     "cta": "Reconnect with your why today."},
    {"id": "lesbrown_d11", "title": "Winning Attention, Losing Peace",
     "hook": "LOUD LIVES DON'T LAST. PEACE DOES.",
     "body": "You can win everybody's attention through drama, and lose the only thing that was ever going to make you happy, your peace. Being talked about is not the same as being respected. A loud life gets you noticed. A peaceful life gets you free. Choose peace, even when it's quiet, even when nobody's clapping.",
     "cta": "Walk away from the drama. Choose your peace."},
    {"id": "lesbrown_d12", "title": "Winning Favor, Losing Your Time",
     "hook": "EVERY YES TO THEM IS A NO TO YOU.",
     "body": "You can win everybody's favor by always saying yes, and lose your entire life doing it. Your calendar can be completely full and your purpose completely empty at the same time. Somebody has to guard your time, and if it's not you, it's going to be everybody else. Protect it like the treasure it is.",
     "cta": "Say no to one thing today so you can say yes to your purpose."},
    {"id": "lesbrown_d13", "title": "Winning the Promotion, Losing Their Respect",
     "hook": "YOU CLIMBED. WHO DID YOU STEP ON?",
     "body": "You can win that promotion by stepping over people on your way up, and lose their respect on the way there. That title looks powerful on paper. It looks empty in the room once everybody remembers how you got it. Climb, I want you to climb, just don't climb over the people who helped build the ladder.",
     "cta": "Bring somebody up with you on your way up."},
    {"id": "lesbrown_d14", "title": "Winning the Shortcut, Losing the Skill",
     "hook": "THE SHORTCUT TODAY COSTS YOU A LIFETIME OF SKILL.",
     "body": "You can win the shortcut, and lose the skill you would have built walking the long way. A shortcut gets you there fast one time. Skill gets you there fast every time after. Stop trading your ability for convenience. Put in the work now so you never have to depend on luck again.",
     "cta": "Choose the long way. Build the skill."},
    {"id": "lesbrown_d15", "title": "Winning Tonight's Craving, Losing Tomorrow's Strength",
     "hook": "ONE MEAL WON'T BREAK YOU. A THOUSAND WILL.",
     "body": "You can win tonight's craving, and lose tomorrow's strength. It's not one meal, it's not one skipped workout, it's the thousand small surrenders nobody sees that quietly write the story of your health. Your future self has to live in the body you're building right now. Choose like they're watching, because they are.",
     "cta": "Make one healthy choice today. Your body is listening."},
    {"id": "lesbrown_d16", "title": "Winning the Last Word, Losing the Friendship",
     "hook": "YOU GOT THE LAST WORD. WAS IT WORTH THE FRIENDSHIP?",
     "body": "You can win the last word in that argument, and lose the friendship completely. Somewhere along the way people forgot that being understood matters more than being finished talking. Let it go. A real friendship is worth more than any point you'll forget you even made.",
     "cta": "Let the last word go. Keep the friend."},
    {"id": "lesbrown_d17", "title": "Winning by Holding On, Losing What Giving Brings Back",
     "hook": "A CLOSED HAND CAN'T RECEIVE ANYTHING NEW.",
     "body": "You can win by holding on to everything you have, and lose everything generosity was going to bring back to you. A closed fist cannot receive a single new thing. I have watched the most generous people I know end up with the most, because what you pour out always finds a way back. Open your hand.",
     "cta": "Give something away today. Watch what comes back."},
    {"id": "lesbrown_d18", "title": "Winning the Trophy, Losing the Love",
     "hook": "YOU WON THE TROPHY. DID YOU KEEP THE LOVE?",
     "body": "You can win the trophy, and lose the reason you picked up the ball in the first place. Somewhere between practice and the podium, some of you forgot you used to play just because you loved it. Hold the trophy up high. But don't you dare let it replace the love that got you there.",
     "cta": "Reconnect with why you started playing."},
    {"id": "lesbrown_d19", "title": "Winning Control, Losing Trust",
     "hook": "CONTROL FEELS SAFE. TRUST IS WHAT LASTS.",
     "body": "You can win control over every single detail around you, and lose everyone's trust in the process. People do not stay because you managed their every move. People stay because you gave them room to breathe. Let go of the grip. Trust is the only thing that actually keeps people close.",
     "cta": "Loosen the grip today. Let trust do the work."},
    {"id": "lesbrown_d20", "title": "The Real Question",
     "hook": "WHAT ARE YOU WILLING TO LOSE TO WIN?",
     "body": "You can spend your entire life winning, and still lose. Because a win never asks if it was the right goal, it only asks if you got there first. So I need you to ask yourself the real question tonight, what am I willing to lose to get this? Choose a goal worth losing something for. Choose a goal worth your whole life.",
     "cta": "Choose the goal that's actually worth chasing."},
]


def build_prompt(item):
    full_script = f"{item['body']} {item['cta']}"
    return f"""Write this video in a Les Brown-style delivery -- bold, passionate, direct address to the viewer, short punchy declarative sentences, rhetorical questions, urgency, personal conviction, like a motivational speaker preaching truth, not a calm narrator. Use the exact wording below as the base (you may add natural spoken emphasis/pacing but keep the substance and phrasing intact, do not soften or generalize it).

CRITICAL: Scene 1's onscreen_text MUST be exactly this line, verbatim, all caps: "{item['hook']}"
This is the persistent on-screen hook banner that stays visible for the first several seconds of the video -- it must match exactly, not be paraphrased.

Voiceover script (Les Brown energy, passionate delivery):
\"\"\"{full_script}\"\"\"

Title should be close to: "{item['title']}"

Build matching onscreen_text/image_prompt scenes around the script (short bold on-screen text per scene after scene 1, cinematic photorealistic image prompts, no text baked into images, no faces/people in the images -- faceless/illustrative visuals)."""


def submit(item, retries=3):
    payload = {
        "prompt": build_prompt(item),
        "duration": "30",
        "style": "Cinematic, bold, passionate, illustrative",
        "platform": "TikTok/Reels/Shorts",
        "audience": "General, all ages",
        "tone": "Passionate, direct, Les Brown-style motivational speaker",
        "hook": "Bold declarative statement",
        "cta": "",
        "media_source": "ai_images",
        "music_mood": "uplifting",
        "export_formats": ["9:16"],
        "voice_id": VOICE_ID,
    }
    for attempt in range(retries):
        try:
            r = httpx.post(f"{API}/api/generate", json=payload, timeout=120)
            r.raise_for_status()
            return r.json()["job_id"]
        except (httpx.TransportError, httpx.HTTPStatusError) as e:
            if attempt == retries - 1:
                raise
            print(f"  submit retry {attempt+1}/{retries} after error: {e}", flush=True)
            time.sleep(5)


def poll(job_id, timeout=1800):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = httpx.get(f"{API}/api/jobs/{job_id}", timeout=30)
            d = r.json()
        except httpx.TransportError as e:
            print(f"  poll transient error, retrying: {e}", flush=True)
            time.sleep(10)
            continue
        status = d.get("status")
        if status == "done":
            return d
        if status == "failed":
            raise RuntimeError(f"job {job_id} failed: {d.get('error')}")
        time.sleep(10)
    raise RuntimeError(f"job {job_id} timed out")


def already_scheduled(post_id):
    with open(SCHEDULE_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return any(p["id"] == post_id for p in data["posts"])


def add_to_schedule(post_id, video_url, caption, yt_title, scheduled_utc, thumbnail_url=""):
    with open(SCHEDULE_PATH, encoding="utf-8") as f:
        data = json.load(f)
    data["posts"].append({
        "id": post_id, "campaign": "lesbrown", "video_url": video_url,
        "caption": caption, "yt_title": yt_title, "scheduled_utc": scheduled_utc,
        "thumbnail_url": thumbnail_url,
        "platforms": PLATFORMS, "done": False,
    })
    with open(SCHEDULE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_tt_payloads():
    if os.path.exists(TIKTOK_PAYLOADS_PATH):
        with open(TIKTOK_PAYLOADS_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_tt_payload(payloads, entry):
    payloads.append(entry)
    with open(TIKTOK_PAYLOADS_PATH, "w", encoding="utf-8") as f:
        json.dump(payloads, f, indent=2, ensure_ascii=False)


def main():
    produced = []
    tt_payloads = load_tt_payloads()
    tt_ids_done = {p["id"] for p in tt_payloads}

    for i, item in enumerate(ITEMS):
        post_id = item["id"]
        sched = (START_DATE + timedelta(days=i)).replace(hour=SLOT_HOUR_UTC, minute=SLOT_MIN_UTC, second=0)
        sched_str = sched.strftime("%Y-%m-%dT%H:%M:%SZ")

        if already_scheduled(post_id):
            print(f"[{post_id}] already scheduled, skip", flush=True)
        else:
            jid = submit(item)
            print(f"[{post_id}] submitted -> job {jid}, waiting...", flush=True)
            d = poll(jid)
            video_url = d.get("output_url")
            thumbnail_url = d.get("thumbnail_url", "")
            full_script = f"{item['body']} {item['cta']}"
            caption = f"{item['title']}\n\n{full_script}\n\n{FB_TAGS}"
            add_to_schedule(post_id, video_url, caption, item["title"][:100], sched_str, thumbnail_url)
            produced.append(post_id)
            print(f"[{post_id}] done -> {video_url}", flush=True)

            if post_id not in tt_ids_done:
                tt_caption = f"{item['hook']} {item['cta']}\n{TT_TAGS}"
                save_tt_payload(tt_payloads, {
                    "id": post_id, "video_url": video_url, "title": item["title"][:100],
                    "tt_caption": tt_caption, "scheduledTime": sched_str,
                })

    print(f"\n\n=== {len(produced)} posts produced and scheduled (FB/IG/YT) ===", flush=True)
    if produced:
        import subprocess
        os.chdir(os.path.join(DIR, "video_scheduler"))
        subprocess.run(["git", "add", "master_schedule.json"], check=True)
        subprocess.run(["git", "commit", "-m",
                         f"feat: schedule {len(produced)} Les Brown 'Win And Still Lose' reels, Aug 22-Sep 10 2026 6pm CDT"],
                        check=True)
        subprocess.run(["git", "pull", "--rebase", "origin", "main"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("Pushed. Railway worker will pick it up.", flush=True)
    print(f"TikTok payloads written to {TIKTOK_PAYLOADS_PATH} for Blotato posting pass.", flush=True)


if __name__ == "__main__":
    main()
