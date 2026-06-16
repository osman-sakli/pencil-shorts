# PRODUCTION.md — Otomatik Kawaii Çizgi Film Shorts Sistemi (Claude Code Runbook)

> Bu dosya bir **Claude Code görev tarifidir**. Claude Code bunu okuyup adım adım uygular.
> Görevler 🤖 (Claude Code yapar) / 🧑 (Osman yapar) diye işaretli. İnsan adımları
> otomatikleştirilemez: hesap açma, OAuth onayı, banka/monetizasyon.
>
> **Üretim motoru:** bu depodaki **kodla-çizilen kawaii Remotion pipeline'ı.**
> Resim/sprite/Pexels/AI-image YOK. Karakterler `renderer/src/cast.tsx` içinde koddur.
> Videolar **60-90 sn** üretilir (TikTok Creator Rewards uygunluğu için).

---

## 0. Senin (Osman) elle yapacakların — Türkçe özet
1. **Bir kez** CLI auth: `gh auth login`, `aws configure` (veya SSO).
2. **API anahtarları:** LLM (Anthropic) + upload-post.com. (Pexels/görsel API GEREKMEZ.)
3. Marka adıyla TikTok + YouTube kanalı + Instagram (Business) aç.
4. upload-post panelinde bu 3 hesabı OAuth ile bağla (tarayıcıda, tek sefer).
5. Monetizasyon: eşikler dolunca başvuru + AdSense/banka.
Gerisi (kod, altyapı, üretim, yükleme, zamanlama) = Claude Code.

---

## 1. Kapsam (dürüst)
**🤖 Tam otomatik:** GitHub repo + push · senaryo→ses→lip-sync→render→mp4 · upload-post
ile 3 platforma yükleme · AWS altyapısı (Terraform) · GitHub Actions CI · günlük cron.
**🧑 Otomatikleştirilemez:** sosyal hesap açma + kimlik doğrulama · OAuth onayları ·
monetizasyon eşikleri/başvuru · AdSense+banka+vergi · içeriğin tutması (algoritma).

**Para gerçeği & strateji:** Videolar **60-90 sn** üretilir (pipeline buna ayarlı) —
çünkü TikTok Creator Rewards yalnızca 60 sn+ videolara ödeme yapar. Yine de reklam
geliri düşüktür ($0.40-1.00 RPM); asıl gelir **affiliate + TikTok Shop + sponsor**.
Video açıklamasına affiliate linki otomatik eklenir (`AFFILIATE_LINK`).

---

## 2. Önkoşullar (🧑 bir kez, sonra Claude Code devralır)
Geliştirme: EC2 (Ubuntu 24.04, t3.medium). Prod: Fargate.
```bash
for t in git gh aws docker terraform node python3 jq; do
  printf "%-10s " "$t"; command -v "$t" >/dev/null && "$t" --version 2>&1 | head -1 || echo "YOK"
done
```
- Eksikleri Claude Code kurar. **🧑 auth insana ait:** `gh auth login`, `aws configure`,
  doğrula: `aws sts get-caller-identity`.
- Guardrail: Claude Code kimlik bilgisi girmez, sır commit etmez.

---

## 3. Depo yapısı (zaten bu depo)
```
pencil-shorts/                 # GitHub: osmsakli/pencil-shorts (private)
├── PRODUCTION.md
├── characters.yaml            # kadro metadata (kod karakterler)
├── pipeline/                  # python: script, voice, lipsync, manifest, run
├── renderer/                  # Remotion: cast.tsx (kawaii), mouths.tsx, PencilShort.tsx
├── publish/upload.py          # upload-post istemcisi
├── Dockerfile                 # python+node+ffmpeg+rhubarb+remotion tek imaj
├── docker-compose.yml         # lokal test
└── infra/                     # Terraform (Claude Code oluşturacak)
    └── .github/workflows/     # CI (Claude Code oluşturacak)
```

---

## 4. Faz A — Repo + push  🤖
1. `gh repo create osmsakli/pencil-shorts --private --source=. --remote=origin`
2. `.gitignore` doğrula: `.env`, `out/*`, `node_modules/`, `.terraform/`, `__pycache__/`.
3. Commit + push.
**Kabul:** `gh repo view osmsakli/pencil-shorts` çalışır; sır yok.

---

## 5. Faz B — İlk videoyu lokalde üret  🤖
1. `cp .env.example .env`; 🧑 `ANTHROPIC_API_KEY` gir.
2. `ffmpeg` + `rhubarb` kur (yoksa). Ya da Docker kullan (imaj ikisini içerir).
3. `cd pipeline && pip install -r requirements.txt`; `cd ../renderer && npm install`.
4. Üret:
   ```bash
   python pipeline/run.py --topic "Kurşun kalem silgiyi kıskanıyor"
   ```
5. `out/video.mp4`'ü incele. Kawaii karakterler konuşuyor, altyazı senkron mu bak.
   - Lip-sync zayıfsa: `.env` `RHUBARB_RECOGNIZER=phonetic` (TR için).
   - Yeni karakter gerekiyorsa: `characters.yaml` + `renderer/src/cast.tsx`.
**Kabul:** elde oynayan bir `out/video.mp4` var (henüz yükleme yok).

---

## 6. Faz C — Yayınlama: upload-post  🤖 + 🧑
**🧑 tek sefer:** upload-post.com hesabı + API key; panelde TikTok+YouTube+Instagram
(Business) OAuth ile bağla.
**🤖:** `publish/upload.py` zaten `POST https://api.upload-post.com/api/upload`
(`Authorization: Apikey ...`, `platform[]`, `video`). `orchestrator` akışına bağla:
`run.py` üret → `upload.py` yükle (ilk seferinde **private/test**), yanıtı logla, retry.
**Kabul:** üretilen video 3 platforma test modda yüklenir.

