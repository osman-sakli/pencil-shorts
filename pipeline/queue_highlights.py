"""Highlight kliplerini akşam (pm) slotuyla S3 kuyruğuna ekler.

Her highlight bir akşam 19:00'da TikTok+IG+FB'ye gider (YouTube hariç —
kanal temiz kalsın). Metadata büyüme odaklı: merak kancası + profil CTA.

Kullanım:
  python pipeline/queue_highlights.py --script examples/episode3_little_star.json \
      --files out/highlight_1.mp4,out/highlight_2.mp4 \
      --hooks "Mira meets a star! 🥹,Biscuit found something GLOWING 😱" \
      [--start-date 2026-07-05]
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
from pathlib import Path

import boto3

import config

BUCKET = "pencil-shorts-parts-339712706640"
QUEUE_KEY = "queue.json"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--files", required=True, help="virgüllü highlight mp4 listesi")
    ap.add_argument("--hooks", default="", help="virgüllü kanca başlıkları")
    ap.add_argument("--start-date", default=None)
    ap.add_argument("--platforms", default="tiktok,instagram,facebook")
    args = ap.parse_args()

    script = json.loads(Path(args.script).read_text(encoding="utf-8"))
    files = [Path(f.strip()) for f in args.files.split(",")]
    hooks = [h.strip() for h in args.hooks.split(",")] if args.hooks else []
    start = (dt.date.fromisoformat(args.start_date) if args.start_date
             else dt.date.today() + dt.timedelta(days=1))

    s3 = boto3.client("s3")
    try:
        queue = json.loads(s3.get_object(Bucket=BUCKET, Key=QUEUE_KEY)["Body"].read())
    except s3.exceptions.NoSuchKey:
        queue = []

    slug = Path(args.script).stem
    title_clean = script["title"].rstrip("! ").split("!")[0]

    for i, f in enumerate(files, start=1):
        assert f.exists(), f"yok: {f}"
        key = f"highlights/{slug}_{i}.mp4"
        s3.upload_file(str(f), BUCKET, key)
        day = (start + dt.timedelta(days=i - 1)).isoformat()
        hook = hooks[i - 1] if i <= len(hooks) else f"{title_clean} 🥹"
        cta = "Full story on our profile! Watch every part ⭐"

        queue.append({
            "key": key,
            "slot": "pm",
            "title": hook,
            "description": f"{cta}\n#kidsoftiktok #cartoonsforkids #penfamily #cutebaby",
            "hashtags": ["kidsoftiktok", "cartoonsforkids", "penfamily"],
            "platform_meta": {
                "instagram": {"description": (f"{hook}\n{cta}\n"
                              "#kidsreels #babiesofinstagram #animation #kidscartoon "
                              "#toddlermom #penfamily #cutevideos")},
                "facebook": {"description": f"{hook} 🥹 {cta}\nTag a parent who needs this! 👇"},
            },
            "platforms": args.platforms.split(","),
            "not_before": day,
            "published_at": None,
        })
        print(f"  {f.name} → {key} ({day} akşamı)")

    s3.put_object(Bucket=BUCKET, Key=QUEUE_KEY,
                  Body=json.dumps(queue, ensure_ascii=False, indent=2).encode())
    print(f"Kuyruk güncellendi ({len(files)} highlight, pm slotu).")


if __name__ == "__main__":
    main()
