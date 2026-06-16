"""Step 6 (optional): publish out/video.mp4 to TikTok / Reels / Shorts.

Uses upload-post.com (same approach as the openshorts project) so you don't
implement each platform's OAuth yourself. Set UPLOAD_POST_API_KEY in .env.

Usage:
  python publish/upload.py --platforms tiktok youtube instagram
"""
from __future__ import annotations
import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
import config  # noqa: E402
import httpx  # noqa: E402

API = "https://api.upload-post.com/api/upload"


def build_caption(manifest: dict) -> str:
    import os
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
    key = config.__dict__.get("UPLOAD_POST_API_KEY") or ""
    import os
    key = os.getenv("UPLOAD_POST_API_KEY", "")
    if not key:
        raise SystemExit("UPLOAD_POST_API_KEY tanımlı değil (.env)")

    manifest = json.loads((config.OUT / "manifest.json").read_text(encoding="utf-8"))
    video = config.OUT / "video.mp4"
    caption = build_caption(manifest)

    with open(video, "rb") as f:
        r = httpx.post(
            API,
            headers={"Authorization": f"Apikey {key}"},
            data={"title": caption, "platform[]": platforms},
            files={"video": (video.name, f, "video/mp4")},
            timeout=300,
        )
    r.raise_for_status()
    print(f"[publish] {platforms} -> {r.json()}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--platforms", nargs="+",
                    default=["tiktok", "youtube", "instagram"])
    args = ap.parse_args()
    publish(args.platforms)


if __name__ == "__main__":
    main()
