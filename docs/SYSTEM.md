# 🎬 THE PEN FAMILY — İÇERİK SİSTEMİ (v2, 2026-07-07'den geçerli)

> Osman'ın direktifi (2026-07-07): "Daha dikkat çekici 3D sahneler ve scriptler.
> Yaratıcı muhteşem konular. Görsel sahneler harika olmalı. Her hafta zorla
> yaratıcı senaryolarla gel. Karakterlerim ünlensin, tutarlı olsun, sesleri
> harika olsun. Seedance'i harika kullan, boşluk bırakma."
>
> **Bu belge kuraldır. Her yeni bölümde buna harfiyen uyulur.** Bu sistem
> **Cuma'dan (band bölümü) SONRAKİ** bölümde devreye girer.

---

## 1. YAYIN MODELİ — "5 günde bir sinematik film"

Her **5 günde bir** benzersiz, muhteşem, ~**4:30–5 dakikalık sinematik kısa
film** üretilir. Bu film, ayrı ayrı da izlenebilen ama **birleşince tam bir
film oluşturan** bölümlerden (chapter) kurulur.

### Bölümün iç yapısı
- Film **4–5 adet "65 saniyelik chapter"e** bölünür.
- Her chapter **kendi içinde konu bütünlüğü** olan bir sahne dizisidir
  (kendi mini-kancası, gelişimi, mini-cliffhanger'ı var) — tek başına
  izlenince bile tatmin eder AMA sıradakini merak ettirir.
- 4–5 chapter × 65 sn ≈ 4:20–5:25 → hedef **4:30–5:00**.

### İki ayrı short akışı
| Akış | Platform | Süre | Sıklık | İçerik |
|---|---|---|---|---|
| **A) TikTok chapter** | TikTok | **65 sn** | Günde 1 (sabah 06:00) | Filmin o günkü chapter'ı (60 sn+ = para) |
| **B) Sinematik highlight** | Facebook + YouTube Shorts + Instagram | **20–25 sn** | **Günde 2 (06:00 ve 18:00)** | Filmin en çarpıcı tek anları |

### 5 günlük döngü takvimi (örnek)
```
Gün 1  06:00 TikTok Chapter 1 (65s)   | 06:00 Highlight #1 (FB/YT/IG)  | 18:00 Highlight #2
Gün 2  06:00 TikTok Chapter 2 (65s)   | 06:00 Highlight #3             | 18:00 Highlight #4
Gün 3  06:00 TikTok Chapter 3 (65s)   | 06:00 Highlight #5             | 18:00 Highlight #6
Gün 4  06:00 TikTok Chapter 4 (65s)   | 06:00 Highlight #7             | 18:00 Highlight #8
Gün 5  06:00 TikTok Chapter 5 (65s)   | 06:00 Highlight #9             | 18:00 Highlight #10
```
→ Döngü başına: **5 TikTok chapter + 10 sinematik highlight** (2/gün × 5).
→ Ayrıca uzun film YouTube'a tam hâliyle yüklenir (bölüm çıkışında).

### Bunun için kurulacak otomasyon (Cuma sonrası)
- Mevcut S3 kuyruk + 2 scheduler'a **3. slot** eklenir: `PUBLISH_SLOT=am2`
  (sabah 06:00 ikinci highlight) veya pm'i 18:00'e çek + yeni sabah highlight.
- Net: **06:00** → TikTok chapter + FB/YT/IG highlight (2 iş), **18:00** →
  FB/YT/IG highlight (1 iş). Yani sabah 2, akşam 1 highlight değil —
  Osman "günde iki short" dedi: **06:00 highlight + 18:00 highlight** = 2/gün
  (FB/YT/IG), TikTok bunlardan ayrı sabah chapter'ı.
- `queue_highlights.py` her döngüde 10 highlight'ı am/pm slotlarıyla dizecek.

---

## 2. YARATICI STANDART — "milyonlar izlesin"

Cookie Mystery / Little Star sevimli ama **jenerik**. Milyonluk izlenme için
her konu şu 4 kancadan **en az 2'sini** taşımalı:

1. **GÖRSEL ŞOK** — ilk 2 saniyede "vay bu ne?!" dedirten bir görüntü
   (dev bir şey, parlayan bir şey, ters dönen dünya, renk patlaması).
2. **MERAK BOŞLUĞU** — cevabı geciken bir soru ("O kutudan ne çıkacak?").
3. **DUYGU** — kayıp/kavuşma, korku/güven, yalnızlık/dostluk (Little Star'ın
   işe yaraması buydu).
