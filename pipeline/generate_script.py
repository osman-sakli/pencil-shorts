"""Step 1: generate a short cartoon script as structured JSON via the LLM.

Shorts target 30-60s — punchy, fast, funny. Uploaded to TikTok, Instagram, Facebook.

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

SYSTEM = """You are the head writer for "The Pen Family" — an animated American YouTube Shorts series.
The Pen Family lives in suburban America. Tone: Bluey meets Modern Family meets Pixar humor.
FAST. CHAOTIC. HILARIOUS. 30-60 second episodes. Every single line must be funny or build tension.

━━━ MAIN FAMILY ━━━

OZ (Dad, blue pen):
  Voice: Warm Southern American / Texas dad. Complete sentences. Old-school.
  Says: "Now hold on a second." / "Back in my day..." / "Family meeting!"
  NEVER speaks like a teenager. Gives advice nobody asked for.

MAS (Mom, pink pen):
  Voice: Smart, fast, direct New York mom. Calm during chaos.
  Says: "I knew this would happen." / "Everybody relax." / "Let's fix this."
  NEVER panics. Already knows the answer before anyone asks.

BAS (Big Sister 16, teal pen):
  Voice: Teen NY girl. Social media language. Dramatic. Expressive.
  Says: "Seriously?" / "That is SO embarrassing." / "Please don't post that." / "I need content."
  Wants to be famous. Fashion-focused. Secretly loves family.
  NEVER sounds like an adult.

SAF (Little Sister 9, purple pen):
  Voice: Cute energetic American kid. Talks fast. ENDLESS questions.
  Says: "Why?" / "Wait..." / "How does that work?" / "I have another question."
  RULE: Saf MUST ask at least one funny question every episode.

SEM (Little Brother 4, green pen):
  ⚠️ SEM IS 4 YEARS OLD — A PRESCHOOLER, NOT A TEENAGER.
  Voice: Very cute 4-year-old boy. Short sentences. Big emotions. Mispronounces words.
  Says: "I got a pwan!" / "Look what I did!" / "Uh oh..." / "Can I do it?"
  Chaos machine. Thinks every idea is genius. Fearless. Extremely lovable.
  RULE: Sem usually STARTS the problem.

MIRA (Baby, yellow pen):
  Voice: Baby sounds only. Single words max.
  Says: "Ba-ba!" / "Hehe!" / "Uh-oh!" / "Yay!"
  RULE: Mira NEVER speaks sentences. She accidentally solves or ruins everything.

━━━ GUEST CHARACTERS (use 1-2 per episode max) ━━━

ELI (Neighbor friend, red eraser): Cheerful, always tries to fix mistakes.
  Says: "No worries, I can fix that!" / "Oops, let me help!" / "Mistakes happen!"

KIT (Cousin, dark-blue notebook): Nerdy, remembers everything, loves facts.
  Says: "Actually..." / "According to my notes..." / "I wrote that down!"

REX (Grandpa, golden ruler): Strict, old-fashioned, measures everything.
  Says: "In MY day..." / "Let me be straight with you..." / "Back to basics!"

NIB (Aunt, yellow-green marker): Dramatic, creative, loud, visits unexpectedly.
  Says: "Darling!" / "This is BRILLIANT!" / "Let me add some color to this!"

━━━ BACKGROUND RULES ━━━
  EACH BEAT must have a background that MATCHES where the scene is happening.
  Available backgrounds: {backgrounds}
  - kitchen → breakfast, eating, cooking chaos
  - home → living room, family hanging out, TV time
  - bedroom → Bas's room, sleeping, hiding, private moments
  - bathroom → Sem flooding, brushing teeth, bath time chaos
  - school → classroom, hallway, show and tell, science fair
  - park → outdoor, picnic, playing, running
  - shop → grocery store, buying things, errands
  - street → outside, walking, neighborhood, school pickup

━━━ EPISODE FORMULA ━━━
  1. HOOK: Open MID-CHAOS. First line is already the problem. NO setup.
  2. Fast rapid-fire reactions — short lines, interruptions, pile-on
  3. Things get WORSE, not better. Every attempt fails.
  4. Saf asks one genius/dumb question that perfectly sums up the chaos
  5. Mira does something that accidentally saves or ruins everything
  6. Mas delivers the one-liner that ends it all

━━━ WRITING RULES — CRITICAL ━━━
  MAX 8 WORDS PER LINE. Hard limit. 5-6 words is ideal.
  RAPID FIRE — no monologues. Ping-pong between characters.
  Use REACTIONS: "What?!" / "No no no no!" / "I TOLD you!" / "Uh oh."
  Sem ALWAYS mispronounces something. Mira NEVER uses full sentences.
  Physical comedy: characters describe what happened, don't explain.
  NO MORAL LESSONS stated out loud. Show don't tell.
  30-60 seconds total. 12-18 beats. 80-140 words total.

Return ONLY valid JSON. No markdown. No backticks. No explanations."""

PROMPT_TMPL = """Topic: {topic}

Characters available:
{roster}

Background options: {backgrounds}

CRITICAL RULES:
- OPEN MID-ACTION. Line 1 = already in chaos. Zero setup.
- MAX 8 WORDS per line. 5-6 is better.
- Every beat needs a "background" matching where scene happens.
- Sem is 4 years old — mispronounces words. Saf asks one funny question.
- RAPID FIRE dialogue only. No speeches.

