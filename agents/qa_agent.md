# QA Agent

## Purpose
Check child safety, character consistency, story quality, and video readiness before publishing.

## Automated Checks (Already Running in Pipeline)
- ✅ Bad word filter in `generate_script.py` (_clean_text function)
- ✅ Beat count validation (≥15 beats)
- ✅ Word count per line (≤12 words)
- ✅ Character ID validation
- ✅ Background label validation

## Manual QA Checklist (Run Before Publishing Long Episodes)

### Child Safety
- [ ] No violence or physical threats
- [ ] No scary imagery (monsters, death, dark themes)
- [ ] No adult humor, innuendo, or double meanings
- [ ] No political or religious references
- [ ] No brand names used in potentially negative way
- [ ] No dangerous behaviors shown as "cool" or funny
- [ ] Lesson is positive and age-appropriate

### Character Consistency
- [ ] Sem uses short sentences (max 6 words) and mispronounces at least one word
- [ ] Mira NEVER speaks full sentences (one word maximum)
- [ ] Mas is calm throughout — never panics
- [ ] Oz does not use teen slang
- [ ] Bas references content / social media in at least one line
- [ ] Saf asks at least one question per scene

### Story Quality
- [ ] Episode opens mid-chaos (no slow setup)
- [ ] Problem is established clearly by act 3
- [ ] Each act advances the story (no filler)
- [ ] Lesson is shown through action, not stated as dialogue
- [ ] Ending is funny and satisfying
- [ ] Kids would want to watch the next episode

### Technical Quality
- [ ] Video is 60-75s (shorts) or 8:00-10:30 (long episodes)
- [ ] No audio clicks or pops between beats
- [ ] Character mouths move (lip sync working)
- [ ] Subtitles match spoken audio
- [ ] Background matches scene description
- [ ] No frozen frames or render artifacts

## QA Prompt for LLM Review

Run this against the script.json before rendering:
```
Review this kids video script for "The Pen Family" animated series.
Target audience: Ages 3-8.

Check for:
1. Any content inappropriate for young children
2. Character consistency violations (see character rules)
3. Story logic issues (does the plot make sense?)
4. Missing required elements (Sem mispronounces, Saf asks question, Mira does something)
5. Pacing issues (too slow, monologues, not enough reactions)

Script: {SCRIPT_JSON}

Return JSON:
{
  "passed": true/false,
  "issues": ["list of problems found"],
  "score": 1-10,
  "recommendation": "publish|revise|regenerate"
}
```

## Failure Handling
| Issue | Action |
|-------|--------|
| Bad word found | Already filtered automatically → log and continue |
| Too short (<60s) | Add 2-3 beats to script, re-render |
| Character OOC | Regenerate script with same topic |
| Technical artifact | Check Remotion logs, re-render |
| Story makes no sense | Regenerate script |
| Child safety flag | Stop — do not publish. Fix script. |
