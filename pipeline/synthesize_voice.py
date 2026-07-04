"""Step 2: synthesize per-beat audio.

For each beat:
  - generate wav via Kokoro (default), EdgeTTS, or ElevenLabs
  - capture word boundaries (for subtitle timing) -> out/beat_N.words.json
  - convert to 16kHz mono PCM wav (Rhubarb requirement) -> out/beat_N.wav

TTS_PROVIDER options:
  kokoro      - Kokoro TTS (natural US English, CPU-friendly, default)
  edge        - EdgeTTS (free, faster, slightly robotic)
  elevenlabs  - ElevenLabs (premium quality, requires API key)
  openai      - OpenAI gpt-4o-mini-tts (natural acted voices, emotion
                steerable via instructions; uses OPENAI_API_KEY)
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


# ── OpenAI TTS ────────────────────────────────────────────────────────────────

# Sahne duygusu → seslendirme talimatı eki
_EMOTION_HINT = {
    "happy": " Speak with delighted, giggly excitement.",
    "angry": " Speak with comic frustration, huffing.",
    "surprised": " Speak with gasping amazement.",
    "sad": " Speak softly, pouty and sniffly.",
}


def _openai_tts(text: str, voice: str, instructions: str, mp3_path: Path) -> list[dict]:
    import os
    import urllib.request
    key = os.getenv("OPENAI_API_KEY", "")
    if not key:
        raise SystemExit("OPENAI_API_KEY yok (.env)")
    req = urllib.request.Request(
        "https://api.openai.com/v1/audio/speech",
        data=json.dumps({
            "model": "gpt-4o-mini-tts", "voice": voice, "input": text,
            "instructions": instructions, "response_format": "mp3",
        }).encode(),
        headers={"Authorization": f"Bearer {key}",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        mp3_path.write_bytes(r.read())
    # Kelime zamanları: toplam süreye orantılı dağıtım (altyazı için yeterli)
    probe = subprocess.run(
        [config.FFMPEG.replace("ffmpeg", "ffprobe"), "-v", "error",
         "-show_entries", "format=duration", "-of", "csv=p=0", str(mp3_path)],
        capture_output=True, text=True)
    dur = float(probe.stdout.strip() or 1.0)
    return _words_from_sentence(text, 0.06, max(0.2, dur - 0.18))


# ── EdgeTTS ───────────────────────────────────────────────────────────────────

# Edge duygu modülasyonu: karakterin taban hız/perdesine sahne duygusu eklenir
_EDGE_EMOTION = {
    "happy":     (8, 15),    # (+rate%, +pitchHz) — cıvıl cıvıl
    "surprised": (12, 25),   # hızlı ve tiz — nefesi kesilmiş
    "angry":     (10, 8),    # hızlanmış, gergin
    "sad":       (-14, -15), # yavaş ve pes — buruk
}


def _edge_mod(base: str, delta: int, unit: str) -> str:
    """'+15%' + 8 -> '+23%' ; '+40Hz' + 25 -> '+65Hz'"""
    val = int(base.rstrip("%Hz").replace("+", "") or "0")
    total = val + delta
    return f"{'+' if total >= 0 else ''}{total}{unit}"

def _words_from_sentence(sent_text: str, sent_start: float, sent_dur: float) -> list[dict]:
    """Distribute word timing within a sentence proportionally by character count."""
    raw_words = sent_text.split()
    if not raw_words:
        return []
    char_counts = [max(1, len(w.strip(".,!?'\"()-"))) for w in raw_words]
    total_chars = sum(char_counts)
    words: list[dict] = []
    t = sent_start
    for w, cc in zip(raw_words, char_counts):
        word_dur = sent_dur * cc / total_chars
        words.append({"word": w, "start": t, "end": t + word_dur})
        t += word_dur
    return words


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
                        # edge-tts < 7.x: direct word boundaries
                        start = chunk["offset"] / 1e7
                        dur = chunk["duration"] / 1e7
                        words.append({"word": chunk["text"], "start": start, "end": start + dur})
                    elif chunk["type"] == "SentenceBoundary":
                        # edge-tts >= 7.x: sentence-level timing — distribute words proportionally
                        sent_start = chunk["offset"] / 1e7
                        sent_dur = chunk["duration"] / 1e7
                        words.extend(_words_from_sentence(chunk["text"], sent_start, sent_dur))
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

def synthesize(script: dict, provider: str | None = None) -> None:
    provider = provider or config.TTS_PROVIDER

    for i, beat in enumerate(script["beats"]):
        char = config.CHARACTERS[beat["character"]]
        wav_16k = config.OUT / f"beat_{i}.wav"
        # Karakter bazlı sağlayıcı: Osman'ın seçtiği sesler karışık kadro
        p = char.get("voice_provider", provider)

        if p == "openai":
            voice = char.get("voice_openai", "ash")
            instructions = char.get("voice_instructions",
                                    "Speak naturally for a children's cartoon.")
            instructions += _EMOTION_HINT.get(beat.get("emotion", ""), "")
            mp3 = config.OUT / f"beat_{i}.mp3"
            words = _openai_tts(beat["text"], voice, instructions, mp3)
            _to_wav_16k(mp3, wav_16k)

        elif provider == "kokoro":
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
            # Sahne duygusunu hız/perdeye işle (daha canlı okuma)
            d_rate, d_pitch = _EDGE_EMOTION.get(beat.get("emotion", ""), (0, 0))
            rate = _edge_mod(rate, d_rate, "%")
            pitch = _edge_mod(pitch, d_pitch, "Hz")
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
