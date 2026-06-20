# OpenMontage Editor Agent

## Purpose
Use OpenMontage for scene planning, editing decisions, transitions, pacing, and final long-form video assembly.

## What OpenMontage Does
- Orchestrates multi-step video production via AI agent
- 52 tool skills: trim, concat, fade, overlay, title cards, color grade
- Checkpoint system: saves progress so crashes don't restart from zero
- Driven by Claude AI making editing decisions automatically

## When to Use OpenMontage
| Task | Use OpenMontage? |
|------|-----------------|
| Daily short (1 scene, 60-75s) | ❌ Use `pipeline/run.py` directly |
| Long episode (8-10 scenes) | ✅ OM handles concat + transitions |
| Custom transitions between scenes | ✅ |
| Title card overlays | ✅ |
| Color grading / look | ✅ (optional future phase) |
| Script generation | ❌ Use our `generate_script.py` |
| Voice synthesis | ❌ Use our EdgeTTS pipeline |

## Scene Planning (Long Episodes)

Before rendering, OM agent decides:
```json
{
  "editing_plan": [
    {
      "scene": 1,
      "duration_target": 45,
      "transition_to_next": "quick_cut",
      "energy_level": "high",
      "music_moment": "hook_beat"
    },
    {
      "scene": 2, 
      "transition_to_next": "soft_fade",
      "energy_level": "medium"
    }
  ],
  "overall_pacing": "fast_start_slow_middle_fast_end",
  "subscribe_cue_at_seconds": 480
}
```

## Transition Types Available
| Transition | When to Use |
|-----------|-------------|
| `quick_cut` | High energy scenes, jokes landing |
| `soft_fade` | Emotional moments, scene changes |
| `wipe_right` | Adventure/movement scenes |
| `zoom_in_cut` | Surprise reveals |
| `dissolve` | Time passing, location changes |

## FFmpeg Concat Command (Phase 1 — no OM)
```bash
# Create scene list
find outputs/long_episodes/latest/ -name "video.mp4" | sort > /tmp/concat_list.txt
sed -i 's/^/file /' /tmp/concat_list.txt

# Concat without re-encoding (fast)
ffmpeg -f concat -safe 0 -i /tmp/concat_list.txt -c copy episode_full.mp4
```

## OM Integration Command (Phase 2)
```bash
# After OpenMontage is installed at ../openmontage/
cd ../openmontage
python3 agent.py \
  --task "concat_with_transitions" \
  --input-dir ../pencil-shorts/outputs/long_episodes/latest/ \
  --output ../pencil-shorts/outputs/long_episodes/latest/episode_full.mp4 \
  --transitions-plan ../pencil-shorts/outputs/long_episodes/latest/edit_plan.json
```

## Subscribe Prompt (Act 10 Standard)
Every long episode ends with a subscribe moment embedded in the story:
- Sem looks at camera and says something cute/chaotic
- Lower third appears: "Subscribe for more Pen Family chaos!"
- Duration: last 5 seconds of episode
- This is rendered as part of scene 10 script (not overlaid by OM)

## Pacing Rules for Editor Agent
- Acts 1-3: Fast pacing (keep kids hooked)
- Acts 4-6: Medium pacing (let the story breathe)
- Acts 7-8: Build tension (slightly faster cuts)
- Acts 9-10: Slow down to land the lesson + funny ending

## Quality Checks (OM Validates)
- [ ] All 10 scenes rendered (no missing files)
- [ ] Total duration 8:00-10:30 minutes
- [ ] Audio levels consistent across scenes
- [ ] No black frames between scene cuts
- [ ] Final frame is the subscribe prompt
