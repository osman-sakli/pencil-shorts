"""Step 6 (optional): publish out/video.mp4 to TikTok / Reels / Shorts.

Uses upload-post.com API. Requires:
  - UPLOAD_POST_API_KEY  in .env / SSM
  - UPLOAD_POST_USER     in .env / SSM  (managed-user profile name, e.g. "familypencils")

Usage:
  python publish/upload.py --platforms tiktok youtube instagram facebook
  python publish/upload.py --platforms tiktok   # single platform test
"""
from __future__ import annotations
import sys
import json
import argparse
import os
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
import config  # noqa: E402
import requests  # noqa: E402

API = "https://api.upload-post.com/api/upload"
STATUS_API = "https://api.upload-post.com/api/uploadposts/status"
HEADERS = {
    "Authorization": "",
    "User-Agent": "upload-post-python-client/2.0.0",
    "X-Upload-Post-Source": "pip",
}

# TikTok retry config
TIKTOK_RETRIES = 4           # max retry attempts
TIKTOK_RETRY_WAIT = 90 * 60  # 90 minutes between retries


def build_texts(manifest: dict) -> tuple[str, str]:
    title = manifest.get("title", "").strip()[:100]
    parts = []
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
    description = "\n\n".join(p for p in parts if p)
    return title, description


def _post(platforms: list[str], key: str, user: str,
          manifest: dict, video: Path) -> dict:
    headers = {**HEADERS, "Authorization": f"Apikey {key}"}
    title, description = build_texts(manifest)
    data = [("user", user), ("title", title), ("description", description)]
    for p in platforms:
        data.append(("platform[]", p))
    with open(video, "rb") as f:
        r = requests.post(
            API, headers=headers, data=data,
            files=[("video", (video.name, f, "video/mp4"))],
            timeout=300,
        )
    r.raise_for_status()
    return r.json()


def _check_status(request_id: str, key: str) -> list[dict]:
    headers = {**HEADERS, "Authorization": f"Apikey {key}"}
    for _ in range(12):  # poll up to 2 minutes
        r = requests.get(f"{STATUS_API}?request_id={request_id}", headers=headers)
        r.raise_for_status()
        data = r.json()
        if data.get("status") == "completed":
            return data.get("results", [])
        time.sleep(10)
    return []


def _is_tiktok_cap_error(result: dict) -> bool:
    err = result.get("error_message", "") or ""
    return "temporary restriction" in err.lower() or "active user cap" in err.lower()


def publish(platforms: list[str], *,
            video_path: Path | None = None,
            manifest_data: dict | None = None) -> dict:
    """Upload a video to one or more platforms.

    video_path    — override the default out/video.mp4 (use for long episodes)
    manifest_data — override metadata read from out/manifest.json
    """
    key = os.getenv("UPLOAD_POST_API_KEY", "")
    if not key:
        raise SystemExit("UPLOAD_POST_API_KEY not set (.env or SSM)")
    user = os.getenv("UPLOAD_POST_USER", "")
    if not user:
        raise SystemExit("UPLOAD_POST_USER not set (.env or SSM)")

    manifest = manifest_data or json.loads(
        (config.OUT / "manifest.json").read_text(encoding="utf-8"))
    video = Path(video_path) if video_path else config.OUT / "video.mp4"

    # Upload all platforms in one shot
    body = _post(platforms, key, user, manifest, video)
    request_id = body.get("request_id", "")
    print(f"[publish] İstek gönderildi → request_id={request_id}")

    # Wait for processing
    time.sleep(20)
    results = _check_status(request_id, key)

    for res in results:
        platform = res["platform"]
        if res["success"]:
            print(f"[publish] ✅ {platform}: {res.get('post_url')}")
        else:
            print(f"[publish] ❌ {platform}: {res.get('error_message','')[:80]}")

    # Retry TikTok separately if it hit the cap error
    tiktok_result = next((r for r in results if r["platform"] == "tiktok"), None)
    if "tiktok" in platforms and (not tiktok_result or not tiktok_result["success"]):
        _retry_tiktok(key, user, manifest, video, tiktok_result)

    return body


def _retry_tiktok(key: str, user: str, manifest: dict,
                  video: Path, last_result: dict | None) -> None:
    if last_result and not _is_tiktok_cap_error(last_result):
        print("[tiktok] Kalıcı hata — retry yapılmıyor.")
        return

    for attempt in range(1, TIKTOK_RETRIES + 1):
        wait_min = TIKTOK_RETRY_WAIT // 60
        print(f"[tiktok] Geçici kota hatası. {wait_min} dakika sonra tekrar denenecek "
              f"(deneme {attempt}/{TIKTOK_RETRIES})...")
        time.sleep(TIKTOK_RETRY_WAIT)

        try:
            body = _post(["tiktok"], key, user, manifest, video)
            request_id = body.get("request_id", "")
            time.sleep(20)
            results = _check_status(request_id, key)
            tiktok = next((r for r in results if r["platform"] == "tiktok"), None)

            if tiktok and tiktok["success"]:
                print(f"[tiktok] ✅ Yüklendi: {tiktok.get('post_url')}")
                return
            elif tiktok and _is_tiktok_cap_error(tiktok):
                continue  # kota hâlâ aktif, tekrar bekle
            else:
                err = (tiktok or {}).get("error_message", "bilinmiyor")
                print(f"[tiktok] ❌ Farklı hata, durduruluyor: {err[:100]}")
                return
        except Exception as exc:
            print(f"[tiktok] ⚠️ Bağlantı hatası: {exc}")

    print("[tiktok] ❌ Tüm retry'lar tükendi. Elle yükleme gerekiyor.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--platforms", nargs="+",
                    default=["tiktok", "youtube", "instagram", "facebook"])
    ap.add_argument("--video", help="Path to video file (default: out/video.mp4)")
    args = ap.parse_args()
    publish(args.platforms, video_path=args.video)


if __name__ == "__main__":
    main()
