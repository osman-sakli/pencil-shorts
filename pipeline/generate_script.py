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

━━━ FAMILY PETS ━━━
BISCUIT (family dog): Golden retriever puppy. Only says "Woof!", "Arf!", "Woof woof!". Runs in and causes chaos. Mira's best friend.
MITTENS (family cat): Orange tabby. Only says "Meow.", "Prrr...", "Hiss!". Appears in home/bedroom. Knocks things over.

━━━ SCHOOL FRIENDS ━━━
SNIP (pencil sharpener): Saf and Sem's cheerful blue school friend. Says "I can sharpen that idea!" / "Let me help!" Use in school scenes.

━━━ BACKGROUND RULES ━━━
  EACH BEAT must have a background that MATCHES where the scene is happening.
  CHANGE BACKGROUNDS OFTEN — move characters between locations every 2-3 beats!
  Available backgrounds: {backgrounds}
  - kitchen → breakfast, eating, cooking chaos
  - home → living room, family hanging out, TV time, couch, Biscuit sleeping, Mittens on table
  - bedroom → Bas's room, sleeping, hiding, private moments, Mittens napping
  - bathroom → Sem flooding, brushing teeth, bath time chaos
  - school → classroom, hallway, show and tell, science fair, Snip appears here
  - park → outdoor, picnic, playing, Biscuit running, chasing sticks
  - shop → grocery store, buying things, errands
  - street → outside, walking, neighborhood, school pickup

━━━ EPISODE FORMULA ━━━
  1. HOOK: Open MID-CHAOS. First line is already the problem. NO setup.
  2. Fast rapid-fire reactions — short lines, interruptions, pile-on
  3. Things get WORSE, not better. Every attempt fails.
  4. Saf asks one genius/dumb question that perfectly sums up the chaos
  5. Mira (or Biscuit/Mittens) does something that accidentally saves or ruins everything
  6. Mas delivers the one-liner that ends it all

━━━ WRITING RULES — CRITICAL ━━━
  MAX 7 WORDS PER LINE. Hard limit. 5-6 words is ideal.
  RAPID FIRE — no monologues. Ping-pong between characters.
  Use REACTIONS: "What?!" / "No no no no!" / "I TOLD you!" / "Uh oh."
  Sem ALWAYS mispronounces something. Mira NEVER uses full sentences.
  Physical comedy: characters describe what happened, don't explain.
  NO MORAL LESSONS stated out loud. Show don't tell.
  TEACH ENGLISH NATURALLY — clear vocabulary, natural expressions families use.
  40-44 seconds total. 9-10 beats. 60-80 words total.
  EACH LINE: 5-8 words. No line longer than 8 words.
  SURPRISE FACTOR: Every episode needs one unexpected twist or reveal nobody saw coming.

━━━ TITLE RULES — VIRAL CLICKBAIT ━━━
  Title must INSTANTLY make someone stop scrolling.
  ALWAYS include one of: Biscuit, Mittens, dog, cat, puppy, kitten, baby, OR a shocking verb.
  Use ALLCAPS on the shocking word. Max 8 words.
  PROVEN VIRAL FORMATS:
  - "[Pet] [SHOCKING VERB] [thing]!" → "Biscuit ATE Dad's Report Card!"
  - "[Character] CAUGHT [pet/baby] [doing thing]!" → "Mas CAUGHT Mittens Stealing Food!"
  - "Nobody Expected [character] to [shocking action]!" → "Nobody Expected Sem to WIN!"
  - "The [pet] KNOWS [secret/thing]!" → "The Dog KNOWS Our Secret!"
  - "[Baby/Pet] Just [shocking thing] 😱" → "Mira Just Said Her First Word 😱"

Return ONLY valid JSON. No markdown. No backticks. No explanations."""

PROMPT_TMPL = """Topic: {topic}

Characters available:
{roster}

Background options: {backgrounds}

CRITICAL RULES:
- OPEN MID-ACTION. Line 1 = already in chaos. Zero setup.
- MAX 7 WORDS per line. 5-6 is ideal.
- Every beat needs a "background" matching where scene happens.
- CHANGE BACKGROUND every 2-3 beats — characters move around!
- Sem is 4 years old — mispronounces words. Saf asks one funny question.
- Optional: include biscuit (dog sounds), mittens (cat sounds), snip (school friend).
- TEACH ENGLISH naturally — common family words, clear expressions.
- RAPID FIRE dialogue only. No speeches.

