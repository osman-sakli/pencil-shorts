# Voice Agent

## Purpose
Create voice direction for each character so every script writer and LLM knows exactly how each character sounds.

## Voice Configuration (Current)

All settings are in `characters.yaml`. Do not change without testing first.

| Character | Voice ID | Rate | Pitch | Style |
|-----------|----------|------|-------|-------|
| oz | en-US-ChristopherNeural | 0% | 0Hz | Deep, warm, Southern |
| mas | en-US-JennyNeural | 0% | 0Hz | Smart, direct, New York |
| bas | en-US-EmmaNeural | +10% | +20Hz | Fast teen, dramatic |
| saf | en-US-AnaNeural | 0% | 0Hz | Energetic, curious kid |
| sem | en-US-GuyNeural | +15% | +40Hz | Excited preschooler |
| mira | en-US-AnaNeural | -10% | +60Hz | Baby sounds only |
| eli | en-US-AndrewNeural | +5% | 0Hz | Cheerful neighbor |
| kit | en-US-EricNeural | 0% | 0Hz | Nerdy, precise |
| rex | en-US-SteffanNeural | -10% | -15Hz | Slow, authoritative grandpa |
| nib | en-US-AriaNeural | +8% | +10Hz | Dramatic, expressive aunt |

## Voice Direction Notes

### OZ — How to Write for His Voice
- Long words land well: "extraordinarily", "fundamentally"
- Southern expressions: "I'll be darned", "Bless your heart"
- Pauses work well — he thinks before he speaks
- Avoid slang or contractions that teenagers use
- Example: "Now hold on a second — back in my day, pencils didn't just..." ✅

### MAS — How to Write for Her Voice
- Short declarative sentences land best
- The faster the punchline, the better
- Her calm tone makes chaos funnier
- Example: "I already cleaned it up. Twice." ✅

### BAS — How to Write for Her Voice
- Rising intonation on questions ("seriously?")  
- Emphasize words in ALL CAPS in script for correct stress
- Teen abbreviations are okay: "literally", "lowkey", "slay"
- Example: "That is LITERALLY the most embarrassing thing ever." ✅

### SAF — How to Write for Her Voice
- Questions must end with genuine curiosity, not sarcasm
- She talks fast — short bursts work better than long sentences
- Example: "Wait but WHY does water do that?" ✅

### SEM — How to Write for His Voice
- Key mispronouncements to use: "pwan" (plan), "suprwise" (surprise), "elebant" (elephant)
- Short sentences only — 3-5 words max
- Exclamation marks are important: "I did it!!!" 
- Example: "I got a pwan! We put it... in da fridge!" ✅

### MIRA — How to Write for Her Voice
- Maximum ONE WORD per beat
- Sounds: "Ba!", "Uh!", "Hehe!", "Yay!"
- Names: "Se!" (Sem), "Dada!", "Mama!"
- Example: "Uh-oh!" ✅ / "I think we should all calm down" ❌

## EdgeTTS Quality Tips
- Rate between -20% and +20% sounds natural
- Pitch between -30Hz and +60Hz sounds natural
- Beyond these ranges sounds robotic
- Test new voices with: `edge-tts --voice <id> --text "test line" --write-media test.mp3`

## Available EdgeTTS Voice Options (English US)
Run this to see all options: `edge-tts --list-voices | grep en-US`

Top alternatives if current voices need changing:
- Older male: en-US-BrianMultilingualNeural
- Younger female: en-US-MichelleNeural  
- Grandma: en-US-JaneNeural (with -15% rate, -10Hz pitch)
- Baby alternative: en-GB-MiaNeural (with +50Hz pitch)
