# Long-Form Video Architecture — The Pen Family

## Goal
8-10 minute YouTube episodes, structured as 8-10 mini scenes.  
Each scene = one complete short (45-75 seconds), with its own script/voice/render.  
Final video = FFmpeg concat of all scenes.

## Episode Structure (10 Acts)

| Act | Name | Duration | Background | Who Talks |
|-----|------|----------|-----------|-----------|
| 1 | **Hook** | 45s | varies | Sem or Saf (chaos starts immediately) |
| 2 | **Family Intro** | 50s | home | Oz + Mas (explain situation) |
| 3 | **Funny Problem** | 55s | home/kitchen | Full family reaction cascade |
| 4 | **First Failed Attempt** | 60s | varies | Sem's plan fails spectacularly |
| 5 | **New Clue** | 50s | varies | Saf asks the right question |
| 6 | **Adventure Moment** | 65s | park/street | Outdoor action scene |
| 7 | **Bigger Challenge** | 70s | varies | Things get worse |
| 8 | **Solution** | 60s | varies | Family works together |
| 9 | **Lesson Learned** | 45s | home | Mas delivers the truth |
| 10 | **Funny Ending** | 50s | home | Mira ruins/saves it; subscribe prompt |

**Total:** ~550 seconds = ~9.2 minutes

## File Layout Per Episode

```
outputs/long_episodes/YYYY-MM-DD-{slug}/
  scene_01_hook/
    script.json
    audio_full.wav
    manifest.json
    video.mp4
  scene_02_family_intro/
    ...
  ...
  scene_10_funny_ending/
    ...
  episode_full.mp4          ← FFmpeg concat of all scenes
  episode_thumbnail.png     ← Generated separately
  episode_metadata.json     ← Title, description, hashtags
```

## How `pipeline/long_episode.py` Works

```
1. Generate episode plan (1 LLM call → 10 scene topics + backgrounds)
2. For each scene (1-10):
   a. generate_script(topic=scene_topic, scene_number=N, episode_context=...)
   b. synthesize_voice(out_dir=scene_dir)
   c. lipsync(out_dir=scene_dir)
   d. build_manifest(out_dir=scene_dir)
   e. remotion_render(out_dir=scene_dir)
3. FFmpeg concat all 10 video.mp4 files → episode_full.mp4
4. Upload to YouTube (only — not TikTok/Instagram)
```

## Episode Prompt Template (for LLM)

The long_episode.py passes this context to generate_script for each scene:
```
Episode title: {title}
Scene {N} of 10: {act_name}
Episode context: {what_happened_so_far}
Scene goal: {what_must_happen_in_this_scene}
Carry forward: {character_states_from_previous_scene}
```

This ensures continuity: a character who dropped something in scene 3 still references it in scene 6.

## Concat Command (FFmpeg)

```bash
# Build file list
for i in 01 02 03 04 05 06 07 08 09 10; do
  echo "file scene_${i}_*/video.mp4" >> concat_list.txt
done

# Concat (lossless stream copy)
ffmpeg -f concat -safe 0 -i concat_list.txt -c copy episode_full.mp4
```

## Differences vs Short Videos

| | Short (daily) | Long (episode) |
|--|---------------|----------------|
| Duration | 60-75s | 8-10 min |
| Scenes | 1 | 8-10 |
| Script beats | 17-20 | 17-20 per scene |
| Upload platform | TikTok + YT + IG + FB | YouTube only |
| Generate time | ~8 min | ~80 min |
| Run frequency | Daily | Every 3 days |
| Entry point | `pipeline/run.py` | `pipeline/long_episode.py` |

## ECS Considerations
Long episodes need more time — the ECS task timeout must be increased to 120 minutes.  
Use Fargate with 2 vCPU / 4GB RAM for long episode runs.
