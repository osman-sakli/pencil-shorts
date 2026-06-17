"""Step 6 (optional): publish out/video.mp4 to TikTok / Reels / Shorts.

Uses upload-post.com API. Requires:
  - UPLOAD_POST_API_KEY  in .env / SSM
  - UPLOAD_POST_USERNAME per platform in .env / SSM
    e.g.  UPLOAD_POST_USERNAME_TIKTOK=@yourhandle
          UPLOAD_POST_USERNAME_YOUTUBE=@yourhandle
          UPLOAD_POST_USERNAME_INSTAGRAM=@yourhandle

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
import httpx   # noqa: E402

API = "https://api.upload-post.com/api/upload"

PLATFORM_USERNAME_ENVS = {
    "tiktok":    "UPLOAD_POST_USERNAME_TIKTOK",
    "youtube":   "UPLOAD_POST_USERNAME_YOUTUBE",
    "instagram": "UPLOAD_POST_USERNAME_INSTAGRAM",
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


def publish(platforms: list[str]) -> None:
    key = os.getenv("UPLOAD_POST_API_KEY", "")
    if not key:
        raise SystemExit("UPLOAD_POST_API_KEY not set (.env or SSM)")

    manifest = json.loads((config.OUT / "manifest.json").read_text(encoding="utf-8"))
    video = config.OUT / "video.mp4"
    caption = build_caption(manifest)

    results = {}
    for platform in platforms:
        username_env = PLATFORM_USERNAME_ENVS.get(platform)
        username = os.getenv(username_env, "") if username_env else ""
        if not username:
            print(f"[publish] SKIP {platform}: {username_env} not set")
            continue

        with open(video, "rb") as f:
            r = httpx.post(
                API,
                headers={"Authorization": f"Apikey {key}"},
                data={
                    "title": caption,
                    "platform[]": platform,
                    "username": username,
                },
                files={"video": (video.name, f, "video/mp4")},
                timeout=300,
            )
        try:
            body = r.json()
        except Exception:
            body = r.text
        print(f"[publish] {platform} ({r.status_code}): {body}")
        results[platform] = {"status": r.status_code, "body": body}
        r.raise_for_status()

    return results


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--platforms", nargs="+",
                    default=["tiktok", "youtube", "instagram"])
    args = ap.parse_args()
    publish(args.platforms)


if __name__ == "__main__":
    main()
