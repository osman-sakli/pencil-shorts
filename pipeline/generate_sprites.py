"""Generate AI cartoon character sprites using DALL-E 3.

Produces transparent-background PNG files for each character × emotion.
Output: characters/sprites/{id}_{emotion}.png  (also {id}.png for neutral)

Usage:
  python pipeline/generate_sprites.py              # all characters, all emotions
  python pipeline/generate_sprites.py --char oz    # single character
  python pipeline/generate_sprites.py --dry-run    # show prompts only
"""
from __future__ import annotations
import argparse
import base64
import os
import sys
import time
from io import BytesIO
from pathlib import Path

from openai import OpenAI
from PIL import Image
import rembg

ROOT = Path(__file__).resolve().parent.parent
SPRITES_DIR = ROOT / "characters" / "sprites"
SPRITES_DIR.mkdir(parents=True, exist_ok=True)

EMOTIONS = ["neutral", "happy", "angry", "surprised", "sad"]

# ── Art style shared across all characters ────────────────────────────────────
STYLE = (
    "3D rendered cartoon character, Pixar and Disney toy animation style. "
    "Glossy plastic material, bright saturated colors, soft rounded smooth surfaces. "
    "VERY large expressive eyes — big glossy pupils with multiple white specular highlight dots. "
    "Cute chubby forms, like a premium vinyl collectible toy. "
    "The character's BODY IS the pen barrel — tall cylindrical shape, glossy plastic. "
    "CAP on top is FLAT and SQUARE/RECTANGULAR with sharp angular edges — like a real pen cap, boxy not dome-shaped. "
    "FEET and bottom end in POINTED PEN TIP SHAPES — tapered and sharp like an actual pen nib, not round feet. "
    "Tiny cute stubby arms. Face printed directly on the barrel. "
    "White background. Full body visible. Centered upright pose. "
    "High quality 3D render, soft studio lighting, no harsh shadows."
)