Generate JSON:
{{
  "title": "VIRAL TITLE — must feature a pet (Biscuit/Mittens/dog/cat) OR a shocking moment. MAX 8 words. Use ALLCAPS for one keyword. Make people NEED to click. Examples: 'Biscuit ATE Dad's Homework!', 'Mittens RUINED the Birthday Cake!', 'This DOG Knows Our Secret!', 'Sem BROKE the House Again!', 'Baby Mira SHOCKED Everyone Today!'",
  "background": "opening background label",
  "description": "2 punchy sentences social caption + emojis + call to action. Mention Biscuit or Mittens or both if they appear. Add 'Follow for more Pen Family chaos! 🖊️🐶🐱' at end.",
  "hashtags": ["#ThePenFamily", "#BiscuitTheDog", "#MittensTheCat", "#LearnEnglish", "#KidsCartoon", "#FamilyFun", "#Shorts", "#AnimatedFamily", "#CuteDogs", "#CuteCats", "#FunnyKids"],
  "beats": [
    {{"character": "id", "text": "MAX 7 WORDS", "emotion": "neutral|happy|angry|surprised|sad", "background": "scene_label"}}
  ]
}}

9-11 beats. Every beat has a background. RAPID FIRE. FUNNY. 40-45 SECONDS. 55-75 words."""

AUTO_TOPICS = [
    # 🎭 Unexpected twists
    "Sem accidentally calls the pizza place instead of grandpa and orders 40 pizzas",
    "Biscuit ate Oz's car keys and now has to confess — but only Mira understands him",
    "Bas goes viral for the wrong video and it's actually Oz dancing in the kitchen",
    "Sem swaps Oz's coffee with chocolate milk and Oz doesn't notice for the whole morning",
    "Mittens somehow learned to open the fridge and the whole family blames each other",
    "Saf's science experiment accidentally dyes Biscuit bright purple — the vet is shocked",
    "Oz tries to surprise the family but walks into his own surprise party instead",
    "Sem hides Mira's toy and Mira's first real word is 'SEM' in a very angry voice",
    "The family gets Biscuit a GPS collar and discovers he visits the neighbors every single day",
    "Bas posts a cooking video but Sem walks in wearing Oz's giant shoes and steals the show",

    # 🌀 Chaos escalators
    "Sem decides to give Mittens a bath — Mittens disagrees loudly",
    "Oz tries to fix one thing in the house and breaks five more things",
    "Mira learns to open doors and nobody is safe anymore",
    "Saf explains gravity to Sem using Oz's coffee mug — it does not end well",
    "Sem trades his lunch with Snip at school and gets something completely inedible",
    "Bas tries to teach Oz one social media trend — it takes the entire morning",
    "Mittens knocks something expensive off the shelf — everyone pretends not to notice",
    "Sem buries something important in the backyard and forgets what it was",
    "Biscuit chases Mittens through the house and they destroy Bas's room in 8 seconds",

    # 💡 English learning built in
    "Sem tries to use grown-up words he overheard but uses them all completely wrong",
    "Saf teaches Sem the difference between 'borrow' and 'steal' using Oz's cookie",
    "The family plays a word game at dinner and Sem invents words that somehow make sense",
    "Oz teaches Sem the word 'responsible' but Sem thinks it means something incredible",
    "Saf explains what 'patient' means to Sem — Sem immediately tries to test everyone's patience",
    "Sem learns 'apologize' and starts apologizing for things that haven't happened yet",

    # 😲 Surprise reveals
    "Mas already knew about every secret in the house — she reveals them all at breakfast",
    "It turns out Biscuit and Mittens have been best friends the whole time and hid it",
    "Sem's 'bad drawing' becomes famous online because Bas accidentally posted it",
    "Mira has been understanding everything this whole time — she finally shows it",
    "Grandpa Rex turns out to be secretly learning TikTok dances in his room",
    "Snip the sharpener comes to visit and has been to every country in the world",
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
    assert len(script["beats"]) >= 8, "En az 8 beat gerekir"
    script.setdefault("description", script.get("title", ""))
    script.setdefault("hashtags", [])
    for b in script["beats"]:
        if b["character"] not in config.CHARACTERS:
            b["character"] = list(config.CHARACTERS.keys())[0]
        if b.get("emotion") not in {"neutral", "happy", "angry", "surprised", "sad"}:
            b["emotion"] = "neutral"
        # New characters included in scripts now
        if b["character"] not in config.CHARACTERS:
            b["character"] = list(config.CHARACTERS.keys())[0]
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