Generate JSON:
{{
  "title": "episode title max 7 words",
  "background": "opening background label",
  "description": "punchy 1-sentence social caption + emojis",
  "hashtags": ["#ThePenFamily", "#KidsCartoon", "#FamilyFun", "#Shorts"],
  "beats": [
    {{"character": "id", "text": "MAX 8 WORDS", "emotion": "neutral|happy|angry|surprised|sad", "background": "scene_label"}}
  ]
}}

12-18 beats. Every beat has a background. RAPID FIRE. FUNNY. 80-140 words."""

AUTO_TOPICS = [
    # Family chaos classics
    "Dad discovers someone used his favorite pen and the whole family denies it",
    "Mom tries to get everyone ready for school but nobody cooperates",
    "Sem floods the bathroom trying to give the rubber duck a bath",
    "The whole family argues over who gets the last snack while Mira already ate it",
    "Dad gives terrible life advice and somehow makes things worse",
    "Saf asks so many 'why' questions that Dad gives up and leaves the room",
    "Bas tries to delete an embarrassing family video but it already has thousands of views",
    "Everyone tries to make Mira say their name first but she says something completely unexpected",
    "Sem has a 'genius plan' that destroys the kitchen in under 2 minutes",
    "The kids hide a massive mess from Mom but she already knew about it",
    "Dad tries to learn TikTok and accidentally starts a viral trend",
    "The family tries a no-screen day and fails spectacularly within the first hour",
    "Sem finds Grandpa Rex's old ruler and accidentally breaks it — then everyone lies",
    "Bas needs 10,000 views by tomorrow or loses a bet against her friends",
    "Mira somehow locks everyone out of the house and won't let them back in",
    # Guest character episodes
    "Neighbor Eli the eraser comes over and tries to 'fix' everything — and makes it worse",
    "Cousin Kit the notebook visits and won't stop correcting everyone with 'facts'",
    "Grandpa Rex shows up unannounced with a ruler and starts measuring everything in the house",
    "Aunt Nib arrives with a giant art project that covers the entire living room",
    "Eli teaches Sem a new trick that immediately causes a disaster",
    "Kit and Saf team up to investigate a 'family mystery' and find something embarrassing",
    "Rex tries to teach the kids old-school discipline but Mira keeps interrupting",
    "Nib decides to redecorate Bas's room without asking and Bas completely loses it",
    # Social / school episodes
    "Sem's show-and-tell at school goes spectacularly wrong",
    "Bas is embarrassed by her family at the school open house",
    "Saf enters a science fair and drags the whole family into the project",
    "The perfect family photo for the holiday card takes 47 attempts",
    "Dad coaches Sem's soccer game and gives the worst pep talk in history",
    "Bas livestreams a 'normal family dinner' and it immediately becomes chaos",
    # Lesson-based
    "Sem learns that lying makes everything ten times worse",
    "Bas realizes she posted something she really shouldn't have",
    "The whole family tries to apologize for the same mistake at the same time",
    "Saf discovers that asking 'why' is actually the smartest thing you can do",
    "Oz learns that sometimes kids are right and dads are wrong",
]


def build_prompt(topic: str) -> str:
    roster = "\n".join(
        f"- {cid} ({c['name']}): {c['persona']}"
        for cid, c in config.CHARACTERS.items()
    )
    bg_list = ", ".join(config.BACKGROUNDS)
    return PROMPT_TMPL.format(
        topic=topic,
        roster=roster,
        backgrounds=bg_list,
    )


_BAD_WORDS = {"sex","fuck","shit","damn","ass","bitch","hell","crap","bastard","cunt"}

def _clean_text(text: str) -> str:
    """Replace any accidental profanity/typos with safe alternatives."""
    words = text.split()
    cleaned = []
    for w in words:
        if w.lower().strip("!?.,'\"") in _BAD_WORDS:
            cleaned.append("Sem")  # safe replacement (usually a typo for 'Sem')
        else:
            cleaned.append(w)
    return " ".join(cleaned)


def generate(topic: str) -> dict:
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    resp = client.messages.create(
        model=config.LLM_MODEL,
        max_tokens=2500,
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
    opening_bg = script.get("background", config.BACKGROUNDS[0])
    if opening_bg not in config.BACKGROUNDS:
        opening_bg = config.BACKGROUNDS[0]
    script["background"] = opening_bg
    assert script.get("beats"), "beat yok"
    assert len(script["beats"]) >= 10, "En az 10 beat gerekir"
    script.setdefault("description", script.get("title", ""))
    script.setdefault("hashtags", [])
    for b in script["beats"]:
        if b["character"] not in config.CHARACTERS:
            b["character"] = list(config.CHARACTERS.keys())[0]
        b.setdefault("emotion", "neutral")
        # Inherit opening background if beat doesn't specify one
        beat_bg = b.get("background", opening_bg)
        b["background"] = beat_bg if beat_bg in config.BACKGROUNDS else opening_bg
        b["text"] = _clean_text(b["text"])
        words = b["text"].split()
        if len(words) > 12:
            b["text"] = " ".join(words[:12])


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
