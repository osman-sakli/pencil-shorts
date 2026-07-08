"""Otomatik şarkı üretimi: sözler -> fal.ai DiffRhythm -> söylenmiş MP3.

Suno'ya gerek YOK. Sözleri (LRC zaman damgalı ya da düz) verirsin, DiffRhythm
söyleyerek şarkıyı üretir. ~$0.001/sn (80sn ≈ $0.08).

LRC formatı (satır başına zaman damgası, DiffRhythm bunu ister):
  [00:00.00]Twinkle twinkle little star
  [00:04.00]Up so high that's where you are

Kullanım:
  python pipeline/generate_song_fal.py --lyrics examples/songs/twinkle.lrc \
      --out out/nursery/twinkle_fal.mp3 [--ref <stil_referans_mp3_url>]
  # düz sözlerden otomatik LRC (eşit dağıt):
  python pipeline/generate_song_fal.py --plain examples/songs/twinkle.txt \
      --seconds 80 --out out/nursery/twinkle_fal.mp3
"""
from __future__ import annotations
import argparse
import os
import sys
import urllib.request
from pathlib import Path

ENDPOINT = "fal-ai/diffrhythm"


def plain_to_lrc(lines: list[str], seconds: float) -> str:
    """Düz söz satırlarını süreye eşit yayıp LRC zaman damgası ekler."""
    lines = [l.strip() for l in lines if l.strip()]
    if not lines:
        return ""
    step = seconds / len(lines)
    out = []
    for i, line in enumerate(lines):
        t = i * step
        mm, ss = int(t // 60), t % 60
        out.append(f"[{mm:02d}:{ss:05.2f}]{line}")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lyrics", help="LRC zaman damgalı sözler dosyası")
    ap.add_argument("--plain", help="düz sözler (otomatik LRC'ye çevrilir)")
    ap.add_argument("--seconds", type=float, default=80, help="--plain için hedef süre")
    ap.add_argument("--ref", default="", help="opsiyonel stil referans ses URL'si")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if not os.getenv("FAL_KEY"):
        sys.exit("FAL_KEY .env'de yok.")

    if args.lyrics:
        lrc = Path(args.lyrics).read_text(encoding="utf-8")
    elif args.plain:
        lrc = plain_to_lrc(Path(args.plain).read_text(encoding="utf-8").splitlines(), args.seconds)
    else:
        sys.exit("--lyrics ya da --plain ver.")

    import fal_client
    arguments = {"lyrics": lrc}
    if args.ref:
        arguments["reference_audio_url"] = args.ref

    print(f"Şarkı üretiliyor (DiffRhythm)… {len(lrc.splitlines())} satır söz")
    try:
        result = fal_client.subscribe(ENDPOINT, arguments=arguments, with_logs=False)
    except Exception as e:
        # Şema alan adı sürümle değişebilir — ilk gerçek çalıştırmada doğrulanır
        sys.exit(f"fal hatası: {e}\n(Not: fal bakiyesi dolu mu? Şema alanları "
                 f"model sürümüyle değişebilir — hata mesajını kontrol et.)")

    audio_url = (result.get("audio", {}) or {}).get("url") or result.get("audio_url")
    if not audio_url:
        sys.exit(f"Beklenm/ audio url yok. Ham sonuç: {result}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(audio_url, out)
    print(f"Şarkı hazır → {out}")


if __name__ == "__main__":
    main()
