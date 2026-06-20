# Current Pipeline Review — The Pen Family

## Overview
Fully automated daily short-video pipeline. Runs end-to-end: idea → script → voice → lip-sync → render → upload.

## Pipeline Steps

### 1. Script Generation (`pipeline/generate_script.py`)
- **LLM:** Claude Haiku (`claude-haiku-4-5-20251001`)
- **Input:** Topic string (manual or auto-selected from `AUTO_TOPICS` list)
- **Output:** `out/script.json` — beats array with character, text, emotion, background per line
- **Format:** 17-20 beats, 140-180 words, 60-70 seconds target
- **Characters:** 10 total (oz, mas, bas, saf, sem, mira + eli, kit, rex, nib as guest characters)

### 2. Voice Synthesis (`pipeline/synthesize_voice.py`)
- **Provider:** EdgeTTS (Microsoft Azure free TTS)
- **Per character:** unique voice, rate, pitch settings from `characters.yaml`
- **Output:** `out/beat_N.mp3` (high quality) + `out/beat_N.wav` (16kHz for Rhubarb)
- **Word boundaries:** captured for subtitle timing → `out/beat_N.words.json`

### 3. Lip Sync (`pipeline/lipsync.py`)
- **Tool:** Rhubarb Lip Sync (phoneme-based)
- **Input:** 16kHz mono WAV per beat
- **Output:** `out/beat_N.cues.json` — mouth shape timeline (A-H + X shapes)

### 4. Manifest Build (`pipeline/build_manifest.py`)
- Concatenates all audio segments with silence gaps
- Assigns per-beat positions (left/right alternating)
- Uses per-beat background from script
- Output: `out/manifest.json` + `out/audio_full.wav`

### 5. Render (`renderer/` — Remotion / TypeScript / React)
- **Framework:** Remotion 4.x, 1080×1920 vertical, 30fps
- **Characters:** PNG sprites (`characters/sprites/*.png`) with spring animations
- **Backgrounds:** 8 illustrated scenes drawn in React/CSS (home, kitchen, bedroom, bathroom, school, park, shop, street) — zero copyright
- **Subtitles:** Word-by-word karaoke highlight with character color
- **Output:** `out/video.mp4`

### 6. Upload (`publish/upload.py`)
- **Service:** upload-post.com (profile: `familypencils`)
- **Platforms:** TikTok, YouTube, Instagram, Facebook
- **TikTok retry:** 4 attempts × 90 min for new account cap errors

## Assets
| Asset | Location | Format |
|-------|----------|--------|
| Character sprites | `characters/sprites/*.png` | PNG transparent |
| Character config | `characters.yaml` | YAML |
| Background scenes | `renderer/src/backgrounds.tsx` | React/TSX code |
| Voice settings | `characters.yaml` (voice_edge, voice_rate, voice_pitch) | YAML |

## What Can Be Reused for Long Videos
- ✅ All voice synthesis (same EdgeTTS per character)
- ✅ All lip sync (same Rhubarb)
- ✅ All character sprites and backgrounds
- ✅ Remotion renderer (just longer totalDurationFrames)
- ✅ Upload system
- ⚠️ Script generator needs new long-form mode
- ⚠️ Manifest builder needs multi-scene audio concatenation
