# 🎬 Çizgi Film Üretim Rehberi — "Bir Daha Asla" Kuralları

Bu belge, Yıldız bölümünde (Ep3) yaşanan ~$34'lık fazla harcamanın derslerinden
doğdu. **Buradaki sıraya harfiyen uyulursa bir bölüm ilk seferde doğru çıkar.**

---

## 1. Senaryo yazım kuralları (her beat için ZORUNLU alanlar)

```json
{
  "character": "sem",              // konuşan (characters.yaml'da kayıtlı olmalı)
  "emotion": "surprised",          // neutral|happy|angry|surprised|sad
  "background": "hill_night",      // environments'ta TANIMLI olmalı
  "music": "adventure",            // mystery|happy|calm|adventure
  "model": "full",                 // SADECE hero sahnelerde; yoksa mini
  "cast": ["sem", "twinkle"],      // kadro — MAX 3 önerilir, 4 sınır
  "text": "Look! It is GLOWING!",  // MAX 14 kelime; Mira ise SADECE agulamalar
  "action": "..."                  // aşağıdaki sahneleme kurallarına uygun
}
```

### Action (sahneleme) yazarken — kelimesi kelimesine kurallar

1. **SOLO/İKİLİ YAKIN PLAN yaz.** "The whole family..." / "everyone..." YASAK.
   Kalabalık duygusu gerekiyorsa: kadrodakiler dışındakileri "toward the
   off-screen family" diye çerçeve DIŞINA yaz.
2. **Kadroda olmayan hiçbir karakterin adını action'a yazma** — model onu
   uydurur (tahta kalem/insan çıkar).
3. Her karakteri İLK geçtiği yerde tarif sıfatıyla an: "the green toddler pen
   Sem". Çıplak isim yeterli değil.
4. Kamera talimatı ekle: "Close-up:", "Camera: slow push-in" vb.
5. İnsan çağıran kelimeler YASAK: family (kalabalık anlamında), town,
   neighborhood, suburban, people, kids, crowd.
6. Şarkı/ninni sahnesi normaldir — kod otomatik `generate_audio=False`'a
   düşer; özel bir şey yapma.
7. Mira'nın text'i yalnız bebek sesleri: "Gaga! Baba! Ooooh!" (+1-2 minik
   kelime: dada/mama).

### Sahne tipi → model seçimi (kanıtlanmış matris)

| Sahne tipi | Model | Başlangıç karesi |
|---|---|---|
| Solo/ikili yakın plan, iç mekân | mini | gerekmez |
| Solo/ikili yakın plan, gece dış | full | gerekmez |
| 3-4 karakter VEYA gece geniş açı | **full** | **ZORUNLU (kompozit)** |
| Saf gökyüzü / tek Twinkle | mini | gerekmez |
| Duygusal doruk (hero) | full | önerilir |

---

## 2. Komut sırası — PARA HARCAMAYAN adımlar önce

### Adım 0 — Ortam plakaları (yeni mekân varsa; ~$0.04/plaka, OpenAI)
```bash
# out/plates/<env>.png yoksa üret (composite_start için gerekli)
# prompt şablonu: "Empty 3D cartoon <mekan>, preschool TV cartoon style: ...
#                  NO characters, NO people — completely empty scene."
```

### Adım 1 — Kompozit başlangıç kareleri ($0)
```bash
python3 pipeline/composite_start.py --plate hill_night \
    --chars "oz:0.30:0.46,sem:0.50:0.22,twinkle:0.68:0.13" --out beat_33
# boy oranları: oz .46 | mas .42 | bas .36 | saf .30 | sem .22 | mira .15
#               biscuit .20 | twinkle .13
# senaryoda beat'e ekle: "start_frame": "out/startframes/beat_33.png"
```

### Adım 2 — Doğrulama + maliyet ($0, ZORUNLU)
```bash
python3 pipeline/generate_cartoon_seedance.py \
    --script examples/<bolum>.json --aspect 16:9 --dry-run
# Çıktıyı OKU: hata listesi boş mu? maliyet beklediğin gibi mi?
# out/dry_run_prompts.txt içinden 3-4 prompt'u gözle kontrol et.
```

### Adım 3 — Sesler ($0; OpenAI kısmı sentten ucuz)
```bash
python3 pipeline/generate_cartoon_seedance.py \
    --script examples/<bolum>.json --aspect 16:9 --beats 0
# --beats 0 hiç video üretmez ama TTS koşar; beat_N.mp3'leri DİNLE.
```

### Adım 4 — TEK SAHNE test (~$0.50-0.80)
```bash
python3 pipeline/generate_cartoon_seedance.py \
    --script examples/<bolum>.json --aspect 16:9 --no-tts --beats 1
# out/cartoon/beat_0.mp4'ü İZLE. Karakter doğru mu? İnsan var mı?
# Sorun varsa SENARYOYU düzelt, bu adımı tekrarla. İyi olmadan Adım 5'e GEÇME.
```

### Adım 5 — Tam üretim (bölüm başı ~$25-30, tek seferde)
```bash
python3 pipeline/generate_cartoon_seedance.py \
    --script examples/<bolum>.json --aspect 16:9 --no-tts --start 1
```

### Adım 6 — QC taraması ($0, ZORUNLU — yayından önce)
```bash
# kontak levhası çıkar, HER kareyi gözle tara: insan? sapma? bozuk klip?
# bozuk sahne varsa: --redo "5,12" ile SADECE onları yenile (~$0.8/sahne)
python3 pipeline/generate_cartoon_seedance.py \
    --script examples/<bolum>.json --aspect 16:9 --no-tts --redo "5,12"
```

### Adım 7 — Master + parçalar ($0)
```bash
python3 pipeline/build_cartoon_overlay.py --script examples/<bolum>.json --aspect 16:9
cd renderer && npx remotion render CartoonOverlay ../out/<bolum>_youtube.mp4 \
    --props=../out/cartoon_overlay_props.json --public-dir=../ && cd ..
python3 pipeline/split_cartoon.py --parts 4 --portrait
python3 pipeline/cut_highlights.py --ranges "9:10,22:23,41:42"
```

### Adım 8 — Yayın (Osman'ın YouTube onayından SONRA)
```bash
python3 pipeline/queue_parts.py --script examples/<bolum>.json --parts 4
python3 pipeline/queue_highlights.py --script examples/<bolum>.json \
    --files out/highlight_1.mp4,out/highlight_2.mp4,out/highlight_3.mp4 \
    --hooks "kanca 1,kanca 2,kanca 3"
# YouTube uzunu: upload.publish(['youtube'], ...) — SADECE Osman onayıyla
```

---

## 3. Asla yapma listesi

- ❌ Dry-run görmeden üretim başlatma
- ❌ Tek sahne testi geçmeden tam bölüm başlatma
- ❌ Gece + geniş açı + 3-4 karakter sahnesini kompozitsiz üretme
- ❌ Mini modele kalabalık/duygusal sahne verme
- ❌ QC yapmadan kuyruk doldurma / yayınlama
- ❌ `--redo` yerine bölümü baştan üretme (kliplerin hepsi out/cartoon/'da durur!)
- ❌ Süreklilik (@Video1) referansını QC'siz zincire sokma — kirlilik yayar

## 4. Bölüm ekonomisi (hedef)

| Kalem | Maliyet |
|---|---|
| 48 beat (40 mini + 8 full, 480p) | ~$24 |
| Tek sahne test + 2-3 redo payı | ~$3 |
| TTS + plakalar + kompozitler | <$1 |
| **Bölüm toplamı (5 güne yayılır)** | **~$28 → günde ~$5.60** |
