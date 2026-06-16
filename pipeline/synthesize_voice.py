"""Step 2: synthesize per-beat audio.

For each beat:
  - generate mp3 via EdgeTTS (or ElevenLabs)
  - capture word boundaries (for subtitle timing) -> out/beat_N.words.json
  - convert to 16kHz mono PCM wav (Rhubarb requirement) -> out/beat_N.wav
"""
from __future__ import annotations
import json
import asyncio
import subprocess
from pathlib import Path
import edge_tts
import config


async def _edge_tts(text: str, voice: str, mp3_path: Path) -> list[dict]:
    """Synthesize with EdgeTTS, returning word-boundary list (seconds)."""
    communicate = edge_tts.Communicate(text, voice)
    words: list[dict] = []
    with open(mp3_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                # offset/duration are in 100-nanosecond ticks
                start = chunk["offset"] / 1e7
                dur = chunk["duration"] / 1e7
                words.append({"word": chunk["text"], "start": start, "end": start + dur})
    return words


def _elevenlabs(text: str, voice: str, mp3_path: Path) -> list[dict]:
    import httpx
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    r = httpx.post(
        url,
        headers={"xi-api-key": config.ELEVENLABS_API_KEY},
        json={"text": text, "model_id": "eleven_multilingual_v2"},
        timeout=60,
    )
    r.raise_for_status()
    mp3_path.write_bytes(r.content)
    return []  # word timings come from Rhubarb fallback


def _to_wav(mp3_path: Path, wav_path: Path) -> None:
    subprocess.run(
        [config.FFMPEG, "-y", "-i", str(mp3_path),
         "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(wav_path)],
        check=True, capture_output=True,
    )


def synthesize(script: dict) -> None:
    for i, beat in enumerate(script["beats"]):
        char = config.CHARACTERS[beat["character"]]
        voice = char["voice"]
        mp3 = config.OUT / f"beat_{i}.mp3"
        wav = config.OUT / f"beat_{i}.wav"

        if config.TTS_PROVIDER == "elevenlabs":
            words = _elevenlabs(beat["text"], voice, mp3)
        else:
            words = asyncio.run(_edge_tts(beat["text"], voice, mp3))

        _to_wav(mp3, wav)
        (config.OUT / f"beat_{i}.words.json").write_text(
            json.dumps(words, ensure_ascii=False), encoding="utf-8"
        )
        print(f"[tts] beat {i} ({beat['character']}) -> {wav.name} ({len(words)} kelime)")


def main() -> None:
    script = json.loads((config.OUT / "script.json").read_text(encoding="utf-8"))
    synthesize(script)


if __name__ == "__main__":
    main()
