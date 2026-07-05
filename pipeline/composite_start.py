"""Sprite'ları boş sahne plakası üzerine dizip Seedance başlangıç karesi üretir.

Kimlik garantisi: ilk karede karakterler birebir bizim sprite'lar olur;
Seedance bu kareden animasyona devam eder (kayma ihtimali ciddi düşer).

Kullanım:
  python pipeline/composite_start.py --plate garden_night \
      --chars "mas:0.30:0.42,biscuit:0.52:0.16,twinkle:0.62:0.12" --out beat_8
  (format: id:x_oran:boy_oran — x soldan, boy kare yüksekliğine oran)
"""
from __future__ import annotations
import argparse
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

import config
import generate_cartoon_seedance as g

W, H = 1536, 1024  # 16:9'a yakın plaka boyutu (Seedance kırpar)
GROUND_Y = 0.88    # karakter tabanının dikey konumu (plaka oranı)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plate", required=True)
    ap.add_argument("--chars", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ground", type=float, default=GROUND_Y)
    args = ap.parse_args()

    plate = Image.open(config.OUT / "plates" / f"{args.plate}.png").convert("RGBA")
    plate = plate.resize((W, H))

    for spec in args.chars.split(","):
        cid, x_ratio, h_ratio = spec.strip().split(":")
        sprite = Image.open(g.sprite_path(cid, "neutral")).convert("RGBA")
        # sprite'lar koyu/şeffaf zeminli — kırp
        bbox = sprite.getbbox()
        sprite = sprite.crop(bbox)
        target_h = int(H * float(h_ratio))
        target_w = int(sprite.width * target_h / sprite.height)
        sprite = sprite.resize((target_w, target_h))
        # gece sahnesine uyum: hafif karart + soğuk ton
        sprite = ImageEnhance.Brightness(sprite).enhance(0.88)
        x = int(W * float(x_ratio)) - target_w // 2
        y = int(H * args.ground) - target_h
        # zemine yumuşak gölge
        shadow = Image.new("RGBA", (target_w, max(8, target_h // 10)), (0, 0, 0, 0))
        from PIL import ImageDraw
        d = ImageDraw.Draw(shadow)
        d.ellipse([0, 0, shadow.width, shadow.height], fill=(0, 0, 20, 110))
        shadow = shadow.filter(ImageFilter.GaussianBlur(6))
        plate.alpha_composite(shadow, (x, int(H * args.ground) - shadow.height // 2))
        plate.alpha_composite(sprite, (x, y))

    out_dir = config.OUT / "startframes"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{args.out}.png"
    plate.convert("RGB").save(out, quality=95)
    print(f"başlangıç karesi → {out}")


if __name__ == "__main__":
    main()
