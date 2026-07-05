"""Bölüm parçalarını S3 yayın kuyruğuna ekler (lokalde, bölüm bittikten sonra).

Kullanım:
  python3 pipeline/queue_parts.py --script examples/episode3_little_star.json \
      --parts 4 --start-date 2026-07-05
Her parça bir sonraki güne sıralanır (Part1 → start-date, Part2 → +1 gün...).
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
    ap.add_argument("--parts", type=int, required=True)
    ap.add_argument("--start-date", default=(dt.date.today() + dt.timedelta(days=1)).isoformat())
    ap.add_argument("--platforms", default="tiktok,instagram,facebook,youtube")
    args = ap.parse_args()

    script = json.loads((config.ROOT / args.script).read_text(encoding="utf-8"))
    slug = "".join(c for c in script["title"].lower() if c.isalnum())[:24]
    start = dt.date.fromisoformat(args.start_date)

    s3 = boto3.client("s3")
    try:
        queue = json.loads(s3.get_object(Bucket=BUCKET, Key=QUEUE_KEY)["Body"].read())
    except Exception:
        queue = []

    for i in range(1, args.parts + 1):
        video = config.OUT / f"cartoon_part_{i}.mp4"
        if not video.exists():
            raise SystemExit(f"{video} yok!")
        key = f"parts/{slug}_part_{i}.mp4"
        print(f"S3'e yükleniyor: {key} ({video.stat().st_size // 1024 // 1024} MB)")
        s3.upload_file(str(video), BUCKET, key)
        day = (start + dt.timedelta(days=i - 1)).isoformat()
        extra = (f"Part {i} of {args.parts}! The adventure continues! 🎬\n\n"
                 if i > 1 else f"Part 1 of {args.parts}! New part every morning 6 AM! ⏰\n\n")
        title_clean = script["title"].rstrip("! ").split("!")[0]
        base_tags = script.get("hashtags", [])

        # Platforma özel paketleme — her algoritmanın sevdiği format farklı
        platform_meta = {
            "tiktok": {
                "title": f"{title_clean} — Part {i} 🍿 wait for it...",
                "description": (f"Part {i}/{args.parts} ⏰ New part every morning at 6! "
                                f"Follow so you don't miss the ending! 🎬\n"
                                + " ".join(f"#{t}" for t in
                                           ["kidsoftiktok", "cartoonsforkids", "kidsvideos",
                                            "bedtimestories", "penfamily", f"part{i}"])),
            },
            "instagram": {
                "title": f"{script['title']} — Part {i}/{args.parts}",
                "description": (extra + script.get("description", "") + "\n"
                                + " ".join(f"#{t}" for t in base_tags +
                                           ["kidsreels", "toddleractivities", "animation",
                                            "kidscartoon", "familyfun", "penfamily"])),
            },
            "facebook": {
                "title": f"{script['title']} — Part {i}/{args.parts}",
                "description": (f"Which Pen Family member is your favorite? Tell us below! 👇\n\n"
                                + extra + script.get("description", "")),
            },
            "youtube": {
                "title": f"{title_clean} — Part {i}/{args.parts} ⭐",
                "description": (extra + script.get("description", "")
                                + "\n\nSubscribe for the full episode and daily parts! 🔔"
                                + "\n#shorts #kidscartoon #penfamily"),
                "hashtags": base_tags + ["shorts", f"part{i}"],
            },
        }

        queue.append({
            "key": key,
            "title": f"{script['title']} — Part {i}/{args.parts}",
            "description": extra + script.get("description", ""),
            "hashtags": base_tags + [f"part{i}"],
            "platform_meta": platform_meta,
            "platforms": args.platforms.split(","),
            "not_before": day,
            "published_at": None,
        })
        print(f"  kuyruğa eklendi → {day} sabahı")

    s3.put_object(Bucket=BUCKET, Key=QUEUE_KEY,
                  Body=json.dumps(queue, ensure_ascii=False, indent=2).encode())
    print(f"\nKuyruk güncellendi: toplam {len(queue)} kayıt")


if __name__ == "__main__":
    main()
