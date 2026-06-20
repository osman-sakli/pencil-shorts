# Short Video Agent

## Purpose
Create one complete daily short video (60-75 seconds) for The Pen Family.

## Daily Workflow

```
1. Pick topic (auto from topic bank or trending)
2. generate_script.py → out/script.json
3. synthesize_voice.py → out/beat_N.mp3 + beat_N.wav
4. lipsync.py → out/beat_N.cues.json
5. build_manifest.py → out/manifest.json + audio_full.wav
6. remotion render → out/video.mp4
7. upload.py → TikTok + YouTube + Instagram + Facebook
```

## Full Command (One Shot)
```bash
cd /Users/osmansakli/video-pencils-projects/pencil-shorts
python3 pipeline/run.py --auto
```

## Manual Topic Command
```bash
python3 pipeline/run.py --topic "Sem floods the bathroom trying to wash his crayons"
```

## Quality Checklist Before Publishing
- [ ] Video is 60-75 seconds (not shorter, not longer)
- [ ] Sem mispronounces at least one word
- [ ] Saf asks at least one question
- [ ] Mira does something unexpected
- [ ] Mas has the best last line
- [ ] No bad words / adult content (filter handles this automatically)
- [ ] Background matches the scene (kitchen for breakfast, bedroom for night, etc.)

## Script Validation Rules
- 17-20 beats minimum
- 140-180 words total
- Max 8 words per line
- Every beat has a background label
- All character IDs valid (oz, mas, bas, saf, sem, mira, eli, kit, rex, nib)

## Output Files
```
out/
  script.json        ← LLM output
  beat_0.mp3         ← voice per line
  beat_0.wav         ← 16kHz for lip sync
  beat_0.words.json  ← word timing
  beat_0.cues.json   ← mouth shapes
  manifest.json      ← full video plan
  audio_full.wav     ← concatenated audio
  video.mp4          ← final rendered video
```

## Upload Targets
| Platform | Account | Notes |
|----------|---------|-------|
| TikTok | @familypencils | 90-min retry if rate limited |
| YouTube | familypencils | Auto-published as Short |
| Instagram | familypencils | Reels format |
| Facebook | familypencils | Reels format |

## Error Handling
- TikTok rate limit → auto retry 4× every 90 min
- Script validation fail → LLM retried automatically
- Render fail → check `out/render.log` for Remotion errors
- Upload fail → re-run `python3 publish/upload.py --platforms youtube instagram facebook`
