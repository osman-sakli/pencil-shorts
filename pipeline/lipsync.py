"""Step 3: run Rhubarb lip-sync on each beat wav.

Produces out/beat_N.cues.json:
{"mouthCues": [{"start": 0.0, "end": 0.12, "value": "X"}, ...]}

Rhubarb mouth shapes: A B C D E F G H (talking) + X (rest/closed).
For Turkish use the phonetic recognizer (no dialog text needed).
"""
from __future__ import annotations
import json
import subprocess
from pathlib import Path
import config


def run_rhubarb(wav_path: Path, out_json: Path) -> dict:
    cmd = [
        config.RHUBARB,
        "-f", "json",
        "--recognizer", config.RHUBARB_RECOGNIZER,
        "-o", str(out_json),
        str(wav_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return json.loads(out_json.read_text(encoding="utf-8"))


def lipsync(script: dict) -> None:
    for i in range(len(script["beats"])):
        wav = config.OUT / f"beat_{i}.wav"
        out_json = config.OUT / f"beat_{i}.cues.json"
        data = run_rhubarb(wav, out_json)
        cues = data.get("mouthCues", [])
        print(f"[lipsync] beat {i} -> {len(cues)} ağız şekli")


def main() -> None:
    script = json.loads((config.OUT / "script.json").read_text(encoding="utf-8"))
    lipsync(script)


if __name__ == "__main__":
    main()
