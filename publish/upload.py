"""Step 6 (optional): publish out/video.mp4 to TikTok / Reels / Shorts.

Uses upload-post.com API. Requires:
  - UPLOAD_POST_API_KEY  in .env / SSM
  - UPLOAD_POST_USER     in .env / SSM  (managed-user profile name, e.g. "familypencils")

Usage:
  python publish/upload.py --platforms tiktok youtube instagram
  python publish/upload.py --platforms tiktok   # single platform test
"""
from __future__ import annotations
import sys
import json
import argparse
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
import config  # noqa: E402
import requests  # noqa: E402

API = "https://api.upload-post.com/api/upload"
HEADERS = {
    "Authorization": "",          # set at runtime
    "User-Agent": "upload-post-python-client/2.0.0",
    "X-Upload-Post-Source": "pip",
}


def build_caption(manifest: dict) -> str:
    parts = [manifest.get("title", "").strip()]
    desc = manifest.get("description", "").strip()
    if desc and desc != manifest.get("title", "").strip():
        parts.append(desc)
    affiliate = os.getenv("AFFILIATE_LINK", "").strip()
    cta = os.getenv("AFFILIATE_CTA", "👇").strip()
    if affiliate:
        parts.append(f"{cta} {affiliate}")
    tags = " ".join(manifest.get("hashtags", []))
    if tags:
        parts.append(tags)
    return "\n\n".join(p for p in parts if p)


def publish(platforms: list[str]) -> dict:
    key = os.getenv("UPLOAD_POST_API_KEY", "")
    if not key:
        raise SystemExit("UPLOAD_POST_API_KEY not set (.env or SSM)")

    user = os.getenv("UPLOAD_POST_USER", "")
    if not user:
        raise SystemExit("UPLOAD_POST_USER not set (.env or SSM) — set to your upload-post profile name, e.g. 'familypencils'")

    manifest = json.loads((config.OUT / "manifest.json").read_text(encoding="utf-8"))
    video = config.OUT / "video.mp4"
    caption = build_caption(manifest)

    headers = {**HEADERS, "Authorization": f"Apikey {key}"}

    data = [("user", user), ("title", caption)]
    for p in platforms:
        data.append(("platform[]", p))

    with open(video, "rb") as f:
        r = requests.post(
            API,
            headers=headers,
            data=data,
            files=[("video", (video.name, f, "video/mp4"))],
            timeout=300,
        )

    try:
        body = r.json()
    except Exception:
        body = r.text
    print(f"[publish] {platforms} ({r.status_code}): {body}")
    r.raise_for_status()
    return body


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--platforms", nargs="+",
                    default=["tiktok", "youtube", "instagram"])
    args = ap.parse_args()
    publish(args.platforms)


if __name__ == "__main__":
    main()
