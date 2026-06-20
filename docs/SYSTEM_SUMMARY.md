# System Summary — The Pen Family Production Stack

## Files Created (This Upgrade)

### Documentation
| File | Purpose |
|------|---------|
| `docs/CURRENT_PIPELINE_REVIEW.md` | How the existing short pipeline works end-to-end |
| `docs/OPENMONTAGE_INTEGRATION_PLAN.md` | How to add OpenMontage as a long-video editor layer |
| `docs/LONG_FORM_VIDEO_ARCHITECTURE.md` | 10-act structure for 8-10 minute episodes |
| `docs/CHARACTER_MEMORY_SYSTEM.md` | Character bible: appearance, voice, personality, catchphrases |
| `docs/DAILY_AUTOMATION_PLAN.md` | Daily + every-3-days schedule, commands, retry strategy |
| `docs/SYSTEM_SUMMARY.md` | This file |

### Agents
| File | Purpose |
|------|---------|
| `agents/story_generator_agent.md` | Auto-generates short + long episode ideas with full prompts |
| `agents/trend_agent.md` | Seasonal topic bank + trending kids content strategy |
| `agents/short_video_agent.md` | Daily short workflow: commands, checklist, error handling |
| `agents/long_video_agent.md` | Long episode workflow: 10 acts, continuity rules, YouTube specs |
| `agents/asset_agent.md` | Image generation prompts for sprites, backgrounds, thumbnails |
| `agents/voice_agent.md` | Voice direction for every character + EdgeTTS config reference |
| `agents/openmontage_editor_agent.md` | How to use OM for transitions, pacing, scene planning |
| `agents/qa_agent.md` | Safety + quality checklist + LLM review prompt |
| `agents/youtube_package_agent.md` | Title formulas, description templates, metadata for all platforms |

### Code
| File | Purpose |
|------|---------|
| `pipeline/long_episode.py` | **NEW: Long episode runner** — generates 10 scenes + FFmpeg concat |

### Example Scripts
| File | Purpose |
|------|---------|
| `examples/shorts/sem_loses_purple_color.json` | Sample short: Sem washes off Saf's color |
| `examples/shorts/ulku_giant_eraser_problem.json` | Sample short: Eli erases Saf's school project |
| `examples/shorts/dad_pencil_funny_farm_lesson.json` | Sample short: Oz's farm patience lesson |
| `examples/long_episodes/sem_goes_to_the_farm.json` | Full long episode: 10 acts, farm adventure |
| `examples/long_episodes/giant_crayon_castle.json` | Full long episode: 10 acts, Nib's castle |

---

## How OpenMontage Will Be Used

**Phase 1 (now):** `pipeline/long_episode.py` handles concat via plain FFmpeg stream copy.  
**Phase 2 (later):** OpenMontage agent takes over scene ordering, transition selection, and audio leveling.  
The existing short pipeline is completely untouched.

---

## How to Run Daily Shorts

```bash
cd /Users/osmansakli/video-pencils-projects/pencil-shorts

# Auto-pick topic, render, upload all 4 platforms:
python3 pipeline/run.py --auto

# Manual topic:
python3 pipeline/run.py --topic "Sem floods the bathroom again"

# Skip upload (review first):
python3 pipeline/run.py --auto --no-publish
```

---

## How to Run 8-10 Minute Long Episodes

```bash
cd /Users/osmansakli/video-pencils-projects/pencil-shorts

# Step 1: Generate plan only (review before committing ~80 min render time)
python3 pipeline/long_episode.py --auto --plan-only

# Step 2: Render (no upload)
python3 pipeline/long_episode.py --plan-file outputs/long_episodes/YYYY-MM-DD-slug/episode_plan.json

# Step 3: Review video at outputs/long_episodes/YYYY-MM-DD-slug/episode_full.mp4

# Step 4: Upload to YouTube
python3 publish/upload.py --platforms youtube

# OR: Do all steps including upload in one command:
python3 pipeline/long_episode.py --auto --upload

# Resume if it crashed at scene 6:
python3 pipeline/long_episode.py --plan-file outputs/long_episodes/.../episode_plan.json --resume --from-scene 6
```

---

## What Still Needs API Keys or Manual Setup

| Item | Status | Action Needed |
|------|--------|---------------|
| `ANTHROPIC_API_KEY` | ✅ In SSM | None |
| `UPLOAD_POST_API_KEY` | ✅ In SSM | None |
| `UPLOAD_POST_USER` | ✅ In SSM | None |
| OpenMontage (Phase 2) | ⏳ Not installed | `git clone` + install alongside project |
| Better character sprites | ⏳ PIL placeholders exist | Use asset_agent.md prompts with DALL-E 3 |
| Thumbnail generation | ⏳ Manual | Use youtube_package_agent.md thumbnail prompts |
| ECS long episode task | ⏳ Not configured | Increase timeout to 120min, memory to 4GB |

---

## Next Best Improvement (Priority Order)

1. **Better sprites** — Run the prompts in `agents/asset_agent.md` through DALL-E 3 to get Pixar-quality sprites for all 10 characters. This is the biggest visual upgrade.

2. **Thumbnail automation** — Add `pipeline/generate_package.py` to auto-create YouTube title + thumbnail prompt from each script.json.

3. **Test long_episode.py** — Run `python3 pipeline/long_episode.py --auto --plan-only` first to verify the plan generation works, then do a single scene test before a full 10-scene render.

4. **ECS task for long episodes** — Add a second ECS task definition with 2vCPU/4GB/120min for the every-3-days episode run.

5. **OpenMontage Phase 2** — Install and wrap as described in `docs/OPENMONTAGE_INTEGRATION_PLAN.md`.
