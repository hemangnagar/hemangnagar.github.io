#!/usr/bin/env python3
"""promote.py — post an X (Twitter) thread from a text file via the official API.

Zero dependencies (Python 3.10+ stdlib only). Dry-run by default; nothing is
posted unless you pass --send.

ONE-TIME SETUP (~10 minutes). In the X Developer Console, open your app ->
"User authentication settings" -> Set up: App permissions = "Read and write".
Then pick whichever credentials the console gives you; put them in a .env file
in this folder (it is gitignored):

  MODE A - OAuth 1.0a (preferred: the token never expires)
    "OAuth 1.0 Keys" section, after permissions are Read and write:
       X_API_KEY=...            (Consumer Key)
       X_API_SECRET=...         (Consumer Secret)
       X_ACCESS_TOKEN=...       (Access Token  - generate AFTER setting Read and write)
       X_ACCESS_SECRET=...      (Access Token Secret)

  MODE B - OAuth 2.0 (the console shows a 2-hour access token + 6-month refresh token)
    "OAuth 2.0 Keys" section:
       X_CLIENT_ID=...
       X_CLIENT_SECRET=...      (leave empty if your app is a public client)
       X_REFRESH_TOKEN=...      (the 6-month one; the 2-hour token is NOT needed)
    On every run the script exchanges the refresh token for a fresh access token
    and writes the rotated refresh token back to .env, so you never touch it again.
    Required scopes on the app: tweet.read tweet.write users.read offline.access

The script picks Mode A if all four OAuth 1.0a values are present, else Mode B.

THREAD FILE FORMAT: plain text; tweets separated by a line containing only
"---". Lines starting with "#" are comments and are skipped.

USAGE:
  python promote.py thread.txt            # dry run: shows tweets + lengths
  python promote.py thread.txt --send     # actually posts the thread
  python promote.py thread.txt --send --delay 5   # seconds between tweets

The free API tier allows ~500 posts/month — far more than a launch needs.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import secrets
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

POST_URL = "https://api.x.com/2/tweets"
TOKEN_URL = "https://api.x.com/2/oauth2/token"
ENV_PATH = Path(__file__).resolve().parent / ".env"
TWEET_LIMIT = 280  # URLs count as 23 regardless of length


def load_env_file(path: Path = ENV_PATH) -> None:
    """Minimal .env loader so the keys can live next to the script."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def save_env_value(key: str, value: str, path: Path = ENV_PATH) -> None:
    """Rewrite one KEY=value line in .env (refresh tokens rotate on every use)."""
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    out, done = [], False
    for line in lines:
        if line.split("=", 1)[0].strip() == key:
            out.append(f"{key}={value}")
            done = True
        else:
            out.append(line)
    if not done:
        out.append(f"{key}={value}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")
    os.environ[key] = value


