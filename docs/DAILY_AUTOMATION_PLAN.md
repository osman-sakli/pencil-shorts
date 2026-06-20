# Daily Automation Plan — The Pen Family

## Folder Structure
```
pencil-shorts/
  pipeline/           ← Python scripts (generate, voice, lipsync, build, run)
  pipeline/long_episode.py  ← NEW: long-form episode runner
  renderer/           ← Remotion TypeScript renderer
  publish/            ← Upload scripts
  characters/         ← sprites + yaml config
  agents/             ← Agent documentation
  docs/               ← Architecture docs
  examples/           ← Sample scripts and episodes
  outputs/
    shorts/           ← Rendered short videos by date
    long_episodes/    ← Rendered long episodes by date
  assets/
    characters/       ← Character image files
    backgrounds/      ← Background image files  
    props/            ← Prop image files
  scripts/
    shorts/           ← Saved short scripts by date
    scripts/long_episodes/  ← Saved long episode scripts
  out/                ← Working directory (cleared each run)
```

## Daily Workflow — Short Video (Every Day)

### Time: 9:00 AM UTC (runs on ECS Fargate)
```bash
cd /Users/osmansakli/video-pencils-projects/pencil-shorts
python3 pipeline/run.py --auto
```

### What happens:
1. `generate_script.py --auto` — picks random topic from AUTO_TOPICS list
2. `synthesize_voice.py` — EdgeTTS generates all beat audio
3. `lipsync.py` — Rhubarb generates mouth cues
4. `build_manifest.py` — assembles manifest + audio_full.wav
5. Remotion renders `out/video.mp4`
6. `publish/upload.py --all` — uploads to TikTok, YouTube, Instagram, Facebook
7. Output saved to `outputs/shorts/YYYY-MM-DD/`

### Duration: ~8 minutes total

---

## Every 3 Days — Long Episode

### Time: 8:00 AM UTC on day 1, 4, 7, 10, ...
```bash
python3 pipeline/long_episode.py --auto --no-publish
```

Then review the video, then:
```bash
python3 publish/upload.py --platforms youtube --video outputs/long_episodes/latest/episode_full.mp4
```

### What happens:
1. Generate 10-scene episode plan (1 LLM call)
2. For each of 10 scenes: run full short pipeline
3. FFmpeg concat all scenes → episode_full.mp4
4. Manual review by human before upload
5. Upload to YouTube only

### Duration: ~80 minutes total

---

## ECS Task Definitions

### Short Video Task
```json
{
  "cpu": "1024",
  "memory": "2048",
  "timeout_minutes": 30,
  "spot": true
}
```

### Long Episode Task
```json
{
  "cpu": "2048", 
  "memory": "4096",
  "timeout_minutes": 120,
  "spot": true
}
```

---

## Error Handling

| Error | Auto Recovery | Manual Action |
|-------|--------------|---------------|
| TikTok rate limit | ✅ 90-min retry × 4 | None needed |
| Script validation fail | ✅ Retry with same topic | If 3 fails: pick new topic |
| Render crash | ❌ | Check `out/render.log`; re-run |
| Upload auth expire | ❌ | Refresh upload-post.com token |
| Long episode scene fail | ❌ | Re-run from `--scene N` |
| ECS Spot interruption | ❌ | Restart task from CloudWatch |

## Retry Strategy
```bash
# Retry a failed short from where it stopped:
python3 pipeline/run.py --skip-script --skip-voice  # if only render failed

# Retry failed upload only:
python3 publish/upload.py --all --video out/video.mp4

# Retry long episode from scene 5:
python3 pipeline/long_episode.py --resume --from-scene 5
```

---

## Quality Checklist (Pre-Publish)

Automated checks (pipeline validates automatically):
- ✅ Beat count ≥15
- ✅ Duration 60-75s (shorts)
- ✅ No bad words
- ✅ All character IDs valid
- ✅ All background labels valid

Human review needed (long episodes only):
- [ ] Story makes sense end-to-end
- [ ] Lesson is appropriate for 3-8 year olds
- [ ] No accidental adult content
- [ ] Subscribe prompt at end
- [ ] Thumbnail ready

---

## Weekly Schedule

| Day | Task |
|-----|------|
| Mon | Short video (auto) |
| Tue | Short video (auto) |
| Wed | Short video (auto) + Long episode render |
| Thu | Short video (auto) |
| Fri | Short video (auto) |
| Sat | Short video (auto) + Long episode upload (after review) |
| Sun | Short video (auto) |

---

## Secrets Management
**Sır değerleri ASLA repoya/log'a yazma — sadece SSM'e**

All secrets live in AWS SSM Parameter Store:
- `/pencil-shorts/ANTHROPIC_API_KEY`
- `/pencil-shorts/UPLOADPOST_API_KEY`

ECS task role has SSM read permissions via IAM.  
Local dev: use `.env` file (not committed to git, listed in `.gitignore`).
