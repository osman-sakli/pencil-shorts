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
    ap.add_argument("--platforms", default="tiktok,instagram,facebook")
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
                 if i > 1 else f"Part 1 of {args.parts}! New part every morning! ⏰\n\n")
        queue.append({
            "key": key,
            "title": f"{script['title']} — Part {i}/{args.parts}",
            "description": extra + script.get("description", ""),
            "hashtags": script.get("hashtags", []) + [f"part{i}"],
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
