#!/usr/bin/env python3
"""promote.py — post an X (Twitter) thread from a text file via the official API.

Zero dependencies (Python 3.10+ stdlib only). Dry-run by default; nothing is
posted unless you pass --send.

ONE-TIME SETUP (~10 minutes, no phone needed if your X account is verified by email):
  1. Sign in to https://developer.x.com with your X account -> Free tier.
  2. Create a Project + App. In the app's "User authentication settings":
     enable OAuth 1.0a, App permissions = "Read and write".
  3. From "Keys and tokens", copy 4 values into a .env file (or your shell):
       X_API_KEY=...            (a.k.a. consumer key)
       X_API_SECRET=...         (consumer secret)
       X_ACCESS_TOKEN=...       (your account's access token)
       X_ACCESS_SECRET=...      (access token secret)
     Regenerate the access token AFTER setting permissions to Read and write.

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
TWEET_LIMIT = 280  # URLs count as 23 regardless of length


def load_env_file(path: Path = Path(".env")) -> None:
    """Minimal .env loader so the four keys can live next to the script."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


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


def post_tweet(text: str, reply_to: str | None) -> str:
    payload: dict = {"text": text}
    if reply_to:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to}
    body = json.dumps(payload).encode()
    request = urllib.request.Request(
        POST_URL,
        data=body,
        method="POST",
        headers={
            "Authorization": oauth1_header("POST", POST_URL, body),
            "Content-Type": "application/json",
        },
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
        print(f"\nDry run only. Re-run with --send to post {len(tweets)} tweets.")
        return

    reply_to = None
    for i, tweet in enumerate(tweets, 1):
        reply_to = post_tweet(tweet, reply_to)
        print(f"posted {i}/{len(tweets)}: https://x.com/i/web/status/{reply_to}")
        if i < len(tweets):
            time.sleep(args.delay)
    print("\nThread posted. Pin the first tweet from the X app if it's the launch thread.")


if __name__ == "__main__":
    main()
