"""Long-form unified episode pipeline.

Generates ONE complete coherent script (Bluey/Niloya style) and renders
it as a single video — no scene stitching, no concatenation.

Usage:
  python pipeline/run_long_unified.py --auto
  python pipeline/run_long_unified.py --script /path/to/script.json   # use pre-approved script
  python pipeline/run_long_unified.py --auto --no-publish             # render only, upload to S3 for preview
  python pipeline/run_long_unified.py --auto --no-render              # script only
"""
from __future__ import annotations
import argparse
import json
import random
import subprocess
import sys
from pathlib import Path

import anthropic
import config
import synthesize_voice
import lipsync
import build_manifest

sys.path.insert(0, str(config.ROOT / "publish"))
import upload


# ── Topic pool ──────────────────────────────────────────────────────────────
LONG_TOPICS = [
    {
        "title": "The Dinosaur Egg",
        "premise": "Sem finds a tiny seed and is 100% convinced it's a dinosaur egg. He puts it in wrong places (cereal box, Oz's shoe, bathtub). Saf teaches him about soil/water/sunlight and photosynthesis ('the plant eats sunshine!'). They plant it together. Mira overwaters. Day 8 it sprouts. Sem names it Sunshine.",
        "education": "Seeds need soil, water, sunlight. Photosynthesis. Patience. Caring for living things."
    },
    {
        "title": "The Missing Cookie",
        "premise": "A cookie disappears from the kitchen. Everyone suspects someone else. Saf starts a full investigation with evidence. Sem confesses to eating it but claims 'the cookie jumped into my mouth.' Mas calmly reveals she hid it because Sem had already eaten four. Lesson: honesty and consequences.",
        "education": "Honesty, cause and effect, family trust."
    },
    {
        "title": "Saf's Science Fair",
        "premise": "Saf has a science fair project about the water cycle. Sem keeps 'helping' and making it worse. Oz tries to explain with a dad analogy nobody understands. Mas quietly fixes everything. The project wins — but Saf gives Sem credit for accidentally making the rain cloud demonstration better.",
        "education": "Water cycle: evaporation, condensation, precipitation. Teamwork."
    },
    {
        "title": "Bas's Big Audition",
        "premise": "Bas has a video audition for a youth talent show. Sem keeps walking into frame. The family tries to keep him out. Eventually Sem's interruption goes viral and Bas gets in because of it. She's embarrassed then secretly grateful. Lesson: unexpected help from people you love.",
        "education": "Creativity, persistence, accepting help."
    },
    {
        "title": "The Bedtime Machine",
        "premise": "Sem invents 'the bedtime machine' — a pillow fort with dials — to avoid going to sleep. Saf explains why sleep is important (brain growth, repair). Oz adds a dad story. Eventually Sem falls asleep inside his own machine mid-explanation.",
        "education": "Why sleep is important, brain development, health habits."
    },
]

LONG_SYSTEM = """You are a professional children's TV writer. You write "The Pen Family" — a Bluey/Niloya-style animated family show on YouTube. Episodes are warm, funny, and teach something real without being preachy.

THE PEN FAMILY:
- OZ (Dad, 35): Southern American dad. Warm, slightly goofy. Complete sentences. "Now hold on—" / "Family meeting!" / "Back in my day..." Never uses slang.
- MAS (Mom, 32): Smart, calm New Yorker. Already knows what's happening. "I knew this would happen." / "Everybody relax." Dry wit.
- BAS (Big Sister, 16): Teen girl, dramatic, TikTok-obsessed. "Seriously?" / "That is SO embarrassing." / "This is actually good content." Secretly loves family.
- SAF (Little Sister, 9): Endless curiosity, science brain. Always asks the KEY question. "Wait, but HOW does that work?" Makes everyone smarter.
- SEM (Little Brother, 4): ⚠️ FOUR YEARS OLD. Short sentences. Mispronounces words. "I got a pwan!" / "Uh oh..." / "Look what I did!" Chaos machine. Thinks every idea is genius.
- MIRA (Baby, 1): ONLY baby sounds. "Ba-ba!" / "Hehe!" / "Uh-oh!" NEVER sentences. Accidentally causes or fixes things.

WRITING RULES:
1. ONE continuous story. Characters REFER BACK to earlier moments. Not stitched scenes.
2. Each line MAX 18 WORDS. Natural real speech.
3. Rhythm: funny → frustrated → warm → educational → resolution. Let quiet moments breathe.
4. Educational content is INVISIBLE — taught through Saf's curiosity, Sem's misunderstanding, parent responses.
5. VOICE CONTRAST: Sem says "wotew/soiw/dino-saw". Bas says "literally". Saf says "actually". Oz says "Now hold on a second." Mas says "I knew this would happen."
6. Humor from CHARACTER. Every joke reveals personality.
7. Lesson lands naturally in final 6-8 beats. Never preachy.
8. Write 60-70 BEATS. Each beat = one character's dialogue line."""

LONG_PROMPT = """Write a complete 62-70 beat episode for The Pen Family.

TITLE: {title}
PREMISE: {premise}
EDUCATIONAL THEME: {education}

Structure:
- Beats 1-10: Normal family morning. Problem starts (Sem causes it).
- Beats 11-28: Family reacts. Sem makes it worse in 2-3 funny ways. Saf tries science. Bas films.
- Beats 29-45: Family meeting OR moment of calm. Saf teaches the key fact naturally. Sem misunderstands adorably.
- Beats 46-58: They do the right thing together. Mira accidentally helps/hinders. Warm family moment.
- Beats 59-70: Resolution. Lesson lands through Sem saying something unexpectedly wise. Warm ending.

DIALOGUE QUALITY: Natural English for families. Clear vocabulary — kids learning English as a second language should understand words from context. NO forced educational speeches. Funny because of who the characters are.

Output ONLY valid JSON:
{{
  "title": "...",
  "description": "...(2-3 warm sentences for YouTube/Instagram, with emojis)",
  "hashtags": ["ThePenFamily", "KidsCartoon", ... 8 total],
  "background": "kitchen",
  "beats": [
    {{"character": "sem", "text": "...(max 18 words)", "emotion": "happy|neutral|surprised|angry|sad", "background": "kitchen|home|bedroom|bathroom|park|school|shop|street"}}
  ]
}}

Write 62-70 beats. ONE continuous story that feels like a real 7-minute cartoon."""