def auth_mode() -> str:
    oauth1 = all(os.environ.get(k) for k in
                 ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET"))
    if oauth1:
        return "oauth1"
    if os.environ.get("X_CLIENT_ID") and os.environ.get("X_REFRESH_TOKEN"):
        return "oauth2"
    sys.exit(
        "No usable credentials in .env. Provide either\n"
        "  X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET   (OAuth 1.0a), or\n"
        "  X_CLIENT_ID, X_CLIENT_SECRET (optional), X_REFRESH_TOKEN  (OAuth 2.0).\n"
        "See the setup notes at the top of promote.py."
    )


def oauth2_bearer() -> str:
    """Trade the long-lived refresh token for a 2-hour access token; persist the
    rotated refresh token so the next run keeps working."""
    client_id = os.environ["X_CLIENT_ID"]
    client_secret = os.environ.get("X_CLIENT_SECRET", "")
    body = {"grant_type": "refresh_token", "refresh_token": os.environ["X_REFRESH_TOKEN"]}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if client_secret:
        basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
        headers["Authorization"] = f"Basic {basic}"
    else:
        body["client_id"] = client_id  # public client: id goes in the body
    request = urllib.request.Request(
        TOKEN_URL, data=urllib.parse.urlencode(body).encode(), method="POST", headers=headers
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as err:
        detail = err.read().decode(errors="replace")[:400]
        sys.exit(
            f"Token refresh failed ({err.code}): {detail}\n"
            "If the refresh token was already used elsewhere or has expired, generate a "
            "new one in the Developer Console and update X_REFRESH_TOKEN in .env."
        )
    if data.get("refresh_token"):
        save_env_value("X_REFRESH_TOKEN", data["refresh_token"])
    return data["access_token"]


def read_thread(path: Path) -> list[str]:
    tweets, current = [], []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() == "---":
            if current:
                tweets.append("\n".join(current).strip())
                current = []
        elif not line.lstrip().startswith("#"):
            current.append(line)
    if current:
        tweets.append("\n".join(current).strip())
    return [t for t in tweets if t]


def display_length(text: str) -> int:
    """Tweet length the way X counts it: every URL costs 23 characters."""
    length, extra = 0, 0
    for word in text.split():
        if word.startswith(("http://", "https://")):
            extra += 23 - len(word)
    return len(text) + extra


def oauth1_header(method: str, url: str, body: bytes) -> str:
    """OAuth 1.0a HMAC-SHA1 signature for a JSON-body request (params empty)."""
    creds = {name: os.environ.get(name) for name in
             ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")}
    missing = [k for k, v in creds.items() if not v]
    if missing:
        sys.exit(f"Missing credentials: {', '.join(missing)} (see setup notes in this file).")

    oauth = {
        "oauth_consumer_key": creds["X_API_KEY"],
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": creds["X_ACCESS_TOKEN"],
        "oauth_version": "1.0",
    }
    quote = lambda s: urllib.parse.quote(s, safe="")  # noqa: E731
    param_str = "&".join(f"{quote(k)}={quote(v)}" for k, v in sorted(oauth.items()))
    base = "&".join([method.upper(), quote(url), quote(param_str)])
    signing_key = f"{quote(creds['X_API_SECRET'])}&{quote(creds['X_ACCESS_SECRET'])}"
    digest = hmac.new(signing_key.encode(), base.encode(), hashlib.sha1).digest()
    oauth["oauth_signature"] = base64.b64encode(digest).decode()
    header = ", ".join(f'{quote(k)}="{quote(v)}"' for k, v in sorted(oauth.items()))
    return f"OAuth {header}"


def post_tweet(text: str, reply_to: str | None, bearer: str | None) -> str:
    payload: dict = {"text": text}
    if reply_to:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to}
    body = json.dumps(payload).encode()
    auth = f"Bearer {bearer}" if bearer else oauth1_header("POST", POST_URL, body)
    request = urllib.request.Request(
        POST_URL,
        data=body,
        method="POST",
        headers={"Authorization": auth, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as resp:
            return json.load(resp)["data"]["id"]
    except urllib.error.HTTPError as err:
        detail = err.read().decode(errors="replace")[:400]
        sys.exit(f"X API refused tweet ({err.code}): {detail}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Post an X thread from a text file.")
    parser.add_argument("thread_file", type=Path)
    parser.add_argument("--send", action="store_true", help="actually post (default: dry run)")
    parser.add_argument("--delay", type=float, default=2.0, help="seconds between tweets")
    args = parser.parse_args()

    load_env_file()
    tweets = read_thread(args.thread_file)
    if not tweets:
        sys.exit("No tweets found (separate tweets with a line containing only ---).")

    over = [(i + 1, display_length(t)) for i, t in enumerate(tweets)
            if display_length(t) > TWEET_LIMIT]
    for number, length in over:
        print(f"  !! tweet {number} is {length} chars (limit {TWEET_LIMIT})")
    if over:
        sys.exit("Fix the long tweets above, then re-run.")

    for i, tweet in enumerate(tweets, 1):
        print(f"\n--- tweet {i}/{len(tweets)} ({display_length(tweet)} chars) ---")
        print(tweet)

    if not args.send:
        mode = auth_mode()
        print(f"\nDry run only (auth: {mode}). Re-run with --send to post {len(tweets)} tweets.")
        return

    mode = auth_mode()
    bearer = oauth2_bearer() if mode == "oauth2" else None
    print(f"\nauth: {mode}")

    reply_to = None
    for i, tweet in enumerate(tweets, 1):
        reply_to = post_tweet(tweet, reply_to, bearer)
        print(f"posted {i}/{len(tweets)}: https://x.com/i/web/status/{reply_to}")
        if i < len(tweets):
            time.sleep(args.delay)
    print("\nThread posted. Pin the first tweet from the X app if it's the launch thread.")


if __name__ == "__main__":
    main()
