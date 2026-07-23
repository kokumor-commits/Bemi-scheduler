"""
One-time script to get YouTube OAuth2 refresh token.
Run locally, paste into GitHub Secrets. Never run again.

Usage:
  pip install google-auth-oauthlib
  python get_yt_token.py
"""
from google_auth_oauthlib.flow import InstalledAppFlow
import json

CLIENT_CONFIG = {
    "installed": {
        "client_id":     "PASTE_YOUR_CLIENT_ID",
        "client_secret": "PASTE_YOUR_CLIENT_SECRET",
        "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        "auth_uri":      "https://accounts.google.com/o/oauth2/auth",
        "token_uri":     "https://oauth2.googleapis.com/token",
    }
}

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
creds = flow.run_local_server(port=0)

print("\n=== SAVE THESE TO GITHUB SECRETS ===")
print(f"YT_CLIENT_ID:     {CLIENT_CONFIG['installed']['client_id']}")
print(f"YT_CLIENT_SECRET: {CLIENT_CONFIG['installed']['client_secret']}")
print(f"YT_REFRESH_TOKEN: {creds.refresh_token}")
