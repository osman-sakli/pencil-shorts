# YouTube Package Agent

## Purpose
Create YouTube title, description, hashtags, thumbnail prompt, and upload metadata for every video.

## Short Video Package

### Title Formula
```
[EMOJI] [CHARACTER] [FUNNY SITUATION] | #Shorts

Examples:
😂 Sem Floods The ENTIRE Bathroom! | #Shorts
🤣 Dad's WORST Life Advice Ever | #Shorts  
😱 Bas Goes VIRAL For The Wrong Reason! | #Shorts
```

### Description Template
```
{PUNCHY_CAPTION_FROM_SCRIPT} 🎉

The Pen Family is back with another chaotic adventure! 

Subscribe for daily Pen Family chaos → {CHANNEL_URL}

#ThePenFamily #KidsCartoon #FamilyFun #Shorts #AnimatedSeries #KidsYouTube
```

### Hashtag Sets
Always include: `#ThePenFamily #KidsCartoon #Shorts`
Add 2-3 from:
- `#FamilyFun #AnimatedFamily #KidsTv`
- `#FunnyKids #CutestKids #KidsContent`
- `#BabySem #PencilFamily #CartoonFamily`
- `#KidsSafety #FamilyComedy #TikTokKids`

### Thumbnail Prompt
```
The Pen Family thumbnail. [MAIN_REACTION_CHARACTER] looking shocked/excited with huge eyes.
Bright background. [KEY_PROP_FROM_STORY] visible. No text in image. 
Maximum 3 characters in frame. Colorful. 1280x720.
```

## Long Episode Package

### SEO Title Formula
```
[The Pen Family] [STORY PREMISE] | Funny Kids Cartoon [YEAR]

Examples:
The Pen Family Goes to the Farm! 🐄 | Funny Kids Cartoon 2026
Sem's BIGGEST Disaster Ever! | The Pen Family Full Episode
The Pen Family and the Giant Crayon Castle! 🏰 | Kids Animation
```

### Full Description Template
```
{EPISODE_PREMISE_2_SENTENCES}

In this episode: {BRIEF_SCENE_SUMMARY}

New episodes every 3 days! Subscribe so you never miss one 👉 {CHANNEL_URL}

⏱️ Timestamps:
0:00 - The Hook
0:45 - Family Intro  
1:35 - The Problem Starts
2:30 - First Attempt Fails
3:20 - Saf's Big Question
4:15 - The Adventure Begins
5:25 - Things Get Worse!
6:30 - Working Together
7:45 - The Lesson
8:30 - Funny Ending

#ThePenFamily #KidsCartoon #FamilyAnimation #KidsYouTube #AnimatedSeries #ChildrenContent #FunnyAnimation #FamilyFriendly
```

### Upload Metadata
```json
{
  "title": "...",
  "description": "...",
  "tags": ["The Pen Family", "kids cartoon", "animated series", "family fun", "kids youtube", "funny cartoon"],
  "category": "1",
  "made_for_kids": true,
  "language": "en",
  "thumbnail": "outputs/.../thumbnail.png"
}
```

## Platform-Specific Notes

| Platform | Title Max | Description | Hashtags |
|----------|-----------|-------------|---------|
| YouTube Shorts | 100 chars | 5000 chars | In description |
| YouTube Long | 100 chars | 5000 chars | In description |
| TikTok | 150 chars | In caption | Max 5 hashtags |
| Instagram | In caption | 2200 chars | Max 30 hashtags |
| Facebook | In caption | No limit | Max 10 hashtags |

## How to Generate Package Automatically
```bash
# After script.json is created, generate the full package:
python3 pipeline/generate_package.py --script out/script.json
# Outputs: out/youtube_package.json with title, description, hashtags, thumbnail_prompt
```

Note: `generate_package.py` does not yet exist — add to pipeline/long_episode.py roadmap.
