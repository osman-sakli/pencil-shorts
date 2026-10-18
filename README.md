# pencil-shorts

Automated pipeline that makes short kids cartoons (60–90 s, vertical 1080x1920) about **The Pencil Family**, a family of kawaii pencil characters. It writes the script, voices it, lip-syncs the mouths, renders the video and publishes it to TikTok / YouTube Shorts / Instagram Reels — every day, unattended, for about $0 per video.

Characters are drawn 100% in code (React/SVG in Remotion), so they stay perfectly consistent across episodes and need no image generation.

Türkçe README: [README.tr.md](README.tr.md)

## Who it's for

My own YouTube/TikTok channel. The repo is also a working reference for anyone who wants a cheap, fully code-driven short-video factory.

## Stack

| Part | Tech |
|---|---|
| Script | LLM (Anthropic API by default) → `out/script.json` |
| Voice | EdgeTTS (free) or ElevenLabs |
| Lip-sync | Rhubarb → mouth shapes A–H, X |
| Render | Remotion (React + TypeScript), `renderer/` |
| Orchestration | Python 3.11+, `pipeline/` |
| Cast config | `characters.yaml` + `renderer/src/cast.tsx` |
| Publish | upload-post.com API, `publish/` |
| Prod | Docker, AWS ECS Fargate scheduled task, ECR, EventBridge Scheduler |
| IaC | Terraform, `infra/` |
| CI/CD | GitHub Actions with AWS OIDC (no stored AWS keys) |

## Flow

```
generate_script.py   LLM      -> out/script.json
synthesize_voice.py  EdgeTTS  -> out/beat_N.mp3 (+ word timings) -> wav
lipsync.py           Rhubarb  -> out/beat_N.cues.json
build_manifest.py             -> out/manifest.json + out/audio_full.wav
renderer (Remotion)           -> out/video.mp4
publish/upload.py             -> TikTok / Reels / Shorts (optional)
```

`pipeline/run.py` runs all steps in order. `pipeline/long_episode.py` is the long-form episode runner.

## Setup

Needs Python 3.11+, Node 20+, `ffmpeg`, `rhubarb` on PATH.

```bash
cp .env.example .env          # put your ANTHROPIC_API_KEY
cd pipeline && pip install -r requirements.txt && cd ..
cd renderer && npm install && cd ..
```

## Run

```bash
python pipeline/run.py --topic "Pencil is jealous of the eraser"
python pipeline/run.py --auto            # random topic
# render only:
cd renderer && npx remotion render PencilShort ../out/video.mp4 --props=../out/manifest.json --public-dir=../
```

Output: `out/video.mp4` (1080x1920, 30 fps).

## Cost per video

LLM (Haiku) ~$0.001 · EdgeTTS $0 · Rhubarb + render $0 → **~$0**. ElevenLabs voice adds ~$0.10–0.30.

## Production

Daily run on AWS Fargate, deployed by GitHub Actions. See [PRODUCTION.md](PRODUCTION.md) and [AWS_SETUP.md](AWS_SETUP.md). Architecture notes in [docs/](docs/).

## Secrets

No keys in the repo. Use `.env` locally (git-ignored, template in `.env.example`) and AWS SSM Parameter Store in prod.

## Assets

Background music: tracks in `assets/music/` (from Pixabay) are used by the cartoon overlay step; shorts can also fetch music at runtime via `pipeline/fetch_music.py`.

## Roadmap

See [ROADMAP.md](ROADMAP.md).

## License

Code: [MIT](LICENSE). Remotion is used under its own license, see https://remotion.dev/license.
