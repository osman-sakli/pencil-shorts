"""Step 4: assemble everything into out/manifest.json + out/audio_full.wav.

- Concatenates per-beat wavs with silence gaps for pacing.
- Offsets each beat's mouth cues and word timings to the global timeline.
- Computes frame in/out points for each beat.
- Emits a self-contained manifest consumed by the Remotion renderer.

All asset paths are relative to the repo root (Remotion is run with --public-dir=../).
"""
from __future__ import annotations
import json
from pathlib import Path
from pydub import AudioSegment
import config


def _round_f(seconds: float) -> int:
    return round(seconds * config.FPS)


def _assign_positions(beats: list[dict]) -> dict[str, str]:
    """Alternate left/right per character so they never share a side."""
    mapping: dict[str, str] = {}
    for b in beats:
        cid = b["character"]
        if cid not in mapping:
            # Strict alternation: odd-indexed chars go right, even go left
            mapping[cid] = "right" if len(mapping) % 2 == 1 else "left"
    return mapping


def build(script: dict) -> dict:
    beats_out: list[dict] = []
    full_audio = AudioSegment.silent(duration=0)
    cursor_s = 0.0
    positions = _assign_positions(script["beats"])

    opening_bg = script.get("background", config.BACKGROUNDS[0])

    for i, beat in enumerate(script["beats"]):
        # Use original high-quality mp3 for final audio if available.
        # The 16kHz wav is only for Rhubarb lip-sync — never for the mix.
        mp3_path = config.OUT / f"beat_{i}.mp3"
        wav_path = config.OUT / f"beat_{i}.wav"
        if mp3_path.exists():
            seg = AudioSegment.from_mp3(mp3_path)
        else:
            seg = AudioSegment.from_wav(wav_path)
        dur_s = len(seg) / 1000.0
        audio_start = cursor_s

        cues = json.loads((config.OUT / f"beat_{i}.cues.json").read_text())["mouthCues"]
        words = json.loads((config.OUT / f"beat_{i}.words.json").read_text(encoding="utf-8"))

        beats_out.append({
            "character": beat["character"],
            "text": beat["text"],
            "emotion": beat.get("emotion", "neutral"),
            "position": positions[beat["character"]],
            "background": beat.get("background", opening_bg),
            "startFrame": _round_f(audio_start),
            "endFrame": _round_f(audio_start + dur_s),
            # times shifted to global timeline (seconds)
            "mouthCues": [
                {"start": c["start"] + audio_start,
                 "end": c["end"] + audio_start,
                 "value": c["value"]}
                for c in cues
            ],
            "words": [
                {"word": w["word"],
                 "start": w["start"] + audio_start,
                 "end": w["end"] + audio_start}
                for w in words
            ],
        })

        full_audio += seg + AudioSegment.silent(duration=int(config.BEAT_GAP_S * 1000))
        cursor_s += dur_s + config.BEAT_GAP_S

    total_s = cursor_s + config.TAIL_PAD_S
    audio_path = config.OUT / "audio_full.wav"
    full_audio.export(audio_path, format="wav")

    # only the characters actually used (metadata only; visuals are code-drawn)
    used = {b["character"] for b in script["beats"]}
    chars = {
        cid: {
            "name": c["name"],
            "color": c["color"],
            "scale": c.get("scale", 1.0),
        }
        for cid, c in config.CHARACTERS.items() if cid in used
    }

    return {
        "title": script["title"],
        "fps": config.FPS,
        "width": config.WIDTH,
        "height": config.HEIGHT,
        "audio": "out/audio_full.wav",
        "background": "",  # renderer draws a code background; label kept in script only
        "totalDurationFrames": _round_f(total_s),
        "characters": chars,
        "beats": beats_out,
        "description": script.get("description", script.get("title", "")),
        "hashtags": script.get("hashtags", []),
    }


def main() -> None:
    script = json.loads((config.OUT / "script.json").read_text(encoding="utf-8"))
    manifest = build(script)
    out = config.OUT / "manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[manifest] {manifest['totalDurationFrames']} frame "
          f"({manifest['totalDurationFrames']/config.FPS:.1f}s) -> {out}")


if __name__ == "__main__":
    main()