4. **TEKRARLANAN BÜYÜ** — çocuğun tekrar tekrar izleyeceği bir öğe (şarkı,
   dönüşüm, bir replik, bir dans).

### Sahne görselliği (Seedance'i "harika" kullanmak)
- **Her chapter en az 1 "hero shot"** içerir: geniş açı, sinematik ışık,
  parçacık efekti (glitter/kar/ateşböceği/yaprak), full model 720p opsiyonel.
- **Kamera dili zorunlu**: her action'da kamera talimatı ("slow push-in",
  "sweeping crane up", "over-the-shoulder"). Statik plan yok.
- **Işık atmosferi**: gece=derin mavi+altın; büyü=parlayan renk; sıcak
  an=altın saat. Ortam tarifleri (`environments`) bu paleti sabitler.
- **Boşluk bırakma**: her karede ya karakter aksiyonu ya çevre hareketi
  (rüzgâr, ışık, parçacık) olsun — durağan/boş kare yasak.
- **Geçişler**: chapter sonları mini-cliffhanger + görsel kanca ile bitsin.

### Karakter kuralları (ünlensin + tutarlı) — CARTOON_PLAYBOOK.md ile birlikte
- Sertleştirilmiş prompt zorunlu: per-karakter kilit, kalem-ucu ayak, karakter
  sayı kilidi, HARD_CONSTRAINTS, sabit CHAR_SEED (bkz. generate_cartoon_seedance.py).
- Boy sırası her sahnede: Oz > Mas > Bas > Saf > Sem > Mira; Twinkle en küçük.
- İnsan ASLA (çerçeve/TV/yansıma dahil). Jenerik tahta kalem yok.
- **İmza öğeleri** karakteri ünlü yapar: Sem'in "Boom boom!", Oz'un "Family
  meeting!", Mira'nın agulaması, Twinkle'ın "Twinkle twinkle!". Her bölümde
  bu imza replikler tekrarlanır → tanınırlık.