---

## 7. Faz D — AWS altyapısı  🤖
> **Hazır komutlar:** `AWS_SETUP.md` tüm `aws cli` komutlarını sırayla içerir.
> Claude Code onu çalıştırır (Terraform yerine doğrudan CLI). 🧑 sadece auth + sır değerleri.

**En ucuz, serverless:** EventBridge Scheduler → **ECS Fargate (Spot) tek-shot görev**
(günde ~3-6 dk, boşta $0). Lambda değil (ffmpeg/remotion ağır + 15dk sınırı).
**Tek container:** bu depo imajı (python+node+ffmpeg+rhubarb+remotion). MoneyPrinterTurbo
gibi ikinci servis YOK.
`infra/` modülleri (oluştur):
- `ecr.tf` — uygulama imajı için repo.
- `s3.tf` — videolar + `state.json` (konu tekrarını önler); public kapalı, versiyonlu.
- `ssm.tf` — `/pencil-shorts/anthropic_api_key`, `/upload_post_api_key` (SecureString;
  değerleri 🧑 `aws ssm put-parameter` ile girer; Terraform değeri commit etmez).
- `iam.tf` — task role: ECR pull, SSM read, S3 RW, CloudWatch logs.
- `ecs.tf` — cluster + task def (2 vCPU / 4GB, Fargate Spot). Remotion için container'da
  headless chromium gerekir: imajda `npx remotion browser ensure` çalıştır (build adımı).
- `schedule.tf` — EventBridge Scheduler, `cron(0 14 * * ? *)` UTC günlük → ECS RunTask.
- `budget.tf` — aylık $20 alarm (osmsakli@gmail.com).
**🧑 onay:** Claude Code `terraform plan`'i gösterir, **apply öncesi onay ister.**
**Kabul:** `aws ecs run-task ...` → S3'e mp4 + platformlara yükleme.

---

## 8. Faz E — CI/CD (GitHub Actions)  🤖
- `deploy.yml`: main'e push → imaj build → ECR push (GitHub OIDC, uzun ömürlü anahtar yok)
  → `terraform plan` (PR) / `apply` (main, environment approval).
- `trigger.yml`: `workflow_dispatch` → seçili konu ile anında bir video (`aws ecs run-task`).
**🧑:** repo Settings → environment "production" + required reviewer (kendisi).
**Kabul:** push → imaj ECR'da; tek tıkla video üretimi.

---

## 9. Faz F — Kanallar + Monetizasyon  🧑 (+ zaman)
- 🧑 Marka adı, 3 hesap (TikTok, YouTube, Instagram Business), profiller, upload-post bağlama.
- 🧑 `AFFILIATE_LINK`'i SSM'e gir (örn. TikTok Shop ürün linki / Amazon Associates / kendi
  ürünün). Her videonun açıklamasına otomatik eklenir.

**Gelir önceliği (en hızlıdan en yavaşa):**
1. **Affiliate** — takipçi şartı yok, ilk günden başlar. Açıklamadaki linkten satış komisyonu.
2. **TikTok Shop** — ~5.000 takipçi; en çok gerçek paranın aktığı yer.
3. **LIVE hediyeleri** — 1.000 takipçi.
4. **Brand/sponsor** — ~10.000 takipçi; niş kitleyle daha değerli.
5. **Reklam payı (en zayıf):** TikTok Creator Rewards = 10.000 takipçi + son 30 günde
   100.000 izlenme + **video 60 sn+** (pipeline buna ayarlı), RPM $0.40-1.00. YouTube
   Shorts ve Instagram CMP düşük/değişken. (Güncel eşikleri başvuru anında doğrula.)

**Strateji:** günde 1-2 video, tek nişte; 100+ videoda patlayan(lar)ı affiliate/Shop ile
paraya çevir. Reklam gelirini bonus say, ana motor affiliate/sponsor olsun.

---

## 10. Operasyon
- Loglar: CloudWatch `/ecs/pencil-shorts` (konu, süre, yükleme yanıtı).
- Manuel tetik: Actions `trigger.yml` veya `aws ecs run-task`.
- Kill switch: `aws scheduler update-schedule --name pencil-daily --state DISABLED`.
- Opsiyonel gözlem: OTel exporter → Honeycomb (başarı oranı, render süresi, hata).

---

## 11. Maliyet (aylık kaba)
Fargate Spot (günde ~5dk) birkaç sent–$1 · S3+SSM+CloudWatch <$1 · LLM (Haiku) sent ·
EdgeTTS/Rhubarb/render $0 · upload-post 🧑 abonelik · **AWS toplam ~$2-5/ay.**

---

## 12. Claude Code guardrail'leri
1. Sır yazma — sadece SSM; kod/log/repoya asla.
2. Maliyet kapısı — `terraform apply`, `run-task`, ilk gerçek yükleme öncesi onay iste; bütçe alarmını ilk kur.
3. İdempotent Terraform; isimler `pencil-shorts-` ön ekli, izole.
4. İnsan kapıları (OAuth, hesap, monetizasyon, CLI auth) insana bırak, açıkça iste.
5. İlk yüklemeyi private/test yap, doğrulat, sonra public.
6. Küçük adım → kabul kriteri → insana özet → devam onayı.
7. Mevcut AWS kaynaklarına dokunma.

### Başlangıç komutu (Claude Code'a ver)
> "PRODUCTION.md'yi oku. Faz A'dan başla. Önkoşulları kontrol et, eksik auth'ları benden
> iste, her fazı kabul kriteriyle bitir, her fazdan sonra dur, özetle ve devam onayı al.
> Sır yazma, apply öncesi onay al."
