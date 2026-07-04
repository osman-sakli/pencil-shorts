"""Pilot: beat'leri Seedance 2.0 (fal.ai) ile gerçek video klibe çevirir.

Her beat için: karakter sprite'ı (@Image1) + sahne fotoğrafı (@Image2) +
EdgeTTS sesi (@Audio1) reference-to-video endpoint'ine gider; dönen klipler
ffmpeg ile birleştirilir.

Kullanım:
  python pipeline/generate_video_seedance.py                # ilk 3 beat, 480p
  python pipeline/generate_video_seedance.py --beats 5 --resolution 720p

Maliyet (fal.ai, token bazlı): 480p ≈ $0.135/sn, 720p ≈ $0.30/sn.
Pilot (3 beat × ~5sn, 480p) ≈ $2-3.
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import config

ENDPOINT = "bytedance/seedance-2.0/reference-to-video"
SEEDANCE_OUT = config.OUT / "seedance"

# Duyguya göre sprite'ı olan karakterler (renderer/src/CharacterSprite.tsx ile aynı)
AI_CHARS = {"oz", "mas", "bas", "saf", "sem", "mira", "biscuit", "mittens", "snip"}
VALID_EMOTIONS = {"neutral", "happy", "angry", "surprised", "sad"}

# Fotoğrafı olmayan sahneler en yakın gerçek mekânı kullanır (renderer ile aynı)
PHOTO_ALIAS = {"bathroom": "bedroom", "notebook": "office", "desk": "office",
               "pencilcase": "shop", "living_room": "home"}
PHOTO_SCENES = {"home", "kitchen", "bedroom", "park", "school", "shop", "street",
                "office", "library"}


def sprite_path(char: str, emotion: str) -> Path:
    if char in AI_CHARS:
        emo = emotion if emotion in VALID_EMOTIONS else "neutral"
        return config.ROOT / "characters" / "sprites" / f"{char}_{emo}.png"
    return config.ROOT / "characters" / "sprites" / f"{char}.png"


def photo_path(scene: str) -> Path:
    label = scene if scene in PHOTO_SCENES else PHOTO_ALIAS.get(scene, "home")
    return config.ROOT / "backgrounds" / "photos" / f"{label}.jpg"


def build_prompt(beat: dict, char_name: str) -> str:
    emotion = beat.get("emotion", "neutral")
    mood = {
        "happy": "cheerful and bouncy",
        "angry": "comically frustrated",
        "surprised": "wide-eyed and startled",
        "sad": "droopy and sulking",
        "neutral": "calm and friendly",
    }.get(emotion, "calm and friendly")
    return (
        f"The cute 3D toy pencil character from @Image1 stands in the real-life "
        f"location shown in @Image2, {mood}, talking directly to the camera and "
        f"speaking the dialogue in @Audio1 with accurate lip sync and expressive "
        f"gestures. The character keeps the exact same design, colors and "
        f"proportions as @Image1. Photorealistic lighting that matches the "
        f"location, soft contact shadow under the character, subtle handheld "
        f"camera, shallow depth of field. Vertical 9:16 composition."
    )


def render_beat(client, beat_idx: int, beat: dict, characters: dict,
                resolution: str) -> Path | None:
    import fal_client

    char = beat["character"]
    audio = config.OUT / f"beat_{beat_idx}.mp3"
    sprite = sprite_path(char, beat.get("emotion", "neutral"))
    photo = photo_path(beat.get("background", "home"))
    for p, label in [(audio, "ses"), (sprite, "sprite"), (photo, "foto")]:
        if not p.exists():
            print(f"  beat {beat_idx}: {label} bulunamadı ({p}), atlanıyor")
            return None

    print(f"  beat {beat_idx} [{char}/{beat.get('emotion','neutral')}] yükleniyor…")
    image_url = fal_client.upload_file(str(sprite))
    photo_url = fal_client.upload_file(str(photo))
    audio_url = fal_client.upload_file(str(audio))

    char_name = characters.get(char, {}).get("name", char)
    print(f"  beat {beat_idx} üretiliyor (Seedance)…")
    result = fal_client.subscribe(
        ENDPOINT,
        arguments={
            "prompt": build_prompt(beat, char_name),
            "image_urls": [image_url, photo_url],
            "audio_urls": [audio_url],
            "resolution": resolution,
            "duration": "auto",
            "aspect_ratio": "9:16",
            "generate_audio": True,
        },
        with_logs=False,
    )
    video_url = result["video"]["url"]

    out_path = SEEDANCE_OUT / f"beat_{beat_idx}.mp4"
    import urllib.request
    urllib.request.urlretrieve(video_url, out_path)
    print(f"  beat {beat_idx} indirildi → {out_path}")
    return out_path


def concat_clips(clips: list[Path], out_file: Path) -> None:
    """Klipleri tek codec'e normalize edip birleştirir."""
    list_file = SEEDANCE_OUT / "concat.txt"
    norm: list[Path] = []
    for c in clips:
        n = c.with_suffix(".norm.mp4")
        subprocess.run(
            [config.FFMPEG, "-y", "-i", str(c),
             "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,"
                    "pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=30",
             "-c:v", "libx264", "-preset", "fast", "-crf", "18",
             "-c:a", "aac", "-ar", "44100", "-ac", "2",
             str(n)],
            check=True, capture_output=True)
        norm.append(n)
    list_file.write_text("\n".join(f"file '{n.name}'" for n in norm))
    subprocess.run(
        [config.FFMPEG, "-y", "-f", "concat", "-safe", "0",
         "-i", str(list_file), "-c", "copy", str(out_file)],
        check=True, capture_output=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--beats", type=int, default=3, help="kaç beat üretilecek")
    ap.add_argument("--start", type=int, default=0, help="başlangıç beat indexi")
    ap.add_argument("--resolution", default="480p", choices=["480p", "720p", "1080p"])
    ap.add_argument("--manifest", default=str(config.OUT / "manifest.json"))
    args = ap.parse_args()

    fal_key = os.getenv("FAL_KEY", "")
    if not fal_key:
        sys.exit("FAL_KEY .env'de yok. fal.ai → Dashboard → Keys → 'Add key' "
                 "yapıp .env dosyasına FAL_KEY=... satırını ekle.")
    os.environ["FAL_KEY"] = fal_key

    import fal_client  # noqa: F401  (anahtar kontrolünden sonra import)

    manifest = json.loads(Path(args.manifest).read_text())
    beats = manifest["beats"][args.start:args.start + args.beats]
    total_s = sum((b["endFrame"] - b["startFrame"]) / manifest.get("fps", 30)
                  for b in beats)
    rate = {"480p": 0.135, "720p": 0.3024, "1080p": 0.682}[args.resolution]
    print(f"{len(beats)} beat, ~{total_s:.0f} sn video, tahmini maliyet "
          f"~${total_s * rate:.2f} ({args.resolution})")

    SEEDANCE_OUT.mkdir(exist_ok=True)
    clips: list[Path] = []
    for i, beat in enumerate(beats, start=args.start):
        clip = render_beat(fal_client, i, beat, manifest.get("characters", {}),
                           args.resolution)
        if clip:
            clips.append(clip)

    if not clips:
        sys.exit("Hiç klip üretilemedi.")

    out_file = config.OUT / "seedance_pilot.mp4"
    concat_clips(clips, out_file)
    print(f"\nPilot hazır → {out_file}")


if __name__ == "__main__":
    main()