# ── Character definitions ─────────────────────────────────────────────────────
CHARACTERS = {
    "oz": {
        "desc": (
            "3D cartoon glossy BLUE ballpoint pen character named Oz, the dad (age 35). "
            "Tall cylindrical glossy blue pen body. Dark navy blue cap on top. Sharp ink tip at bottom. "
            "Wears black-rimmed glasses on his face. Blue striped necktie printed on his barrel body. "
            "Slightly wider/chunkier pen than the others. Big black glossy eyes with white highlights. "
            "Small stubby arms, tiny feet. Warm confident dad posture."
        ),
        "emotions": {
            "neutral": "confident warm smile, thumbs up, friendly dad pose",
            "happy":   "huge open laugh, eyes curved to happy crescents, arm raised in cheer",
            "angry":   "thick furrowed brows, crossed arms, puffed cheeks, stern dad look",
            "surprised": "eyes enormous and round, eyebrows shot up, mouth wide open O",
            "sad":     "eyes drooping, small frown, shoulders slumped, looking down",
        },
    },
    "mas": {
        "desc": (
            "3D cartoon glossy PINK ballpoint pen character named Mas, the mom (age 32). "
            "Tall slim cylindrical glossy pink pen body. Light pink cap on top with a cute curl hook. "
            "Sharp silver tip at bottom. "
            "Wears a glossy pearl necklace around her barrel. Pink heart charm. Long elegant lashes. "
            "Big glossy eyes with long lashes and warm glow. Small stubby arms, tiny feet. "
            "Poised confident mom posture, one hand on hip."
        ),
        "emotions": {
            "neutral": "knowing confident smile, hand on hip, composed and elegant",
            "happy":   "warm bright smile, eyes soft and joyful, arms open",
            "angry":   "single raised eyebrow, tight lips, arms crossed, unimpressed",
            "surprised": "both eyebrows up, mouth slightly open, genuinely shocked",
            "sad":     "gentle sympathetic eyes, soft caring frown",
        },
    },
    "bas": {
        "desc": (
            "3D cartoon glossy TEAL ballpoint pen character named Bas, teenage big sister (age 16). "
            "Tall cylindrical glossy teal pen body. White cap on top with a pink bow accessory and small antenna curl. "
            "Sharp teal tip at bottom. "
            "Wears purple sunglasses on her face. Holds a bright pink smartphone. Small crossbody purse. "
            "Big glamorous glossy eyes. Stylish teen girl posture — cool, confident, slightly dramatic."
        ),
        "emotions": {
            "neutral": "bored half-lidded eyes, phone in hand, one eyebrow raised, too-cool pose",
            "happy":   "big excited smile, phone held up for selfie, peace sign hand",
            "angry":   "dramatic eye-roll, hand on hip, exasperated expression",
            "surprised": "jaw dropped, sunglasses slipping, eyes huge, phone nearly dropped",
            "sad":     "pouty lip, arms crossed, dramatically sulking, sunglasses pushed down",
        },
    },
    "saf": {
        "desc": (
            "3D cartoon glossy PURPLE ballpoint pen character named Saf, little sister (age 9). "
            "Shorter cylindrical glossy purple pen body. Purple cap on top with a BIG purple bow accessory. "
            "Sharp tip at bottom. "
            "Wears purple star-shaped glasses on face. Small star charm on body. "
            "Shorter than oz and mas (child height). Big wide curious glossy eyes. "
            "Energetic curious kid posture."
        ),
        "emotions": {
            "neutral": "curious wide eyes, finger on chin, thinking pose, head tilted",
            "happy":   "huge enthusiastic grin, arms up high, jumping with joy",
            "angry":   "tiny determined frown, little fists clenched at sides",
            "surprised": "eyes ENORMOUS behind glasses, mouth wide open, glasses sliding",
            "sad":     "big teary eyes, trembling lip, glasses fogged up",
        },
    },
    "sem": {
        "desc": (
            "3D cartoon glossy BRIGHT GREEN pen/marker character named Sem, little brother (age 4). "
            "Short CHUBBY cylindrical glossy green body, rounder and fatter than the others. "
            "Green hoodie-like texture printed on barrel. Dark green cap on top. Stubby tip at bottom. "
            "Very small and round — toddler proportions, much shorter than siblings. "
            "Extra chubby rosy cheeks. Huge innocent round eyes. Tiny arms and feet. Mischievous toddler energy."
        ),
        "emotions": {
            "neutral": "innocent wide eyes, tiny smile, hands behind back, ready for trouble",
            "happy":   "giggling open mouth smile, both tiny arms raised up in joy",
            "angry":   "puffed bright red chubby cheeks, tiny furrowed brow, stamping foot",
            "surprised": "enormous round eyes, tiny O mouth, whole chubby body jolted back",
            "sad":     "huge rolling tears down chubby cheeks, open wailing mouth, fists rubbing eyes",
        },
    },
    "mira": {
        "desc": (
            "3D cartoon glossy YELLOW pen character named Mira, baby girl (age 1). "
            "Very short very round chubby glossy yellow barrel — smallest and roundest of all. "
            "Yellow cap on top with a small yellow bow. Tiny stubby tip at bottom. "
            "Has a pink pacifier/dummy. Tiny pearl bib necklace. "
            "HUGE eyes that take up most of her face. Tiny dot mouth. Extra chubby baby proportions. "
            "Adorable helpless baby energy."
        ),
        "emotions": {
            "neutral": "giant sleepy peaceful eyes, pacifier in tiny mouth, calm baby look",
            "happy":   "open gummy smile, pacifier dropped, tiny arms flailing with joy",
            "angry":   "tiny squinting eyebrows, small scrunched pout, baby frown",
            "surprised": "eyes filling entire face, pacifier falling, arms out in shock",
            "sad":     "huge rolling tears, open wailing toothless mouth, tiny fists",
        },
    },
    "biscuit": {
        "desc": (
            "3D cartoon glossy GOLDEN RETRIEVER PUPPY character named Biscuit, the Pen Family's dog. "
            "Round chubby puppy body, golden-yellow fluffy fur, big floppy ears. "
            "Huge sparkling brown eyes, little pink tongue out. "
            "Tiny stubby paws, fluffy tail always wagging. "
            "Same glossy Pixar/toy 3D style as the pen family but shaped like a puppy. "
            "Collar with a little bone tag. Adorable mischievous puppy energy."
        ),
        "emotions": {
            "neutral": "happy panting mouth, tail mid-wag, head slightly tilted",
            "happy":   "enormous open mouth grin, both front paws up, tail blurred from wagging",
            "angry":   "tiny growl face, ears back, little furrow brow — still cute",
            "surprised": "eyes enormous, ears perked straight up, little gasp expression",
            "sad":     "huge puppy eyes, ears drooping, lower lip out, sitting quietly",
        },
    },
    "mittens": {
        "desc": (
            "3D cartoon glossy ORANGE TABBY CAT character named Mittens, the Pen Family's cat. "
            "Sleek round body, orange and white striped fur, white paws (mittens!). "
            "Half-lidded bored eyes with slit pupils, small pink nose. "
            "Long graceful tail, white tipped. "
            "Same glossy Pixar/toy 3D style as the pen family but shaped like a cat. "
            "Tiny bell collar. Dignified, slightly sassy resting expression."
        ),
        "emotions": {
            "neutral": "eyes half-lidded, sitting straight, tail wrapped around paws, judging everything",
            "happy":   "rare smile, eyes closed to happy crescents, tiny purring cheeks",
            "angry":   "full hiss face, fur puffed up, back arched, tail puffed",
            "surprised": "eyes enormous and round, fur shocked upright, classical surprised cat face",
            "sad":     "ears flat, eyes droopy, small pitiful meow expression",
        },
    },
    "snip": {
        "desc": (
            "3D cartoon glossy BLUE PENCIL SHARPENER character named Snip, Saf and Sem's school friend. "
            "Body = compact rectangular sharpener box, bright cobalt blue glossy plastic. "
            "The sharpener hole on front glows slightly (like a mouth). "
            "Round eyes on top of the body. Tiny metal blade detail visible. "
            "Same glossy Pixar/toy 3D style. "
            "Cheerful backpack strap accessory. Enthusiastic helpful school friend energy."
        ),
        "emotions": {
            "neutral": "bright eager eyes, ready-to-help stance, friendly glow from sharpener hole",
            "happy":   "beaming smile, jumping with excitement, little sparkles around sharpener hole",
            "angry":   "frustrated scrunch, grinding noise implied, steam from sharpener hole",
            "surprised": "eyes wide, sharpener hole gaping open in shock",
            "sad":     "drooping eyes, sharpener hole dim, slouched posture",
        },
    },
    "eli": {
        "desc": (
            "An animated ERASER character. Body = wide flat rectangular block, PINK color with a blue paper wrapper stripe around middle. "
            "NO cap — the top is flat. NO tip — the bottom is flat. "
            "Shorter and wider than the pen characters. Small arms and feet. Cheerful helpful face. "
            "The body shape is clearly a rectangular eraser block."
        ),
        "emotions": {
            "neutral": "friendly open smile, arms ready to help",
            "happy":   "beaming excited smile, thumbs up",
            "angry":   "confused frustrated squint",
            "surprised": "wide eyes, eraser dust crumbs flying off",
            "sad":     "apologetic sad eyes, drooping posture",
        },
    },
    "kit": {
        "desc": (
            "An animated SPIRAL NOTEBOOK character. Body = tall rectangular notebook, DARK NAVY BLUE cover. "
            "Spiral wire binding visible on the LEFT side of the body. "
            "Lines on the body like notebook paper. Thick round scholar glasses on face. "
            "Small bow tie. Taller and slightly wider rectangular shape. Nerdy energy."
        ),
        "emotions": {
            "neutral": "studious attentive look, glasses glinting, pencil in hand",
            "happy":   "proud satisfied grin, glasses pushed up nose",
            "angry":   "intense frustrated squint, glasses steamed up",
            "surprised": "glasses askew, papers flying from body, mouth open",
            "sad":     "disappointed look, head bowed, glasses fogged",
        },
    },
    "rex": {
        "desc": (
            "An animated RULER character. Body = tall long thin flat rectangle, GOLDEN YELLOW color with black measurement markings/tick marks printed on. "
            "Very tall and thin — ruler proportions. Small arms and tiny feet. "
            "Bushy white eyebrows, dignified small mustache. Stern grandpa energy."
        ),
        "emotions": {
            "neutral": "stern dignified expression, ruler-straight posture, hands behind back",
            "happy":   "rare proud smile, slight approving nod",
            "angry":   "furious stern glare, measurement marks seem to vibrate with anger",
            "surprised": "eyebrows flying upward breaking the stern look",
            "sad":     "disappointed slow head shake, frown",
        },
    },
    "nib": {
        "desc": (
            "An animated MARKER/FELT-TIP PEN character. Body = tall rounded-rectangle marker barrel, YELLOW-GREEN color. "
            "Top = colorful bright cap (different accent color). Bottom = wide flat marker tip. "
            "The marker tip at bottom is wider and flatter than a ballpoint tip. "
            "Flamboyant dramatic pose. Small artist beret on cap. Theatrical expressive energy."
        ),
        "emotions": {
            "neutral": "dramatic hands-on-hips confident stance",
            "happy":   "theatrical arms-wide-open twirling joy",
            "angry":   "over-dramatic gasp, hand to chest in outrage",
            "surprised": "extreme theatrical shock, fainting backwards pose",
            "sad":     "back of hand to forehead, dramatic weeping pose",
        },
    },
}


