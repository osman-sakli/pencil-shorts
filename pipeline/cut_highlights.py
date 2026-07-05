"""Bölümden 15-30 sn'lik dikey highlight klipleri keser (akşam yayını için).

Beat aralıklarını alır, her aralığı altyazılı + başlık kartlı dikey klip
olarak render eder. Kapanış kartı ("New part every morning 6 AM") CTA görevi
görür. Maliyet: $0 — var olan sahnelerden kesilir, Seedance çağrılmaz.

Kullanım:
  python pipeline/cut_highlights.py --ranges "9:10,22:23,41:42" \
      [--props out/cartoon_overlay_props.json] [--titles "Mira meets a star!,..."]
"""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path

import config


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--props", default=str(config.OUT / "cartoon_overlay_props.json"))
    ap.add_argument("--ranges", required=True,
                    help="beat aralıkları: '9:10,22:23' (dahil-dahil)")
    ap.add_argument("--titles", default="", help="virgüllü özel başlıklar (opsiyonel)")
    args = ap.parse_args()

    data = json.loads(Path(args.props).read_text(encoding="utf-8"))["data"]
    beats = data["beats"]
    fps = data["fps"]
    titles = [t.strip() for t in args.titles.split(",")] if args.titles else []

    renderer = config.ROOT / "renderer"
    outputs = []
    for hi, rng in enumerate([r.strip() for r in args.ranges.split(",")], start=1):
        a, b = (int(x) for x in rng.split(":"))
        part = beats[a:b + 1]
        start = part[0]["startFrame"]
        end = part[-1]["endFrame"]
        shifted = [{**bt,
                    "startFrame": bt["startFrame"] - start,
                    "endFrame": bt["endFrame"] - start,
                    "words": [{**w, "start": w["start"] - start / fps,
                               "end": w["end"] - start / fps} for w in bt["words"]]}
                   for bt in part]
        music = [{**m,
                  "startFrame": max(0, m["startFrame"] - start),
                  "endFrame": min(end - start, m["endFrame"] - start)}
                 for m in data.get("music", [])
                 if m["endFrame"] > start and m["startFrame"] < end]
        title = titles[hi - 1] if hi <= len(titles) else data["title"]
        pdata = {**data,
                 "title": title,
                 "totalDurationFrames": end - start,
                 "startFrom": start,
                 "beats": shifted,
                 "music": music,
                 "width": 1080, "height": 1920}
        props = config.OUT / f"highlight_{hi}_props.json"
        props.write_text(json.dumps({"data": pdata}, ensure_ascii=False), encoding="utf-8")

        out_mp4 = config.OUT / f"highlight_{hi}.mp4"
        print(f"  Highlight {hi} (beat {a}-{b}, {(end - start) / fps:.0f} sn) render ediliyor…")
        subprocess.run(
            ["npx", "remotion", "render", "CartoonOverlay", str(out_mp4),
             f"--props={props}", "--public-dir=../"],
            cwd=renderer, check=True, capture_output=True)
        outputs.append(out_mp4)
        print(f"  → {out_mp4.name}")

    print("\nHighlight'lar hazır:")
    for o in outputs:
        print(f"  {o}")


if __name__ == "__main__":
    main()