def _generate_script(topic: dict) -> dict:
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=config.LLM_MODEL,
        max_tokens=6000,
        system=LONG_SYSTEM,
        messages=[{"role": "user", "content": LONG_PROMPT.format(**topic)}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    # Extract JSON object
    start = text.find("{")
    depth = 0; end = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{": depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0: end = i + 1; break
    script = json.loads(text[start:end])
    # Enforce 18-word limit (relaxed from 12 for long episodes)
    for b in script["beats"]:
        words = b["text"].split()
        if len(words) > 18:
            b["text"] = " ".join(words[:18])
        if b["character"] not in config.CHARACTERS:
            b["character"] = list(config.CHARACTERS.keys())[0]
    return script


def _upload_preview_s3(video_path: Path) -> str:
    """Upload rendered video to S3 and return a pre-signed URL for preview."""
    import boto3, datetime
    s3 = boto3.client("s3", region_name="us-east-1")
    bucket = "pencil-shorts-tfstate-339712706640"
    key = f"previews/{datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-preview.mp4"
    s3.upload_file(str(video_path), bucket, key,
                   ExtraArgs={"ContentType": "video/mp4"})
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=86400,  # 24 hours
    )
    return url


def render(manifest_path: Path, out_mp4: Path) -> Path:
    renderer = config.ROOT / "renderer"
    props_path = out_mp4.parent / "props.json"
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    props_path.write_text(json.dumps({"manifest": manifest_data}), encoding="utf-8")
    subprocess.run(
        ["npx", "remotion", "render", "PencilShort", str(out_mp4),
         f"--props={props_path}", f"--public-dir={config.ROOT}"],
        cwd=renderer, check=True,
    )
    return out_mp4


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--auto", action="store_true", help="Pick a random topic")
    ap.add_argument("--topic-index", type=int, help="Use specific topic (0-based)")
    ap.add_argument("--script", help="Path to pre-approved script JSON")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--no-publish", action="store_true",
                    help="Render only — upload to S3 for preview, don't post to social")
    args = ap.parse_args()

    out_dir = config.OUT
    out_dir.mkdir(exist_ok=True)

    # ── 1. Script ─────────────────────────────────────────────────────────
    if args.script:
        script = json.loads(Path(args.script).read_text(encoding="utf-8"))
        print(f"[script] Using pre-approved: {script['title']} ({len(script['beats'])} beats)")
    else:
        if args.topic_index is not None:
            topic = LONG_TOPICS[args.topic_index]
        elif args.auto:
            topic = random.choice(LONG_TOPICS)
        else:
            ap.error("Use --auto, --topic-index N, or --script PATH")
        print(f"=== Generating episode: {topic['title']} ===")
        script = _generate_script(topic)
        print(f"[script] {script['title']} ({len(script['beats'])} beats)")

    (out_dir / "script.json").write_text(
        json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.no_render:
        print("=== Script done (--no-render). ===")
        return

    # ── 2. Voice ──────────────────────────────────────────────────────────
    print("[1/4] Synthesising voice...")
    synthesize_voice.synthesize(script)

    # ── 3. Lip sync ───────────────────────────────────────────────────────
    print("[2/4] Lip sync...")
    lipsync.lipsync(script)

    # ── 4. Manifest ───────────────────────────────────────────────────────
    print("[3/4] Building manifest...")
    manifest = build_manifest.build(script)
    # Fix audio path to be relative to repo root
    manifest["audio"] = str(
        (out_dir / "audio_full.wav").relative_to(config.ROOT)
    )
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    duration_s = manifest["totalDurationFrames"] / config.FPS
    print(f"[3/4] Duration: {duration_s:.1f}s ({duration_s/60:.1f} min)")

    # ── 5. Render ─────────────────────────────────────────────────────────
    print("[4/4] Rendering (this takes a while)...")
    out_mp4 = out_dir / "long_episode.mp4"
    render(manifest_path, out_mp4)
    size_mb = out_mp4.stat().st_size / 1_000_000
    print(f"[4/4] Rendered: {out_mp4.name} ({size_mb:.1f} MB, {duration_s:.1f}s)")

    # ── 6. Publish or preview ─────────────────────────────────────────────
    if args.no_publish:
        print("[preview] Uploading to S3 for review...")
        try:
            url = _upload_preview_s3(out_mp4)
            print(f"\n{'='*60}")
            print(f"PREVIEW URL (expires 24h):")
            print(url)
            print(f"{'='*60}\n")
        except Exception as e:
            print(f"[preview] S3 upload failed: {e}")
            print(f"[preview] Video is at: {out_mp4}")
        return

    print("[5/5] Uploading to all platforms...")
    episode_manifest = {
        "title": script["title"],
        "description": script.get("description", script["title"]),
        "hashtags": script.get("hashtags", []),
    }
    upload.publish(
        ["youtube"],
        video_path=out_mp4,
        manifest_data=episode_manifest,
    )
    print("=== Done: episode live on all platforms ===")


if __name__ == "__main__":
    main()
