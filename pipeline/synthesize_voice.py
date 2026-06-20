"""Step 2: synthesize per-beat audio.

For each beat:
  - generate wav via Kokoro (default), EdgeTTS, or ElevenLabs
  - capture word boundaries (for subtitle timing) -> out/beat_N.words.json
  - convert to 16kHz mono PCM wav (Rhubarb requirement) -> out/beat_N.wav

TTS_PROVIDER options:
  kokoro      - Kokoro TTS (natural US English, CPU-friendly, default)
  edge        - EdgeTTS (free, faster, slightly robotic)
  elevenlabs  - ElevenLabs (premium quality, requires API key)
"""
from __future__ import annotations
import json
import asyncio
import subprocess
import numpy as np
from pathlib import Path
import edge_tts
import config


# ── Kokoro ────────────────────────────────────────────────────────────────────

def _kokoro(text: str, voice: str, wav_path: Path) -> list[dict]:
    """Synthesize with Kokoro TTS at 24kHz, save directly to wav_path."""
    from kokoro import KPipeline
    pipe = KPipeline(lang_code='a')  # 'a' = American English
    chunks = []
    for _, _, audio in pipe(text, voice=voice, speed=1.1):
        chunks.append(audio)
    audio = np.concatenate(chunks)
    import soundfile as sf
    sf.write(str(wav_path), audio, 24000)
    return []  # word timings via Rhubarb


# ── EdgeTTS ───────────────────────────────────────────────────────────────────

async def _edge_tts(text: str, voice: str, mp3_path: Path,
                    rate: str = "+0%", pitch: str = "+0Hz") -> list[dict]:
    import asyncio as _aio
    for attempt in range(4):
        try:
            communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
            words: list[dict] = []
            with open(mp3_path, "wb") as f:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        start = chunk["offset"] / 1e7
                        dur = chunk["duration"] / 1e7
                        words.append({"word": chunk["text"], "start": start, "end": start + dur})
            if mp3_path.stat().st_size > 0:
                return words
            raise RuntimeError("empty audio file")
        except Exception as exc:
            if attempt == 3:
                raise
            wait = 2 ** attempt  # 1, 2, 4 saniye
            await _aio.sleep(wait)
    return []


# ── ElevenLabs ────────────────────────────────────────────────────────────────

def _elevenlabs(text: str, voice: str, mp3_path: Path) -> list[dict]:
    import httpx
    r = httpx.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice}",
        headers={"xi-api-key": config.ELEVENLABS_API_KEY},
        json={"text": text, "model_id": "eleven_multilingual_v2"},
        timeout=60,
    )
    r.raise_for_status()
    mp3_path.write_bytes(r.content)
    return []


# ── Shared ffmpeg resampler ────────────────────────────────────────────────────

def _to_wav_16k(src: Path, dst: Path) -> None:
    """Resample any audio file to 16kHz mono PCM WAV for Rhubarb."""
    subprocess.run(
        [config.FFMPEG, "-y", "-i", str(src),
         "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(dst)],
        check=True, capture_output=True,
    )


# ── Orchestrator ──────────────────────────────────────────────────────────────

def synthesize(script: dict) -> None:
    provider = config.TTS_PROVIDER

    for i, beat in enumerate(script["beats"]):
        char = config.CHARACTERS[beat["character"]]
        wav_16k = config.OUT / f"beat_{i}.wav"

        if provider == "kokoro":
            voice = char["voice"]
            wav_24k = config.OUT / f"beat_{i}_24k.wav"
            words = _kokoro(beat["text"], voice, wav_24k)
            _to_wav_16k(wav_24k, wav_16k)
            wav_24k.unlink(missing_ok=True)

        elif provider == "elevenlabs":
            voice = char["voice"]
            mp3 = config.OUT / f"beat_{i}.mp3"
            words = _elevenlabs(beat["text"], voice, mp3)
            _to_wav_16k(mp3, wav_16k)

        else:  # edge (default fallback)
            voice = char.get("voice_edge", char["voice"])
            mp3 = config.OUT / f"beat_{i}.mp3"
            rate = char.get("voice_rate", "+0%")
            pitch = char.get("voice_pitch", "+0Hz")
            words = asyncio.run(_edge_tts(beat["text"], voice, mp3, rate=rate, pitch=pitch))
            # Keep original mp3 for high-quality audio mix; convert a copy to 16kHz for Rhubarb
            mp3_copy = config.OUT / f"beat_{i}_hq.mp3"
            import shutil; shutil.copy2(mp3, mp3_copy)
            _to_wav_16k(mp3, wav_16k)
            # Restore original mp3 so build_manifest can use it
            mp3_copy.rename(mp3)

        (config.OUT / f"beat_{i}.words.json").write_text(
            json.dumps(words, ensure_ascii=False), encoding="utf-8"
        )
        print(f"[tts] beat {i} ({beat['character']}) -> {wav_16k.name} ({len(words)} kelime)")


def main() -> None:
    script = json.loads((config.OUT / "script.json").read_text(encoding="utf-8"))
    synthesize(script)


if __name__ == "__main__":
    main()
