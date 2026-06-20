"""Long-form episode runner: generates 8-10 mini scenes and concatenates them.

Each scene is a full short pipeline run (script → voice → lipsync → render).
Final output: outputs/long_episodes/YYYY-MM-DD-{slug}/episode_full.mp4

Uploads automatically to ALL 4 platforms (TikTok long video, YouTube, Instagram, Facebook).
Use --no-publish to skip upload (render only).

Usage:
  python pipeline/long_episode.py --auto               # full auto → render + upload all 4
  python pipeline/long_episode.py --auto --no-publish  # render only, skip upload
  python pipeline/long_episode.py --plan-only          # generate plan JSON only
  python pipeline/long_episode.py --resume --from-scene 5  # restart from scene N
"""
from __future__ import annotations
import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import anthropic

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config
import generate_script
import synthesize_voice
import lipsync
import build_manifest

sys.path.insert(0, str(config.ROOT / "publish"))
import upload

# ---------------------------------------------------------------------------
EPISODE_PLANNER_SYSTEM = """You are a head writer for "The Pen Family" — a kids animated YouTube series.
Episodes are 8-10 minutes. Structured as exactly 10 acts.
Characters: Oz (Dad), Mas (Mom), Bas (teen sister 16), Saf (little sister 9), Sem (boy 4), Mira (baby).
Guest characters: Eli (red eraser neighbor), Kit (blue notebook cousin), Rex (gold ruler grandpa), Nib (marker aunt).
Story rules: Funny. Cute. Educational. Safe for kids 3-8. Clear lesson shown through action, never stated.
No violence, no scary content, no adult jokes, no politics, no religion.

IMPORTANT: Sem is 4 years old (preschooler). Mira is 1 (baby, single words only).

Available backgrounds: home, kitchen, bedroom, bathroom, school, park, shop, street
"""

EPISODE_PLANNER_PROMPT = """Create a 10-act episode plan for The Pen Family.

Topic: {topic}

For each act, output JSON. Acts must follow this structure:
1. Hook — Open mid-chaos (45s)
2. Family Intro — Establish situation (50s)
3. Funny Problem — Problem revealed (60s)
4. First Failed Attempt — Dad tries and fails (60s)
5. New Clue — Saf asks the right question (50s)
6. Adventure — Family goes somewhere or discovers something (65s)
7. Bigger Challenge — Things get worse (70s)
8. Solution — Family works together (60s)
9. Lesson Learned — Shown through action (45s)
10. Funny Ending — Callback joke + subscribe (50s)

Output ONLY valid JSON:
{{
  "episode_title": "max 10 words",
  "episode_premise": "2 sentences describing the full episode",
  "slug": "hyphen-case-title-slug",
  "scenes": [
    {{
      "act": 1,
      "act_name": "Hook",
      "topic": "What physically happens in this scene as a script generation topic (1-2 sentences)",
      "background": "home",
      "target_seconds": 45,
      "carry_forward": null
    }}
  ]
}}

10 scenes exactly. Each topic must be specific enough to generate a funny script from.
carry_forward is null for scene 1, then a brief note on what to remember from previous scene."""

# ---------------------------------------------------------------------------
ACT_NAMES = [
    "hook", "family_intro", "funny_problem", "first_attempt",
    "new_clue", "adventure", "bigger_challenge", "solution",
    "lesson_learned", "funny_ending",
]


