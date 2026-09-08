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
"---". Lines starting with "#" are comments and are skipped. A line of the form
"@media path/to/image.png" inside a tweet attaches that image to it (path
relative to the thread file; png/jpg/gif/webp, <= 5 MB, up to 4 per tweet).

USAGE:
  python promote.py thread.txt            # dry run: shows tweets + lengths
  python promote.py thread.txt --send     # actually posts the thread
  python promote.py thread.txt --send --delay 5   # seconds between tweets

NOTE (Sept 2026): posting through the API now draws on a paid credit balance.
With no credits the API answers 402 "credits depleted" and nothing is posted.
For a single thread, posting by hand is free: use the dry run to get the text,
then post tweet 1 and reply to it with each following tweet.
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
MEDIA_URL_V2 = "https://api.x.com/2/media/upload"           # current (2025+)
MEDIA_URL_V1 = "https://upload.twitter.com/1.1/media/upload.json"  # legacy fallback
TWEET_LIMIT = 280  # URLs count as 23 regardless of length
MEDIA_LIMIT_BYTES = 5 * 1024 * 1024
MEDIA_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
               ".gif": "image/gif", ".webp": "image/webp"}


def load_env_file(path: Path = Path(".env")) -> None:
    """Minimal .env loader so the four keys can live next to the script."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def read_thread(path: Path) -> tuple[list[str], list[list[Path]]]:
    """Return (tweets, media) where media[i] lists the image paths for tweet i."""
    tweets, media, current, attachments = [], [], [], []
    def flush():
        text = "\n".join(current).strip()
        if text or attachments:
            tweets.append(text)
            media.append(list(attachments))
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "---":
            flush(); current, attachments = [], []
        elif stripped.startswith("@media "):
            attachments.append((path.parent / stripped[len("@media "):].strip()).resolve())
        elif not line.lstrip().startswith("#"):
            current.append(line)
    flush()
    return tweets, media


def check_media(paths: list[Path]) -> list[str]:
    """Problems with attachments (empty list = fine). Runs in dry-run too."""
    problems = []
    if len(paths) > 4:
        problems.append(f"{len(paths)} attachments (max 4 per tweet)")
    for path in paths:
        if not path.exists():
            problems.append(f"missing file: {path}")
        elif path.suffix.lower() not in MEDIA_TYPES:
            problems.append(f"unsupported type: {path.name}")
        elif path.stat().st_size > MEDIA_LIMIT_BYTES:
            problems.append(f"{path.name} is {path.stat().st_size / 1e6:.1f} MB (limit 5 MB)")
    return problems


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


def _multipart(fields: dict[str, str], file_field: str, path: Path, mime: str) -> tuple[bytes, str]:
    boundary = "----promote" + secrets.token_hex(12)
    out = bytearray()
    for name, value in fields.items():
        out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n"
                f"{value}\r\n").encode()
    out += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{file_field}\"; "
            f"filename=\"{path.name}\"\r\nContent-Type: {mime}\r\n\r\n").encode()
    out += path.read_bytes()
    out += f"\r\n--{boundary}--\r\n".encode()
    return bytes(out), f"multipart/form-data; boundary={boundary}"


def upload_media(path: Path) -> str:
    """Upload one image; return its media id. Tries the v2 endpoint, then v1.1.
    OAuth 1.0a signs only the oauth params for multipart bodies, so the same
    header builder works for both endpoints."""
    mime = MEDIA_TYPES[path.suffix.lower()]
    attempts = (
        (MEDIA_URL_V2, {"media_category": "tweet_image", "media_type": mime}),
        (MEDIA_URL_V1, {"media_category": "tweet_image"}),
    )
    last_error = ""
    for url, fields in attempts:
        body, content_type = _multipart(fields, "media", path, mime)
        request = urllib.request.Request(
            url, data=body, method="POST",
            headers={"Authorization": oauth1_header("POST", url, body),
                     "Content-Type": content_type},
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as resp:
                data = json.load(resp)
        except urllib.error.HTTPError as err:
            last_error = f"{url} -> {err.code}: {err.read().decode(errors='replace')[:300]}"
            continue
        media_id = (data.get("data") or {}).get("id") or data.get("media_id_string")
        if media_id:
            return str(media_id)
        last_error = f"{url} -> no media id in response: {json.dumps(data)[:300]}"
    sys.exit(f"Media upload failed for {path.name}: {last_error}")


def post_tweet(text: str, reply_to: str | None, media_ids: list[str] | None = None) -> str:
    payload: dict = {"text": text}
    if reply_to:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to}
    if media_ids:
        payload["media"] = {"media_ids": media_ids}
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
        hint = ""
        if err.code == 402:
            hint = "\nYour X developer account has no posting credits. Nothing after this tweet was posted.\nPost the remaining tweets by hand as replies (dry run prints them), or add credits in the developer console."
        sys.exit(f"X API refused tweet ({err.code}): {detail}{hint}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Post an X thread from a text file.")
    parser.add_argument("thread_file", type=Path)
    parser.add_argument("--send", action="store_true", help="actually post (default: dry run)")
    parser.add_argument("--delay", type=float, default=2.0, help="seconds between tweets")
    args = parser.parse_args()

    load_env_file()
    tweets, media = read_thread(args.thread_file)
    if not tweets:
        sys.exit("No tweets found (separate tweets with a line containing only ---).")

    problems = []
    for i, tweet in enumerate(tweets, 1):
        if display_length(tweet) > TWEET_LIMIT:
            problems.append(f"tweet {i} is {display_length(tweet)} chars (limit {TWEET_LIMIT})")
        problems += [f"tweet {i}: {p}" for p in check_media(media[i - 1])]
    for problem in problems:
        print(f"  !! {problem}")
    if problems:
        sys.exit("Fix the problems above, then re-run.")

    for i, tweet in enumerate(tweets, 1):
        print(f"\n--- tweet {i}/{len(tweets)} ({display_length(tweet)} chars) ---")
        print(tweet)
        for path in media[i - 1]:
            print(f"  [attachment] {path.name} ({path.stat().st_size // 1024} KB)")

    if not args.send:
        print(f"\nDry run only. Re-run with --send to post {len(tweets)} tweets.")
        return

    reply_to = None
    for i, tweet in enumerate(tweets, 1):
        media_ids = [upload_media(path) for path in media[i - 1]]
        reply_to = post_tweet(tweet, reply_to, media_ids)
        print(f"posted {i}/{len(tweets)}: https://x.com/i/web/status/{reply_to}")
        if i < len(tweets):
            time.sleep(args.delay)
    print("\nThread posted. Pin the first tweet from the X app if it's the launch thread.")


if __name__ == "__main__":
    main()
