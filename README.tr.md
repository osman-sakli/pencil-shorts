# pencil-shorts

Kalemlerin kendi arasında yaşadığı **60-90 saniyelik** kısa çizgi filmleri **ucuza** ve
**otomatik** üreten short-form video pipeline'ı. Karakterler **tamamen kodla çizilir**
(kawaii tarz) — hiç resim/sprite yok, %100 tutarlı, video başı marjinal maliyet ~$0.

> 60-90 sn neden? TikTok Creator Rewards yalnızca 60 sn+ videolara ödeme yapar. Gelir
> önceliği yine de affiliate/TikTok Shop/sponsor; affiliate linki açıklamaya otomatik eklenir
> (`AFFILIATE_LINK`).

## Neden bu mimari
- **Remotion (render):** karakterler React/SVG bileşeni (`renderer/src/cast.tsx`).
  Ağız Rhubarb cue'larına göre değişir (lip-sync). Resim üretimi/Pexels gerekmez.
- **Python (orkestrasyon):** LLM senaryo, EdgeTTS ses, Rhubarb lip-sync, manifest.
- **Config-driven kadro:** `characters.yaml` (isim, kişilik, ses, renk).

## Akış
```
generate_script.py   LLM -> out/script.json
synthesize_voice.py  EdgeTTS -> out/beat_N.mp3 (+kelime zamanları), ffmpeg -> wav
lipsync.py           Rhubarb -> out/beat_N.cues.json (ağız şekilleri A-H,X)
build_manifest.py    -> out/manifest.json + out/audio_full.wav
renderer (Remotion)  manifest.json -> out/video.mp4
publish/upload.py    TikTok/Reels/Shorts (opsiyonel)
```
`pipeline/run.py` hepsini sırayla çalıştırır.

## Kurulum
- Python 3.11+, Node 20+, `ffmpeg`, `rhubarb` (lip-sync binary, PATH'te)
```bash
cp .env.example .env          # ANTHROPIC_API_KEY gir
cd pipeline && pip install -r requirements.txt && cd ..
cd renderer && npm install && cd ..
```
> Karakter sprite'ı / asset üretimi YOK. Kadro kodla geldiği için bu adım kalktı.
> Yeni karakter: `characters.yaml`'a giriş + `renderer/src/cast.tsx`'e bileşen ekle.

## Çalıştırma
```bash
python pipeline/run.py --topic "Kurşun kalem silgiyi kıskanıyor"
python pipeline/run.py --auto
# sadece render:
cd renderer && npx remotion render PencilShort ../out/video.mp4 --props=../out/manifest.json --public-dir=../
```
Çıktı: `out/video.mp4` (1080x1920, 30fps).

## Maliyet (video başı)
LLM (Haiku) ~$0.001 · EdgeTTS $0 · Rhubarb+render $0 · **Toplam ~$0**
(ElevenLabs sesine geçersen ~$0.10-0.30 eklenir.)

## Prod
`Dockerfile` + AWS (Fargate zamanlanmış görev) ile günlük otomatik üretim.
Ayrıntı: `PRODUCTION.md`.
