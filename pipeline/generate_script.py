"""Step 1: generate a 60-90s cartoon script as structured JSON via the LLM.

Longer format is intentional: TikTok Creator Rewards only pays on videos >= 60s,
so we target ~150-220 words across 10-14 beats with strong retention structure.

Output schema (out/script.json):
{
  "title": str,
  "background": str,             # opening scene label (from characters.yaml backgrounds)
  "description": str,            # caption body (CTA + emojis); affiliate link appended later
  "hashtags": [str, ...],
  "beats": [
    {"character": str, "text": str, "emotion": "neutral|happy|angry|surprised|sad"}
  ]
}
"""
from __future__ import annotations
import json
import argparse
import random
import anthropic
import config

SYSTEM = """You are a short-form cartoon scriptwriter. You write funny, story-driven 60-90 SECOND videos
featuring stationery characters — pencils, erasers, sharpeners — in everyday drama.

Length & pacing (CRITICAL — revenue requires videos ≥ 60 s):
- Total spoken text fits 60-90 seconds: roughly 150-220 words.
- 10-14 lines (beats). Keep each line short and punchy.
- Retention structure:
  1) FIRST LINE = strong HOOK (plant conflict/curiosity in first 2 seconds).
  2) Middle escalation: a new mini-twist, misunderstanding, or reaction every 3-5 s.
  3) A TWIST near the end.
  4) Final line = funny, satisfying close (not a cliffhanger).
- Stay on one topic; keep the energy up.

Other rules:
- Use ONLY the provided characters.
- Humour: relatable situation comedy, jealousy, rivalry, absurd observations.
- Write in NATIVE, colloquial ENGLISH — the way real people actually talk.
- Also generate a short, punchy 'description' for the video caption (1-2 sentences + a few emojis)
  and 5-8 relevant 'hashtags'.

Return ONLY valid JSON. No markdown, no backticks, no explanations."""

PROMPT_TMPL = """Topic: {topic}

Available characters:
{roster}

Pick a background for the opening scene from: {backgrounds}

Generate JSON in this exact schema:
{{
  "title": "short, curiosity-driving title",
  "background": "background label",
  "description": "punchy caption for viewers + emojis",
  "hashtags": ["#...", "#..."],
  "beats": [
    {{"character": "character_id", "text": "line of dialogue", "emotion": "neutral"}}
  ]
}}

Remember: 10-14 beats, 150-220 words, strong hook + escalation + twist + funny close."""

AUTO_TOPICS = [
    "The pencil is jealous of the eraser",
    "The pen thinks it's immortal",
    "The sharpener threatens everyone with a sharpening",
    "The pencils argue over who gets to take the exam",
    "The eraser erases all mistakes and nobody likes it",
    "A new colourful pencil disrupts the whole squad",
]


def build_prompt(topic: str) -> str:
    roster = "\n".join(
        f"- {cid} ({c['name']}): {c['persona']}"
        for cid, c in config.CHARACTERS.items()
    )
    return PROMPT_TMPL.format(
        topic=topic,
        roster=roster,
        backgrounds=", ".join(config.BACKGROUNDS),
    )


def generate(topic: str) -> dict:
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=config.LLM_MODEL,
        max_tokens=2000,
        system=SYSTEM,
        messages=[{"role": "user", "content": build_prompt(topic)}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{"):]
    script = json.loads(text)
    _validate(script)
    return script


def _validate(script: dict) -> None:
    assert script["background"] in config.BACKGROUNDS, "bilinmeyen arka plan"
    assert script.get("beats"), "beat yok"
    assert len(script["beats"]) >= 8, "60sn+ için en az 8-10 beat gerekir"
    script.setdefault("description", script.get("title", ""))
    script.setdefault("hashtags", [])
    for b in script["beats"]:
        assert b["character"] in config.CHARACTERS, f"bilinmeyen karakter: {b['character']}"
        b.setdefault("emotion", "neutral")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic")
    ap.add_argument("--auto", action="store_true")
    args = ap.parse_args()
    topic = args.topic or (random.choice(AUTO_TOPICS) if args.auto else None)
    if not topic:
        ap.error("--topic ver veya --auto kullan")
    script = generate(topic)
    out = config.OUT / "script.json"
    out.write_text(json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[script] {script['title']} -> {out} ({len(script['beats'])} beat)")


if __name__ == "__main__":
    main()
