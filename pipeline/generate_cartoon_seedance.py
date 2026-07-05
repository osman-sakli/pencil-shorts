"""Gerçek çizgi film üretimi: senaryo (aksiyon sahneli) -> EdgeTTS -> Seedance 2.0.

Her beat, Seedance reference-to-video ile TAM ANİMASYON olarak üretilir:
karakterler çizgi film dünyasında yürür, nesnelerle etkileşir, senaryodaki
aksiyonu oynar; dudak senkronu EdgeTTS sesinden (@Audio1) gelir.
Ortam fotoğraf değil, 3D çizgi film dünyasıdır (Niloya/Cocomelon tarzı).

Kullanım:
  python pipeline/generate_cartoon_seedance.py --script examples/cookie_cartoon.json --beats 1   # tek beat test
  python pipeline/generate_cartoon_seedance.py --script examples/cookie_cartoon.json             # tümü

Maliyet: 480p ≈ $0.135/sn -> ~60 sn'lik bölüm ≈ $8-9.
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import config
import synthesize_voice

ENDPOINTS = {
    "full": "bytedance/seedance-2.0/reference-to-video",
    "mini": "bytedance/seedance-2.0/mini/reference-to-video",
}
ENDPOINT = ENDPOINTS["full"]  # geriye dönük uyumluluk
RATES_480P = {"full": 0.135, "mini": 0.0721}  # $/sn
CARTOON_OUT = config.OUT / "cartoon"

AI_CHARS = {"oz", "mas", "bas", "saf", "sem", "mira", "biscuit", "mittens", "snip"}
VALID_EMOTIONS = {"neutral", "happy", "angry", "surprised", "sad"}

# Ortam tarifleri — her beat'te AYNI metin kullanılır ki sahneler tutarlı olsun
ENVIRONMENTS = {
    "kitchen": ("a cozy 3D cartoon kitchen with warm wooden cabinets, a big "
                "round glass cookie jar on the counter, colorful tiles, soft "
                "morning light through a window"),
    "home": ("a cozy 3D cartoon living room with a big soft orange couch, a "
             "round rug, framed drawings of pencil characters on warm yellow "
             "walls, soft afternoon light"),
}
DEFAULT_ENV = ENVIRONMENTS["home"]

STYLE = ("High-quality 3D animated children's cartoon, preschool TV series "
         "quality, bright saturated colors, soft rounded shapes, smooth and "
         "expressive full-body character animation, cheerful and warm mood, "
         "gentle camera movement. Consistent character design across shots. "
         "Keep the main characters and action centered in the frame. "
         "CRITICAL: this world is inhabited ONLY by pencil/pen characters "
         "and cute animal pets. Absolutely NO humans, no human people, no "
         "human children, no human hands or faces anywhere in the scene — "
         "not even inside picture frames, photographs or posters. Any "
         "framed pictures on walls show pencil characters only.")

# Kanonik karakter tarifleri — her prompt'a giren kimlik + boy + kalem ucu ayak
CHAR_DESC = {
    "oz":      "Oz the dad pen (tallest, dark blue, black glasses, striped tie)",
    "mas":     "Mas the mom pen (slightly shorter than dad, pink, pearl necklace, heart charm)",
    "bas":     "Bas the teenage big sister pen (teal, purple sunglasses/glasses, pink phone, purse)",
    "saf":     "Saf the 9-year-old little sister pen (purple, big purple bow on cap, yellow star on chest, much shorter than the teens)",
    "sem":     "Sem the 4-year-old little brother pen (green, green hoodie, small and chubby)",
    "mira":    "Mira the 1-year-old baby girl pen (yellow, tiny, pink pacifier, small pearl necklace, little bow)",
    "biscuit": "Biscuit the puppy pen (golden-orange, red collar with bone tag, floppy ears)",
    "twinkle": "Twinkle the tiny magical star child (small glowing golden five-pointed star, big sparkly eyes, rosy cheeks, tiny stubby arms, soft warm golden glow with gentle sparkles, smaller than baby Mira)",
}
SIZE_RULE = ("Character heights follow the family order: dad Oz is the "
             "tallest, mom Mas slightly shorter, teen Bas shorter than mom, "
             "Saf child-sized, Sem toddler-sized, baby Mira the tiniest. "
             "EVERY character, including Sem and baby Mira, stands and walks "
             "balanced on a single sharpened pencil-tip point instead of "
             "feet — no human feet or shoes.")


def sprite_path(char: str, emotion: str = "neutral") -> Path:
    if char in AI_CHARS:
        emo = emotion if emotion in VALID_EMOTIONS else "neutral"
        base = config.ROOT / "characters" / "sprites"
        # Seedance için kalem ucu ayaklı varyant varsa onu tercih et
        tip = base / f"{char}_{emo}_tip.png"
        return tip if tip.exists() else base / f"{char}_{emo}.png"
    return config.ROOT / "characters" / "sprites" / f"{char}.png"


def build_prompt(beat: dict, cast: list[str], aspect: str,
                 environments: dict[str, str]) -> str:
    env = environments.get(beat.get("background", "home"), DEFAULT_ENV)
    who = "; ".join(
        f"@Image{i+1} is {CHAR_DESC.get(c, c)}" for i, c in enumerate(cast))
    comp = ("Vertical 9:16 composition." if aspect == "9:16"
            else "Cinematic horizontal 16:9 composition.")
    return (
        f"{STYLE} {SIZE_RULE} Setting: {env}. "
        f"Characters: {who}. "
        f"They act out this scene: {beat['action']} "
        f"The speaking character speaks the dialogue in @Audio1 with accurate "
        f"lip sync while performing the action. Characters keep the same "
        f"design, colors and proportions as the reference images. "
        f"{comp}"
    )


def render_beat(beat_idx: int, beat: dict, resolution: str,
                prev_clip_url: str | None, aspect: str = "9:16",
                environments: dict[str, str] | None = None,
                model: str = "full") -> tuple[Path, str] | None:
    import fal_client

    audio = config.OUT / f"beat_{beat_idx}.mp3"
    if not audio.exists():
        print(f"  beat {beat_idx}: ses yok ({audio}), atlanıyor")
        return None

    cast = beat.get("cast", [beat["character"]])
    # Konuşan karakter her zaman @Image1
    cast = [beat["character"]] + [c for c in cast if c != beat["character"]]
    cast = cast[:4]
    image_urls = [fal_client.upload_file(str(sprite_path(c, beat.get("emotion", "neutral") if c == beat["character"] else "neutral")))
                  for c in cast]
    audio_url = fal_client.upload_file(str(audio))

    # Süreyi sese bağla: ses + 1.5 sn oyunculuk payı, 4-8 sn arası (tempo + maliyet)
    probe = subprocess.run(
        [config.FFMPEG.replace("ffmpeg", "ffprobe"), "-v", "error",
         "-show_entries", "format=duration", "-of", "csv=p=0", str(audio)],
        capture_output=True, text=True)
    audio_s = float(probe.stdout.strip() or 5)
    duration = str(min(8, max(4, round(audio_s + 1.5))))

    args = {
        "prompt": build_prompt(beat, cast, aspect, environments or ENVIRONMENTS),
        "image_urls": image_urls,
        "audio_urls": [audio_url],
        "resolution": resolution,
        "duration": duration,
        "aspect_ratio": aspect,
        "generate_audio": True,
    }
    # Sahne/stil sürekliliği: önceki klip aynı ortamdaysa referans ver
    if prev_clip_url:
        args["video_urls"] = [prev_clip_url]
        args["prompt"] += (" Continue in exactly the same environment, art "
                           "style and character designs as @Video1.")

    print(f"  beat {beat_idx} [{beat['character']}] üretiliyor ({model})…")
    result = fal_client.subscribe(ENDPOINTS[model], arguments=args, with_logs=False)
    video_url = result["video"]["url"]

    out_path = CARTOON_OUT / f"beat_{beat_idx}.mp4"
    import urllib.request
    for attempt in (1, 2, 3):
        urllib.request.urlretrieve(video_url, out_path)
        # Bütünlük: dosya süresi istenen sürenin en az %80'i olmalı (kopuk indirme koruması)
        probe = subprocess.run(
            [config.FFMPEG.replace("ffmpeg", "ffprobe"), "-v", "error",
             "-show_entries", "format=duration", "-of", "csv=p=0", str(out_path)],
            capture_output=True, text=True)
        got = float(probe.stdout.strip() or 0)
        if got >= float(duration) * 0.8 and out_path.stat().st_size > 400_000:
            break
        print(f"  beat {beat_idx}: indirme kopuk ({got:.1f}s/{duration}s), deneme {attempt}/3")
    print(f"  beat {beat_idx} indirildi → {out_path.name}")
    return out_path, video_url


def mux_and_concat(items: list[tuple[int, Path]], out_file: Path,
                   aspect: str = "9:16") -> None:
    """Her klibe kendi EdgeTTS sesini bindir (garanti ses + senkron), birleştir."""
    w, h = ("1080", "1920") if aspect == "9:16" else ("1920", "1080")
    norm: list[Path] = []
    for beat_idx, clip in items:
        audio = config.OUT / f"beat_{beat_idx}.mp3"
        n = clip.with_suffix(".norm.mp4")
        subprocess.run(
            [config.FFMPEG, "-y", "-i", str(clip), "-i", str(audio),
             "-map", "0:v", "-map", "1:a",
             "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
                    f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,fps=30",
             "-af", "apad",  # ses klipten kısaysa sessizlikle doldur
             "-shortest",
             "-c:v", "libx264", "-preset", "fast", "-crf", "18",
             "-c:a", "aac", "-ar", "44100", "-ac", "2",
             str(n)],
            check=True, capture_output=True)
        norm.append(n)
    list_file = CARTOON_OUT / "concat.txt"
    list_file.write_text("\n".join(f"file '{n.name}'" for n in norm))
    subprocess.run(
        [config.FFMPEG, "-y", "-f", "concat", "-safe", "0",
         "-i", str(list_file), "-c", "copy", str(out_file)],
        check=True, capture_output=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--beats", type=int, default=0, help="0 = hepsi")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--resolution", default="480p", choices=["480p", "720p", "1080p"])
    ap.add_argument("--aspect", default="9:16", choices=["9:16", "16:9"])
    ap.add_argument("--tts", default="openai", choices=["openai", "edge", "elevenlabs"],
                    help="çizgi filmlerde varsayılan: openai (doğal oyunculuk)")
    ap.add_argument("--no-tts", action="store_true", help="sesler zaten üretildiyse atla")
    ap.add_argument("--dry-run", action="store_true",
                    help="Seedance'i ÇAĞIRMADAN tüm promptları + maliyeti dök (bedava ön kontrol)")
    ap.add_argument("--no-continuity", action="store_true",
                    help="devam modunda önceki klibi referans ALMA")
    ap.add_argument("--model", default="mini", choices=["mini", "full"],
                    help="varsayılan model; beat'te \"model\" alanı varsa o kazanır")
    args = ap.parse_args()

    script = json.loads(Path(args.script).read_text(encoding="utf-8"))
    beats = script["beats"]

    # ── Sert doğrulama: para harcamadan önce her şey yerli yerinde mi? ──
    errors = []
    env_all = {**ENVIRONMENTS, **script.get("environments", {})}
    for i, b in enumerate(beats):
        if b["character"] not in config.CHARACTERS:
            errors.append(f"beat {i}: bilinmeyen karakter '{b['character']}'")
        for c in b.get("cast", []):
            if c not in config.CHARACTERS:
                errors.append(f"beat {i}: cast'te bilinmeyen '{c}'")
        if len(b.get("cast", [])) > 4:
            errors.append(f"beat {i}: cast 4'ten kalabalık (kayma riski)")
        if not b.get("action"):
            errors.append(f"beat {i}: action alanı boş")
        if b.get("background") not in env_all:
            errors.append(f"beat {i}: tanımsız mekân '{b.get('background')}'")
        if b.get("music", script.get("music", "happy")) not in {"mystery", "happy", "calm", "adventure"}:
            errors.append(f"beat {i}: bilinmeyen müzik '{b.get('music')}'")
        if len(b.get("text", "").split()) > 14:
            errors.append(f"beat {i}: replik 14 kelimeden uzun (15sn ses sınırı riski)")
        for c in ([b["character"]] + b.get("cast", []))[:4]:
            sp = sprite_path(c, b.get("emotion", "neutral"))
            if not sp.exists():
                errors.append(f"beat {i}: sprite yok {sp.name}")
    if errors:
        print("DOĞRULAMA HATALARI — hiçbir şey üretilmedi, para harcanmadı:")
        for e in errors:
            print("  ✗", e)
        sys.exit(1)
    print(f"✓ Doğrulama temiz: {len(beats)} beat, karakterler/sprite'lar/mekânlar tamam")

    if args.dry_run:
        est = len(beats) * 6.0
        mix = [b.get("model", args.model) for b in beats]
        rate = sum(RATES_480P[m] for m in mix) / len(mix)
        print(f"model karışımı: {mix.count('mini')} mini + {mix.count('full')} full")
        dump = Path(config.OUT / "dry_run_prompts.txt")
        lines = []
        for i, b in enumerate(beats):
            cast = ([b["character"]] + [c for c in b.get("cast", []) if c != b["character"]])[:4]
            lines.append(f"=== BEAT {i} [{b['character']}/{b.get('emotion')}] "
                         f"bg={b.get('background')} müzik={b.get('music', script.get('music'))}\n"
                         f"REPLİK: {b['text']}\n"
                         f"PROMPT: {build_prompt(b, cast, args.aspect, env_all)}\n")
        dump.write_text("\n".join(lines), encoding="utf-8")
        print(f"~{est:.0f} sn video, tahmini maliyet ~${est * rate:.2f} ({args.resolution})")
        print(f"Tüm promptlar → {dump} (Seedance ÇAĞRILMADI, $0 harcandı)")
        return

    if not os.getenv("FAL_KEY"):
        sys.exit("FAL_KEY .env'de yok.")
    sel = beats[args.start:args.start + args.beats] if args.beats else beats[args.start:]

    if not args.no_tts:
        print(f"[1/3] Sesler üretiliyor ({args.tts})…")
        synthesize_voice.synthesize(script, provider=args.tts)

    print(f"[2/3] {len(sel)} sahne Seedance ile üretiliyor ({args.resolution})…")
    CARTOON_OUT.mkdir(exist_ok=True)
    done: list[tuple[int, Path]] = []
    prev_url: str | None = None
    prev_bg: str | None = None
    # Devam modu: önceki klip diskte varsa ve aynı mekândansa sürekliliği koru
    if args.start > 0 and not args.no_continuity:
        prev_clip = CARTOON_OUT / f"beat_{args.start - 1}.mp4"
        prev_beat_bg = beats[args.start - 1].get("background")
        if prev_clip.exists() and prev_beat_bg == beats[args.start].get("background"):
            import fal_client
            prev_url = fal_client.upload_file(str(prev_clip))
            prev_bg = prev_beat_bg
            print(f"  süreklilik: beat_{args.start - 1} referans alındı")
    for i, beat in enumerate(beats):
        if i < args.start or (args.beats and i >= args.start + args.beats):
            continue
        same_scene_url = prev_url if beat.get("background") == prev_bg else None
        env_overrides = {**ENVIRONMENTS, **script.get("environments", {})}
        try:
            res = render_beat(i, beat, args.resolution, same_scene_url,
                              aspect=args.aspect, environments=env_overrides,
                              model=beat.get("model", args.model))
        except Exception as e:
            print(f"  beat {i} HATA: {e}")
            print("  (bakiye bitmiş olabilir — üretilen klipler out/cartoon/ içinde duruyor)")
            break
        if res:
            clip, url = res
            done.append((i, clip))
            prev_url, prev_bg = url, beat.get("background")

    if not done:
        sys.exit("Hiç sahne üretilemedi.")

    print("[3/3] Sesler bindirilip birleştiriliyor…")
    out_file = config.OUT / "cartoon.mp4"
    mux_and_concat(done, out_file, aspect=args.aspect)
    dur = sum(1 for _ in done)
    print(f"\nÇizgi film hazır ({dur} sahne) → {out_file}")


if __name__ == "__main__":
    main()
