"""Bölüm part'ını short platformlarına yayınlar (cron-güvenli, çift yayın korumalı).

Kullanım: python3 pipeline/publish_part.py --script examples/treasure_map.json --part 2 --of 2
Marker dosyası (out/.published_<slug>_partN) varsa hiçbir şey yapmaz.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import config

sys.path.insert(0, str(config.ROOT / "publish"))
import upload


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--part", type=int, required=True)
    ap.add_argument("--of", type=int, required=True)
    ap.add_argument("--platforms", default="tiktok,instagram,facebook,youtube")
    args = ap.parse_args()

    script = json.loads((config.ROOT / args.script).read_text(encoding="utf-8"))
    slug = "".join(c for c in script["title"].lower() if c.isalnum())[:24]
    marker = config.OUT / f".published_{slug}_part{args.part}"
    if marker.exists():
        print(f"Part {args.part} zaten yayınlanmış ({marker.name}), atlanıyor.")
        return

    video = config.OUT / f"cartoon_part_{args.part}.mp4"
    if not video.exists():
        sys.exit(f"{video} yok!")

    tag = f" — Part {args.part}/{args.of}"
    extra = (f"Part {args.part} of {args.of}! The adventure continues! 🎬\n\n"
             if args.part > 1 else
             f"Part 1 of {args.of}! Part 2 tomorrow! ⏰\n\n")
    meta = {"title": script["title"] + tag,
            "description": extra + script.get("description", ""),
            "hashtags": script.get("hashtags", []) + [f"part{args.part}"]}

    results = upload.publish(args.platforms.split(","),
                             video_path=video, manifest_data=meta)
    marker.write_text(json.dumps(str(results), ensure_ascii=False), encoding="utf-8")
    print(f"Part {args.part} yayınlandı, marker yazıldı.")


if __name__ == "__main__":
    main()
