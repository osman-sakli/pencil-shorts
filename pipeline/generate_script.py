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

SYSTEM = """Sen kısa çizgi film senaristisin. Kalem karakterlerinin kendi aralarında
yaşadığı, 60-90 SANIYELIK komik, hikayeli kısa videolar yazıyorsun.

Uzunluk ve ritim (ÇOK ÖNEMLİ — gelir için video 60 sn üstü olmalı):
- Toplam metin 60-90 saniyede seslendirilebilecek uzunlukta: yaklaşık 150-220 kelime.
- 10-14 replik (beat). Replikler kısa ve tempolu olsun.
- İzleyiciyi sonuna kadar tutacak yapı:
  1) İLK REPLİK = güçlü KANCA (ilk 2 saniyede merak/çatışma kur).
  2) Ortada tırmanma: her 3-5 saniyede yeni bir mini-olay, çıkış, yanlış anlama.
  3) Sonlara doğru bir TWIST.
  4) Son replik = komik, tatmin edici kapanış (cliffhanger değil).
- Tek bir konuda kal, dağılma; tempoyu düşürme.

Diğer kurallar:
- SADECE verilen karakterleri kullan.
- Mizah: günlük durum komedisi, kıskançlık, rekabet, absürt yorumlar.
- Türkçe yaz, doğal konuşma dili.
- Ayrıca videonun açıklaması için kısa, çekici bir 'description' (1-2 cümle + birkaç emoji)
  ve 5-8 'hashtags' üret.

Yanıtı SADECE geçerli JSON olarak ver. Markdown, backtick veya açıklama EKLEME."""

PROMPT_TMPL = """Konu: {topic}

Kullanılabilir karakterler:
{roster}

Açılış sahnesi için arka plan seç: {backgrounds}

Bu şemada JSON üret:
{{
  "title": "kısa, merak uyandıran başlık",
  "background": "arka plan etiketi",
  "description": "izleyiciye hitap eden kısa açıklama + emoji",
  "hashtags": ["#...", "#..."],
  "beats": [
    {{"character": "karakter_id", "text": "replik", "emotion": "neutral"}}
  ]
}}

Unutma: 10-14 beat, 150-220 kelime, güçlü kanca + tırmanma + twist + komik kapanış."""

AUTO_TOPICS = [
    "Kurşun kalem silgiyi kıskanıyor",
    "Tükenmez kalem kendini ölümsüz sanıyor",
    "Kalemtraş herkesi açmakla tehdit ediyor",
    "Kalemler sınava kimin gireceğini tartışıyor",
    "Silgi bütün hataları silince kimse onu sevmiyor",
    "Yeni gelen renkli kalem kadroyu karıştırıyor",
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