### Ses standardı ("harika olsun")
- Şu an: eski Edge sesleri (Osman OpenAI'yi beğenmedi) + duygu modülasyonu.
- Hedef: karakter yaşına birebir uygun, doğal, tutarlı. Kalite yetmezse
  **ElevenLabs** (en doğal, premium) tek karakter bazında denenir — ama ses
  KİMLİĞİ bölümler arası ASLA değişmez.
- Şarkılı bölümlerde nakarat sabit → çocuk ezberler (tekrar izleme).

---

## 3. ÜRETİM DİSİPLİNİ (para yakmadan) — CARTOON_PLAYBOOK.md'nin özeti
1. Senaryo yaz (bu belgedeki yaratıcı + görsel standartlara uy).
2. `--dry-run` (BEDAVA): doğrulama + maliyet. Hata varsa üretme.
3. Sesleri üret + DİNLE.
4. TEK sahne testi (~$0.80) → İZLE. İyi değilse senaryoyu düzelt, tekrar.
5. Tam üretim (tek seferde, ~$25–30). **Bakiye önden yüklü olsun** (ortada
   bitmesin — Osman büyük tek yükleme yapacak).
6. QC taraması: her kareyi insan/kayma/boşluk için tara. Bozuk → `--redo "N"`.
7. Master + chapter'lar (65s, TikTok 60s+ GARANTİ) + 10 highlight (20-25s).
8. Uzun YouTube = Osman onayıyla. Chapter/highlight = otomatik kuyruk.

### Bölüm ekonomisi
- ~40-48 beat, 40p mini + hero'lar full 480p → ~$25-30/bölüm.
- 5 güne yayılır → günde ~$5-6. Büyük tek yükleme kesintiyi önler.

---

## 4. YARATICI KONU BANKASI (sıradaki bölümler — görsel güçlü, kancalı)

Her biri 4:30-5 dk, 4-5 chapter'a bölünür. ✅ = yapıldı.

| # | Başlık | Kanca | Neden görsel bomba |
|---|---|---|---|
| ✅ | The Little Star Who Fell | Düşen yıldızı eve götürme | gece+glitter, duygu |
| 🔨 | The Pencil Family Band | Yağmurlu gün → bando | şarkı, renkli notalar |
| 1 | **The Color Thief** | Biri dünyanın renklerini çalıyor! | gri dünya → renk patlaması (görsel şok) |
| 2 | **The Tiny Glowing Door** | Duvarda minik parlayan kapı belirir | dev/mini ölçek, büyülü dünya |
| 3 | **The Last Firefly** | Bahçenin ateşböcekleri kayboluyor | gece, parlayan sürü, kurtarma |
| 4 | **Upside-Down Day** | Yerçekimi tersine döndü, herkes uçuyor! | havada süzülen aile, kaos-komik |
| 5 | **Lost in the Toy Box** | Aile küçülüp dev oyuncak kutusunda kayboldu | devasa ölçek, macera |
| 6 | **The Rainbow Bridge** | Gökkuşağı katılaşır, bulut şatosuna tırmanış | renkli, yükseklik, keşif |
| 7 | **The Midnight Circus** | Gece bahçede büyülü sirk belirir | ışık gösterisi, gizem |
| 8 | **The Runaway Balloon** | Mira'nın balonu oyuncağıyla uçtu — kovalamaca | şehir üstü uçuş, gerilim |
| 9 | **The Glowing Egg** | Gizemli parlayan yumurta çatlıyor... | merak boşluğu, dönüşüm |
| 10 | **The Snow That Sings** | Şarkı söyleyen sihirli kar yağıyor | kar+ışık, şarkı, huzur |
| 11 | **The Wish Well** | Dilek kuyusu — ama dilekler komik ters gider | sürpriz, kahkaha, tekrar |
| 12 | **The Shrinking Puddle** | Yağmur birikintisi başka dünyaya kapı | yansıma/su efekti, keşif |

Her bölüm çıkışında bu bankadan biri seçilir, bu belgedeki standartlarla
senaryolaştırılır. Banka tükendikçe yenileri eklenir.

---

## 4b. NURSERY MÜZİK HATTI (3 günde bir — Osman direktifi 2026-07-07)

Sinematik filmlerin ARASINA, **her 3 günde bir** nursery rhyme / çocuk şarkısı
videosu. Evergreen, sonsuz tekrar izlenir, algoritma sever (Cocomelon modeli).

### Yöntem bölüşümü (maliyet sürdürülebilirliği için)
- **Sinematik film → Seedance** (~$28, yürüme/aksiyon/sinematik gerek).
- **Nursery → KOD-KUKLA (Remotion), BEDAVA.** Şarkı+dans tek ortamda geçer,
  karakter yürümesine gerek yok → kod-kuklanın zaafı burada önemsiz, üstelik
  %100 tutarlı + sıfır maliyet. 3 günde bir sıklık ancak böyle sürdürülür.

### Şarkı sesi (KRİTİK — TTS şarkı söyleyemez)
- **Suno / Udio** gibi AI müzik aracıyla söylenmiş vokal üretilir:
  ya klasik (Twinkle Twinkle, Wheels on the Bus, Old MacDonald, ABC, Baby
  Shark tarzı) ya da "Pen Family" özgün şarkıları.
- Vokal + enstrüman track → Remotion'da karakterler ağız/dans senkronu +
  ekranda zıplayan karaoke şarkı sözleri.
- ⚠️ Osman'dan gereken: Suno hesabı/anahtarı (ya da onaylı vokal kaynağı).

### Nursery yapısı
- 1.5–3 dk şarkı. Dikey (9:16) doğrudan üretilir (kırpma yok).
- Nakarat tekrarlı, sözler ekranda (öğretici + tekrar izleme).
- Kısa 20-30s "en cıvıl" bölümü short olarak da kesilir (FB/YT/IG).
- İmza karakterler şarkı söyler → tanınırlık artar.

### Nursery şarkı bankası (başlangıç)
Twinkle Twinkle (Twinkle karakteriyle birebir!), Wheels on the Bus (aile
gezisi), Old MacDonald (Biscuit + hayvanlar), ABC Song (Saf okulda), Rain
Rain Go Away (yağmurlu gün), Clean Up Song, Bath Song, Colors Song, Numbers
Song, If You're Happy (aile).

---

## 5. ÖZET — DEĞİŞMEZ KURALLAR
1. 5 günde bir 4:30-5 dk sinematik film (4-5 × 65s chapter).
2. TikTok: günde 1, sabah 06:00, 65s chapter (konu bütünlüğü).
3. FB/YT Shorts/IG: günde 2 (06:00 + 18:00), 20-25s sinematik highlight.
4. Uzun film YouTube'a (Osman onayıyla).
5. Konu bankasından yaratıcı+görsel güçlü tema. Jenerik yok.
6. Her chapter ≥1 hero shot, kamera dili, atmosfer ışık, sıfır boş kare.
7. Karakterler tutarlı (sert prompt+seed), imza replikler, insan asla.
8. Para: önden yükle, dry-run → tek test → tam üretim → QC → redo.
