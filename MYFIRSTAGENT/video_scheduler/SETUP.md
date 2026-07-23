# Custom Video Scheduler — Setup Guide

Cost: $0/month. Runs on GitHub Actions.

---

## Step 1: Push repo to GitHub

```bash
# In the MYFIRSTAGENT folder:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

---

## Step 2: Get platform tokens

### Meta (Facebook + Instagram + Threads)
1. Go to https://developers.facebook.com → your app → Graph API Explorer
2. Select your app, grant permissions: `pages_manage_posts`, `instagram_basic`, `instagram_content_publish`, `threads_content_publish`
3. Generate → Exchange for Long-Lived Token (valid 60 days)
4. Get your Page Access Token (never expires for Pages)
5. Your Page ID: `590549717478634` (already known)
6. Instagram Account ID: run this in Graph Explorer:
   `GET /me/accounts` → find your page → `GET /{page-id}?fields=instagram_business_account`
7. Threads User ID: `GET /me?fields=id` using Threads token

### YouTube
1. Go to https://console.cloud.google.com
2. Create project → Enable YouTube Data API v3
3. Create OAuth 2.0 credentials (Desktop App)
4. Run this one-time to get refresh token:
   ```bash
   pip install google-auth-oauthlib
   python video_scheduler/get_yt_token.py
   ```
   (see get_yt_token.py for instructions)

### TikTok
1. Go to https://developers.tiktok.com → your app
2. Get Client Key + Client Secret
3. Generate user access token via OAuth flow
4. Access tokens expire in 24h — set up refresh token for auto-renewal

---

## Step 3: Add GitHub Secrets

Go to your GitHub repo → Settings → Secrets → Actions → New secret

Add these secrets:
```
META_PAGE_TOKEN      = your long-lived page token
FB_PAGE_ID           = 590549717478634
IG_ACCOUNT_ID        = (your IG business account numeric ID)
THREADS_USER_ID      = (your Threads user numeric ID)
THREADS_TOKEN        = (Threads access token — often same as META_PAGE_TOKEN)
YT_CLIENT_ID         = (from Google Cloud)
YT_CLIENT_SECRET     = (from Google Cloud)
YT_REFRESH_TOKEN     = (from one-time auth flow)
TIKTOK_ACCESS_TOKEN  = (from TikTok developer portal)
TIKTOK_REFRESH_TOKEN = (for auto-renewal)
TIKTOK_CLIENT_KEY    = (from TikTok developer portal)
TIKTOK_CLIENT_SECRET = (from TikTok developer portal)
```

---

## Step 4: Build master_schedule.json

```bash
cd MYFIRSTAGENT
python video_scheduler/convert_existing.py
```

This reads your existing campaign JSON files and creates `video_scheduler/master_schedule.json`.

---

## Step 5: Push & activate

```bash
git add video_scheduler/master_schedule.json
git commit -m "Add master schedule"
git push
```

GitHub Actions will now run every 15 minutes and post anything due.

---

## Adding new campaigns

1. Generate videos → save URLs to a JSON file (same format as comeback_urls.json)
2. Add campaign to `convert_existing.py` CAMPAIGNS list with dates
3. Re-run `python video_scheduler/convert_existing.py`
4. Commit and push — scheduler picks it up automatically

No post limits. No monthly fees.