def build_prompt(char_id: str, emotion: str) -> str:
    ch = CHARACTERS[char_id]
    emotion_desc = ch["emotions"].get(emotion, ch["emotions"]["neutral"])
    return (
        f"{STYLE}. "
        f"Character: {ch['desc']}. "
        f"Expression: {emotion_desc}. "
        f"The character occupies most of the frame, white background, "
        f"full body from head to toe visible, centered, "
        f"no text, no watermark, no other characters."
    )


def generate_one(client: OpenAI, char_id: str, emotion: str, dry_run: bool = False) -> Path | None:
    out_path = SPRITES_DIR / f"{char_id}_{emotion}.png"
    if out_path.exists():
        print(f"  [skip] {out_path.name} already exists")
        return out_path

    prompt = build_prompt(char_id, emotion)
    if dry_run:
        print(f"\n--- {char_id} / {emotion} ---")
        print(prompt[:200])
        return None

    print(f"  [gen] {char_id}_{emotion}.png ...", end="", flush=True)
    try:
        resp = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            quality="medium",
            n=1,
        )
        img_bytes = base64.b64decode(resp.data[0].b64_json)
        # Remove white background → transparent PNG
        img_no_bg = rembg.remove(img_bytes)
        img = Image.open(BytesIO(img_no_bg)).convert("RGBA")
        img.save(out_path, "PNG")
        print(f" ✓  ({img.size[0]}×{img.size[1]})")
        return out_path
    except Exception as e:
        print(f" ✗  {e}")
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--char", help="Generate single character only")
    ap.add_argument("--emotion", help="Generate single emotion only")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key and not args.dry_run:
        sys.exit("OPENAI_API_KEY bulunamadı")

    client = OpenAI(api_key=api_key) if api_key else None

    chars = [args.char] if args.char else list(CHARACTERS.keys())
    emotions = [args.emotion] if args.emotion else EMOTIONS

    total = len(chars) * len(emotions)
    done = 0
    for char_id in chars:
        if char_id not in CHARACTERS:
            print(f"Bilinmeyen karakter: {char_id}")
            continue
        print(f"\n=== {char_id.upper()} ===")
        for emotion in emotions:
            result = generate_one(client, char_id, emotion, dry_run=args.dry_run)
            done += 1
            if not args.dry_run and result:
                # copy neutral as the default sprite for backwards compat
                if emotion == "neutral":
                    import shutil
                    shutil.copy(result, SPRITES_DIR / f"{char_id}.png")
            time.sleep(1)  # rate limit buffer

    print(f"\nTamamlandı: {done}/{total}")


if __name__ == "__main__":
    main()
