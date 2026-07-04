"""S3 kuyruğundan sıradaki bölüm parçasını yayınlar (ECS'te her sabah çalışır).

Kuyruk: s3://$QUEUE_BUCKET/queue.json
  [{"key": "parts/ep3_part_1.mp4", "title": "...", "description": "...",
    "hashtags": [...], "platforms": ["tiktok","instagram","facebook"],
    "not_before": "2026-07-05", "published_at": null}, ...]

Her çalıştırmada: tarihi gelmiş, yayınlanmamış İLK parçayı indirir, yayınlar,
queue.json'a yayın zamanını + linkleri yazar. Kuyruk boşsa sessizce çıkar.
"""
from __future__ import annotations
import datetime as dt
import json
import os
import sys
import tempfile
from pathlib import Path

import boto3

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "pipeline"))
import upload  # noqa: E402

BUCKET = os.getenv("QUEUE_BUCKET", "pencil-shorts-parts-339712706640")
QUEUE_KEY = "queue.json"


def main() -> None:
    s3 = boto3.client("s3")
    try:
        raw = s3.get_object(Bucket=BUCKET, Key=QUEUE_KEY)["Body"].read()
        queue = json.loads(raw)
    except s3.exceptions.NoSuchKey:
        print("Kuyruk yok (queue.json bulunamadı) — yapılacak iş yok.")
        return

    today = dt.date.today().isoformat()
    item = next((q for q in queue
                 if not q.get("published_at") and q.get("not_before", "") <= today),
                None)
    if item is None:
        print("Yayınlanacak parça yok (hepsi yayınlandı ya da tarihi gelmedi).")
        return

    print(f"Yayınlanıyor: {item['key']} → {item.get('platforms')}")
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f:
        s3.download_fileobj(BUCKET, item["key"], f)
        video = Path(f.name)

    default_meta = {"title": item["title"],
                    "description": item.get("description", ""),
                    "hashtags": item.get("hashtags", [])}
    platform_meta = item.get("platform_meta", {})

    all_results = {}
    for p in item.get("platforms", ["tiktok", "instagram", "facebook"]):
        meta = {**default_meta, **platform_meta.get(p, {})}
        try:
            all_results[p] = upload.publish([p], video_path=video, manifest_data=meta)
        except Exception as e:  # bir platform patlasa diğerleri devam etsin
            all_results[p] = f"HATA: {e}"
            print(f"  {p}: HATA {e}")

    item["published_at"] = dt.datetime.utcnow().isoformat() + "Z"
    item["results"] = str(all_results)
    s3.put_object(Bucket=BUCKET, Key=QUEUE_KEY,
                  Body=json.dumps(queue, ensure_ascii=False, indent=2).encode())
    print("Tamam — kuyruk güncellendi.")


if __name__ == "__main__":
    main()