def generate_episode_plan(topic: str) -> dict:
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=config.LLM_MODEL,
        max_tokens=3000,
        system=EPISODE_PLANNER_SYSTEM,
        messages=[{"role": "user", "content": EPISODE_PLANNER_PROMPT.format(topic=topic)}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    # Strip markdown fences and any trailing text after the JSON object
    if "```" in text:
        text = text[text.find("{"):]
    start = text.find("{")
    if start > 0:
        text = text[start:]
    # Trim to valid JSON — find the matching closing brace
    depth = 0
    end = 0
    for i, ch in enumerate(text):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    text = text[:end]
    plan = json.loads(text)
    assert len(plan["scenes"]) == 10, f"Expected 10 scenes, got {len(plan['scenes'])}"
    return plan


def _episode_out_dir(slug: str) -> Path:
    date = datetime.now().strftime("%Y-%m-%d")
    safe = re.sub(r"[^a-z0-9-]", "", slug.lower().replace(" ", "-"))[:40]
    out = config.ROOT / "outputs" / "long_episodes" / f"{date}-{safe}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def render_scene(scene_topic: str, scene_dir: Path, act_name: str) -> Path:
    """Run full pipeline for one scene into scene_dir. Returns path to video.mp4."""
    scene_dir.mkdir(parents=True, exist_ok=True)

    # Temporarily redirect OUT to scene_dir
    orig_out = config.OUT
    config.OUT = scene_dir

    try:
        script = generate_script.generate(scene_topic)
        (scene_dir / "script.json").write_text(
            json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  [script] {script['title']} ({len(script['beats'])} beats)")

        synthesize_voice.synthesize(script)
        lipsync.lipsync(script)
        manifest = build_manifest.build(script)
        manifest_path = scene_dir / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

        out_mp4 = scene_dir / "video.mp4"
        renderer = config.ROOT / "renderer"
        props = {"manifest": manifest}
        props_path = scene_dir / "props.json"
        props_path.write_text(json.dumps(props), encoding="utf-8")
        subprocess.run(
            ["npx", "remotion", "render", "PencilShort", str(out_mp4),
             f"--props={props_path}", "--public-dir=../"],
            cwd=renderer, check=True,
        )
        print(f"  [render] {out_mp4.name} ({manifest['totalDurationFrames']/config.FPS:.1f}s)")
        return out_mp4
    finally:
        config.OUT = orig_out


def concat_scenes(scene_videos: list[Path], out_path: Path) -> Path:
    """Concatenate all scene videos into one episode file using FFmpeg stream copy."""
    concat_list = out_path.parent / "concat_list.txt"
    lines = "\n".join(f"file '{v.resolve()}'" for v in scene_videos)
    concat_list.write_text(lines, encoding="utf-8")
    subprocess.run([
        config.FFMPEG, "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list),
        "-c", "copy",
        str(out_path),
    ], check=True)
    concat_list.unlink()
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", help="Episode topic / premise")
    ap.add_argument("--auto", action="store_true", help="Pick a random topic")
    ap.add_argument("--plan-only", action="store_true", help="Only generate the plan JSON")
    ap.add_argument("--no-publish", action="store_true", help="Skip upload after render")
    ap.add_argument("--resume", action="store_true", help="Resume from a checkpoint")
    ap.add_argument("--from-scene", type=int, default=1, help="Scene number to resume from (1-10)")
    ap.add_argument("--plan-file", help="Load existing plan JSON instead of generating")
    args = ap.parse_args()

    # --- Pick topic ---
    LONG_TOPICS = [
        "Sem accidentally shrinks the whole family with Aunt Nib's magical marker",
        "The family finds a baby dragon (actually a lost lizard) and tries to return it",
        "Oz builds a treehouse but Sem 'helps' and it ends up upside down",
        "The school talent show where everyone has a secret act nobody knew about",
        "Sem gets lost in a giant supermarket and makes friends with the vegetables",
        "The Pen Family's worst camping trip: rain, bears, and Sem's genius ideas",
        "Bas accidentally livestreams the most chaotic family dinner ever to 50,000 people",
        "Grandpa Rex visits and tries to teach the family 'old fashioned' values for a day",
        "The family tries to surprise Mas for her birthday but Sem tells her everything",
        "Cousin Kit moves in for a week and tries to organize the entire chaotic house",
    ]
    import random
    topic = args.topic or (random.choice(LONG_TOPICS) if args.auto else None)
    if not topic and not args.plan_file:
        ap.error("Provide --topic, --auto, or --plan-file")

    # --- Load or generate plan ---
    if args.plan_file:
        plan = json.loads(Path(args.plan_file).read_text(encoding="utf-8"))
    else:
        print(f"=== Generating episode plan: {topic} ===")
        plan = generate_episode_plan(topic)
        print(f"[plan] {plan['episode_title']} — {len(plan['scenes'])} scenes")

    episode_dir = _episode_out_dir(plan.get("slug", "episode"))
    plan_path = episode_dir / "episode_plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[plan] saved → {plan_path}")

    if args.plan_only:
        print("=== Plan only mode — done ===")
        return

    # --- Render scenes ---
    scene_videos: list[Path] = []
    start_scene = args.from_scene if args.resume else 1

    for scene in plan["scenes"]:
        act_num = scene["act"]
        if act_num < start_scene:
            # Resume: check if video already exists
            act_label = ACT_NAMES[act_num - 1]
            scene_dir = episode_dir / f"scene_{act_num:02d}_{act_label}"
            existing = scene_dir / "video.mp4"
            if existing.exists():
                print(f"[scene {act_num:02d}] Skipping (already rendered) → {existing}")
                scene_videos.append(existing)
            continue

        act_label = ACT_NAMES[act_num - 1]
        scene_dir = episode_dir / f"scene_{act_num:02d}_{act_label}"
        print(f"\n=== Scene {act_num:02d}/10: {scene['act_name']} ===")

        # Enrich topic with carry-forward context
        full_topic = scene["topic"]
        if scene.get("carry_forward"):
            full_topic += f". Context from previous scene: {scene['carry_forward']}"

        try:
            mp4 = render_scene(full_topic, scene_dir, act_label)
            scene_videos.append(mp4)
            # Save checkpoint
            checkpoint = episode_dir / "checkpoint.json"
            checkpoint.write_text(json.dumps({"last_completed": act_num}), encoding="utf-8")
        except Exception as e:
            print(f"[ERROR] Scene {act_num} failed: {e}")
            print(f"To resume: python pipeline/long_episode.py --plan-file {plan_path} --resume --from-scene {act_num}")
            sys.exit(1)

    # --- Concatenate ---
    print(f"\n=== Concatenating {len(scene_videos)} scenes ===")
    episode_mp4 = episode_dir / "episode_full.mp4"
    concat_scenes(scene_videos, episode_mp4)
    print(f"[concat] {episode_mp4}")

    # Build episode-level upload manifest (title + description + hashtags)
    episode_manifest = {
        "title": plan["episode_title"],
        "description": (
            plan.get("episode_premise", plan["episode_title"])
            + " 🎬 The Pen Family — new episodes every 3 days!"
        ),
        "hashtags": [
            "#ThePenFamily", "#KidsCartoon", "#FamilyAnimation",
            "#KidsYouTube", "#AnimatedSeries", "#FamilyFun", "#KidsTv",
        ],
    }

    # Save metadata
    meta = {
        "title": plan["episode_title"],
        "premise": plan.get("episode_premise", ""),
        "scenes": len(scene_videos),
        "output": str(episode_mp4),
        "rendered_at": datetime.now().isoformat(),
    }
    (episode_dir / "episode_metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    # Symlink outputs/long_episodes/latest → this episode
    latest = config.ROOT / "outputs" / "long_episodes" / "latest"
    if latest.is_symlink():
        latest.unlink()
    latest.symlink_to(episode_dir.resolve())

    print(f"\n=== Episode complete: {episode_mp4} ===")

    if args.no_publish:
        print("Upload atlandı (--no-publish).")
        print(f"Manuel upload: python3 publish/upload.py --video {episode_mp4}")
        return

    # Upload to all 4 platforms automatically
    # TikTok supports long videos (up to 10 min), Facebook Video, Instagram Video, YouTube
    LONG_PLATFORMS = ["tiktok", "youtube", "instagram", "facebook"]
    print(f"\n[upload] Tüm platformlara gönderiliyor: {', '.join(LONG_PLATFORMS)}")
    upload.publish(LONG_PLATFORMS, video_path=episode_mp4, manifest_data=episode_manifest)
    print("=== Done: episode live on all platforms ===")


if __name__ == "__main__":
    main()
