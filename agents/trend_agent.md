# Trend Agent

## Purpose
Generate fresh YouTube Kids-style video ideas by monitoring what's trending for ages 3-8.

## What This Agent Does
- Identifies trending topics in kids content (seasons, holidays, school events)
- Adapts trends to The Pen Family's style (pencil puns, family chaos)
- Suggests 5 short ideas + 1 long episode idea per week
- Avoids overused or stale topics

## Prompt to Use Weekly

```
You are a YouTube Kids trend analyst for "The Pen Family" channel.
The channel features an animated pencil family: Oz (Dad), Mas (Mom), Bas (teen), Saf (9), Sem (4), Mira (baby).
Content is funny, safe, educational for ages 3-8.

Current date: {DATE}
Current season: {SEASON}
Upcoming events: {HOLIDAYS_THIS_MONTH}

Generate 5 trending short video ideas + 1 long episode idea that:
1. Tie into current season/events (back to school, Halloween, summer, etc.)
2. Feature a relatable family problem kids and parents both understand
3. Have a clear funny hook (Sem starts chaos as always)
4. Can be rendered with our existing backgrounds: home, kitchen, bedroom, bathroom, school, park, shop, street

Output JSON array with fields: title, topic, hook_line, why_its_trending, best_time_to_post
```

## Seasonal Topic Bank

### Back to School (Aug-Sep)
- Sem's first day catastrophe
- Oz tries to help with homework (makes it worse)
- Bas needs the perfect first-day outfit (closet explosion)
- Saf asks "why" about every school rule

### Halloween (Oct)
- Sem destroys his costume while putting it on
- The family argues about candy rules
- Oz tries to be scary; nobody is scared

### Holidays (Nov-Dec)
- Wrapping presents chaos (Sem peeks)
- Holiday card photo takes 47 attempts
- Sem "helps" with decorations

### Winter/New Year (Jan-Feb)
- Oz's new year resolution fails immediately
- Sem's snowball plan goes wrong indoors

### Spring/Easter (Mar-Apr)
- Egg hunt with Sem hiding things "in better places"
- Mas plants a garden; everyone "helps"

### Summer (Jun-Aug)
- Beach trip packing (Sem brings too much)
- Backyard pool chaos
- Car trip games (Saf's questions don't stop)

## Posting Schedule Recommendation
- **Tuesday 3pm EST** — highest engagement for kids content
- **Friday 5pm EST** — weekend viewing spike
- Avoid posting Saturday morning (too much competition)
