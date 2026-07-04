"""Çizgi film bölümünü beat sınırlarından Part 1/2/… shortlarına böler.

out/cartoon_overlay_props.json'daki beat zamanlarını kullanır; her parçayı
kendi başlık kartı ("… — Part N") ve kapanış kartıyla Remotion'da render eder.
Kesimler her zaman sahne (beat) sınırındadır, cümle ortasında kesilmez.

Kullanım:
  python pipeline/split_cartoon.py --parts 2
  python pipeline/split_cartoon.py --target-seconds 75   # parça başına hedef süre
"""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path

import config


def group_beats(beats: list[dict], n_parts: int) -> list[list[dict]]:
    """Beat'leri toplam süreye göre dengeli n gruba böl (sınırlar beat arası)."""
    total = beats[-1]["endFrame"]
    target = total / n_parts
    parts: list[list[dict]] = [[]]
    for b in beats:
        cur = parts[-1]
        if cur and len(parts) < n_parts and b["endFrame"] > len(parts) * target:
            parts.append([b])
        else:
            cur.append(b)
    return [p for p in parts if p]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--props", default=str(config.OUT / "cartoon_overlay_props.json"))
    ap.add_argument("--parts", type=int, default=0)
    ap.add_argument("--target-seconds", type=float, default=0)
    ap.add_argument("--portrait", action="store_true",
                    help="16:9 masterdan 9:16 short kes (ortadan kırpar)")
    args = ap.parse_args()

    data = json.loads(Path(args.props).read_text(encoding="utf-8"))["data"]
    beats = data["beats"]
    fps = data["fps"]
    total_s = data["totalDurationFrames"] / fps

    n_parts = args.parts or max(1, round(total_s / args.target_seconds)) if (args.parts or args.target_seconds) else 2
    parts = group_beats(beats, n_parts)
    print(f"{total_s:.0f} sn bölüm → {len(parts)} parça")

    renderer = config.ROOT / "renderer"
    outputs = []
    for pi, part in enumerate(parts, start=1):
        start = part[0]["startFrame"]
        end = part[-1]["endFrame"]
        shifted = [{**b,
                    "startFrame": b["startFrame"] - start,
                    "endFrame": b["endFrame"] - start,
                    "words": [{**w, "start": w["start"] - start / fps,
                               "end": w["end"] - start / fps} for w in b["words"]]}
                   for b in part]
        music = [{**m,
                  "startFrame": max(0, m["startFrame"] - start),
                  "endFrame": min(end - start, m["endFrame"] - start)}
                 for m in data.get("music", [])
                 if m["endFrame"] > start and m["startFrame"] < end]
        pdata = {**data,
                 "title": f"{data['title']} — Part {pi}/{len(parts)}",
                 "totalDurationFrames": end - start,
                 "startFrom": start,
                 "beats": shifted,
                 "music": music}
        if args.portrait:
            pdata["width"], pdata["height"] = 1080, 1920
        props = config.OUT / f"cartoon_part_{pi}_props.json"
        props.write_text(json.dumps({"data": pdata}, ensure_ascii=False), encoding="utf-8")

        out_mp4 = config.OUT / f"cartoon_part_{pi}.mp4"
        print(f"  Part {pi}: {(end - start) / fps:.0f} sn render ediliyor…")
        subprocess.run(
            ["npx", "remotion", "render", "CartoonOverlay", str(out_mp4),
             f"--props={props}", "--public-dir=../"],
            cwd=renderer, check=True, capture_output=True)
        outputs.append(out_mp4)
        print(f"  Part {pi} → {out_mp4.name}")

    print("\nParçalar hazır:")
    for o in outputs:
        print(f"  {o}")


if __name__ == "__main__":
    main()
