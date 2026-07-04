"""cartoon.mp4 üzerine altyazı/başlık/kapanış bindirmek için overlay props üretir.

Klip sürelerini out/cartoon/beat_N.norm.mp4'ten ölçer, kelime zamanlarını
beat_N.words.json'dan alıp mutlak zamana kaydırır.

Kullanım: python pipeline/build_cartoon_overlay.py --script examples/cookie_cartoon.json
Sonra:    cd renderer && npx remotion render CartoonOverlay ../out/cartoon_final.mp4 \
              --props=../out/cartoon_overlay_props.json --public-dir=../
"""
from __future__ import annotations
import argparse
import json
import subprocess
from pathlib import Path

import config

FPS = 30


def probe_frames(path: Path) -> int:
    out = subprocess.run(
        [config.FFMPEG.replace("ffmpeg", "ffprobe"), "-v", "error",
         "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True)
    return round(float(out.stdout.strip()) * FPS)


MUSIC_FILES = {"mystery": "assets/music/mystery.mp3",
               "happy": "assets/music/happy.mp3",
               "calm": "assets/music/calm.mp3",
               "adventure": "assets/music/adventure.mp3"}


def build_music_segments(beats_out: list[dict], moods: list[str]) -> list[dict]:
    """Ardışık aynı ruh halindeki beat'leri tek müzik segmentinde birleştir."""
    segs: list[dict] = []
    for b, mood in zip(beats_out, moods):
        src = MUSIC_FILES.get(mood, MUSIC_FILES["happy"])
        if segs and segs[-1]["src"] == src:
            segs[-1]["endFrame"] = b["endFrame"]
        else:
            segs.append({"src": src, "startFrame": b["startFrame"],
                         "endFrame": b["endFrame"]})
    return segs


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--video", default="out/cartoon.mp4")
    ap.add_argument("--aspect", default="9:16", choices=["9:16", "16:9"])
    args = ap.parse_args()

    script = json.loads(Path(args.script).read_text(encoding="utf-8"))
    beats_out = []
    moods = []
    cursor = 0
    for i, beat in enumerate(script["beats"]):
        clip = config.OUT / "cartoon" / f"beat_{i}.norm.mp4"
        if not clip.exists():
            print(f"beat {i}: klip yok, atlanıyor")
            continue
        frames = probe_frames(clip)
        words = json.loads((config.OUT / f"beat_{i}.words.json").read_text(encoding="utf-8"))
        t0 = cursor / FPS
        char = config.CHARACTERS[beat["character"]]
        beats_out.append({
            "startFrame": cursor,
            "endFrame": cursor + frames,
            "text": beat["text"],
            "words": [{"word": w["word"], "start": w["start"] + t0,
                       "end": w["end"] + t0} for w in words],
            "name": char.get("name", beat["character"]),
            "color": char.get("color", "#4488FF"),
        })
        moods.append(beat.get("music", script.get("music", "happy")))
        cursor += frames

    w, h = (1080, 1920) if args.aspect == "9:16" else (1920, 1080)
    data = {
        "videoSrc": args.video,
        "title": script.get("title", ""),
        "totalDurationFrames": cursor,
        "fps": FPS,
        "width": w,
        "height": h,
        "beats": beats_out,
        "music": build_music_segments(beats_out, moods),
    }
    props = config.OUT / "cartoon_overlay_props.json"
    props.write_text(json.dumps({"data": data}, ensure_ascii=False), encoding="utf-8")
    print(f"{len(beats_out)} beat, {cursor / FPS:.1f}s → {props}")


if __name__ == "__main__":
    main()
