# THE PENCIL FAMILY - OPENMONTAGE LONG VIDEO UPGRADE

You are my senior AI video production engineer.

I already have a working Claude Code pipeline that creates short videos for The Pencil Family.

Now I want you to upgrade my current system by integrating this new GitHub video editor repo:

https://github.com/calesthio/OpenMontage

Main goals:

1. Keep my current short-video pipeline working.
2. Add OpenMontage as a new video editor / producer layer.
3. Add automatic 8-10 minute YouTube episode generation.
4. Create amazing story ideas automatically.
5. Make the system scalable, clean, and easy to run daily.

---

## PROJECT CONTEXT

Project name:
The Pencil Family

Content type:
Animated family-friendly kids videos.

Target audience:
Kids ages 3-8.

Main characters:
- Dad Pencil
- Mom Pencil
- Ayse Pencil
- Ulku Pencil
- Sem Pencil

Important character:
Sem Pencil is the main cute comedy character.

Content formats:
- Daily Shorts: 30-60 seconds
- Long episodes: 8-10 minutes every 3 days

---

## TASK 1: REVIEW CURRENT PIPELINE

First, inspect my existing project.

Find and document:
- How short videos are currently generated
- Where scripts are created
- Where images/assets are stored
- How voices are generated
- How videos are rendered
- How thumbnails are created
- What can be reused for long videos

Create this file:

`docs/CURRENT_PIPELINE_REVIEW.md`

---

## TASK 2: INTEGRATE OPENMONTAGE

Study the OpenMontage repo and decide the best way to use it in this project.

Do not break the current pipeline.

Add OpenMontage as a new optional production path.

Create this file:

`docs/OPENMONTAGE_INTEGRATION_PLAN.md`

Include:
- What OpenMontage does
- How it helps our video workflow
- Which parts should be connected
- Which parts should stay in our current system
- Risks and limitations
- Step-by-step implementation plan

---

## TASK 3: LONG VIDEO SYSTEM

Build a new long-form episode system.

Important:
Do NOT create one single 10-minute scene.

Instead, create long videos as 8-10 mini scenes.

Each scene should be around 45-75 seconds.

Long episode structure:

1. Hook
2. Family intro
3. Funny problem
4. First failed attempt
5. New clue
6. Adventure moment
7. Bigger challenge
8. Solution
9. Lesson learned
10. Funny ending / subscribe moment

Create:

`docs/LONG_FORM_VIDEO_ARCHITECTURE.md`

---

## TASK 4: AUTOMATIC STORY GENERATOR

Create an automatic story idea generator.

It should generate amazing kids episode ideas without me writing every idea manually.

Create:

`agents/story_generator_agent.md`

This agent should generate:

For Shorts:
- 10 daily short ideas
- title
- 60-second script
- scene list
- voice lines
- thumbnail prompt
- hashtags

For long videos:
- 5 long episode ideas
- full 8-10 minute structure
- scene-by-scene script
- dialogue
- image prompts
- voice direction
- thumbnail concept
- SEO title
- description
- hashtags

Story rules:
- Funny
- Cute
- Educational
- Safe for kids
- No violence
- No scary content
- No adult jokes
- No politics
- No religion
- No dangerous challenges
- Clear lesson at the end

---

## TASK 5: CHARACTER MEMORY SYSTEM

Create a character consistency system.

Characters must stay the same across all videos.

Create:

`docs/CHARACTER_MEMORY_SYSTEM.md`

Track:

Dad Pencil:
- appearance
- color
- voice style
- personality
- catchphrases

Mom Pencil:
- appearance
- color
- voice style
- personality
- catchphrases

Ayse Pencil:
- appearance
- age
- color
- personality
- role in family

Ulku Pencil:
- appearance
- age
- color
- personality
- role in family

Sem Pencil:
- appearance
- age
- color
- personality
- role in family
- comedy behavior
- cute phrases

---

## TASK 6: AGENT SYSTEM

Create these agents:

1. `agents/trend_agent.md`
Purpose:
Generate fresh YouTube Kids style ideas.

2. `agents/short_video_agent.md`
Purpose:
Create daily short video scripts.

3. `agents/long_video_agent.md`
Purpose:
Create 8-10 minute episode scripts.

4. `agents/asset_agent.md`
Purpose:
Generate image prompts for characters, backgrounds, props, and thumbnails.

5. `agents/voice_agent.md`
Purpose:
Create voice direction for each character.

6. `agents/openmontage_editor_agent.md`
Purpose:
Use OpenMontage for scene planning, editing, transitions, pacing, and final video assembly.

7. `agents/qa_agent.md`
Purpose:
Check child safety, character consistency, story quality, and video readiness.

8. `agents/youtube_package_agent.md`
Purpose:
Create YouTube title, description, hashtags, thumbnail prompt, and upload metadata.

---

## TASK 7: DAILY AUTOMATION DESIGN

Design a schedule:

Every day:
- Generate 1 short video

Every 3 days:
- Generate 1 long 8-10 minute episode

Create:

`docs/DAILY_AUTOMATION_PLAN.md`

Include:
- folder structure
- commands
- daily workflow
- 3-day long video workflow
- error handling
- retry strategy
- quality checklist

---

## TASK 8: CREATE SAMPLE EPISODES

Create 3 sample Shorts and 2 sample long episodes.

Short examples:
1. Sem Loses His Purple Color
2. Ulku’s Giant Eraser Problem
3. Dad Pencil’s Funny Farm Lesson

Long episode examples:
1. Sem Goes to the Farm
2. The Pencil Family and the Giant Crayon Castle

For each video create:
- script
- scene list
- voice lines
- image prompts
- OpenMontage editing plan
- thumbnail prompt
- title
- description
- hashtags

Save them under:

`examples/shorts/`
`examples/long_episodes/`

---

## TASK 9: IMPLEMENTATION

After creating the documentation and agents, implement the basic folder structure and starter files.

Create folders:

- agents/
- docs/
- examples/
- outputs/
- outputs/shorts/
- outputs/long_episodes/
- assets/
- assets/characters/
- assets/backgrounds/
- assets/props/
- scripts/
- scripts/shorts/
- scripts/long_episodes/

Do not delete any existing working files.

---

## TASK 10: FINAL OUTPUT

At the end, give me:

1. What files you created
2. How OpenMontage will be used
3. How to run daily Shorts
4. How to run 8-10 minute long episodes
5. What still needs API keys or manual setup
6. Next best improvement

Important:
Think like a senior video automation engineer.
Make this production-ready, not just a demo.
Keep it simple enough that I can actually run it.