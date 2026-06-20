# Long Video Agent

## Purpose
Create one complete 8-10 minute episode every 3 days for YouTube.

## Episode Structure
10 acts × ~55 seconds each = ~9 minutes total

| Act | Name | Goal |
|-----|------|------|
| 1 | Hook | Open mid-chaos, grab attention in 3 seconds |
| 2 | Family Intro | Establish who's where and what's happening |
| 3 | Funny Problem | The real problem is revealed (Sem caused it) |
| 4 | First Attempt | Oz tries to fix it; fails hilariously |
| 5 | New Clue | Saf asks the question that changes everything |
| 6 | Adventure | Family goes somewhere (park, shop, school) |
| 7 | Bigger Challenge | A second problem makes things worse |
| 8 | Solution | Family works together (Mira accidentally helps) |
| 9 | Lesson | Mas shows what they learned (no lecturing) |
| 10 | Funny Ending | Subscribe prompt wrapped in a joke |

## Full Command
```bash
cd /Users/osmansakli/video-pencils-projects/pencil-shorts
python3 pipeline/long_episode.py --auto --no-publish
```

Review the video first, then upload:
```bash
python3 publish/upload.py --platforms youtube --video outputs/long_episodes/latest/episode_full.mp4
```

## Episode Plan Generation

The agent generates this JSON before rendering:
```json
{
  "episode_title": "...",
  "episode_premise": "...",
  "scenes": [
    {
      "act": 1,
      "act_name": "Hook",
      "topic": "description of what happens in this scene",
      "background": "home",
      "target_seconds": 45,
      "carry_forward": "what characters remember from previous scene"
    },
    ...
  ]
}
```

## Continuity Rules
- Objects mentioned in scene 3 must exist in scene 6
- Character emotions carry over (if Oz is angry in act 4, he's still a little grumpy in act 5)
- The main lesson is set up in act 5, reinforced in act 9 — never stated as a lesson
- Guest characters (Eli, Kit, Rex, Nib) can appear in act 6 (adventure) or act 7 (bigger challenge)

## Output Location
```
outputs/long_episodes/YYYY-MM-DD-{slug}/
  scene_01/ ... scene_10/
  episode_full.mp4
  episode_metadata.json
```

## YouTube Upload Specs
- Title: Max 100 characters, include "The Pen Family" + keyword
- Description: 3-4 sentences + timestamps + hashtags
- Tags: ThePenFamily, KidsCartoon, FamilyFun, AnimatedSeries, KidsYouTube
- Thumbnail: Sem doing something chaotic, bright colors, shocked expression
- Category: 20 (Gaming — actually use 1 for Film/Animation)
- Made for kids: Yes

## ECS Task Requirements
- Memory: 4GB
- vCPU: 2
- Timeout: 120 minutes
- Spot capacity: acceptable (checkpoint system handles interruption)
