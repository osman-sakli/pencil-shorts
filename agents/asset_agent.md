# Asset Agent

## Purpose
Generate image prompts for characters, backgrounds, props, and thumbnails.  
This agent produces prompts — a human or image generation tool creates the actual images.

## Character Image Prompts

### For new character sprites (PNG, transparent background)
```
Prompt template:
"3D Pixar-style animated [OBJECT] character. [COLOR] colored body. Cute googly eyes. 
Simple friendly face. Cartoon legs. Transparent background. 1080x1080 resolution. 
No text. Family-friendly. Bright and colorful. Character name: [NAME]."

oz: "3D Pixar-style animated pen character. Deep blue colored body with golden clip. 
Warm friendly eyes. Small round belly. Transparent background. 1080x1080."

mas: "3D Pixar-style animated pen character. Soft pink body with rose gold clip. 
Smart confident eyes. Slight smile. Transparent background. 1080x1080."

bas: "3D Pixar-style animated pen character. Teal colored body. Stylish appearance. 
Long eyelashes. Slightly dramatic expression. Teen energy. Transparent background."

saf: "3D Pixar-style animated pen character. Purple body. Smaller size. Big curious eyes. 
Question mark pattern on body. Energetic pose. Transparent background."

sem: "3D Pixar-style animated pen character. Bright green small body. Very small. 
Big innocent eyes. Slight mischievous grin. Tiny little legs. Transparent background."

mira: "3D Pixar-style animated pen character. Bright yellow tiny baby body. 
Huge innocent baby eyes. Chubby little shape. Tiny hands. Transparent background."
```

## Background Prompts (for future photo backgrounds)
```
home: "Bright cheerful cartoon living room. Colorful couch. Family photos on wall. 
TV. Warm lighting. No people. Kids cartoon style. 1080x1920 vertical."

kitchen: "Colorful cartoon kitchen. Bright yellow walls. Cereal boxes on counter. 
Fruit bowl. Fridge with drawings on it. Morning light. 1080x1920 vertical."

bedroom: "Cute cartoon kids bedroom. Star posters. Colorful bed. Night lamp. 
Toys on floor. Purple and blue tones. 1080x1920 vertical."

school: "Bright cartoon classroom. Green chalkboard. Colorful cubbies. Alphabet 
border. Teacher's desk. Morning light. 1080x1920 vertical."

park: "Sunny cartoon outdoor park. Bright green grass. Playground equipment. 
Blue sky. Flowers. No people. 1080x1920 vertical."
```

## Thumbnail Prompts

### For Short Videos
```
Template: "The Pen Family cartoon thumbnail. [MAIN CHARACTER] looking shocked/surprised/
excited. Bright background. Bold text space at top. Big eyes. Colorful. 
No text in image. 1280x720 pixels. YouTube thumbnail style."

Best thumbnail characters:
- Sem (green, small, shocked face) — highest CTR
- Full family chaos shot — second highest  
- Mira doing something unexpected — very clickable
```

### For Long Episodes
```
"The Pen Family long episode thumbnail. Sem in center looking chaotic. 
Other family members reacting around him. Bright saturated colors. 
Episode theme visible in background. No text. 1280x720."
```

## Prop Prompts
```
rubber_duck: "3D cartoon rubber duck. Yellow. Pixar style. No background. PNG."
crayon_box: "3D cartoon crayon box. Open with colorful crayons. Pixar style. PNG."
homework_paper: "3D cartoon homework paper with pencil. Pixar style. PNG."
birthday_cake: "3D cartoon birthday cake. Colorful frosting. Pixar style. PNG."
```

## How to Generate Images
1. Take any prompt above
2. Use any of these tools:
   - DALL-E 3 via ChatGPT
   - Midjourney (add `--ar 9:16` for vertical backgrounds)
   - Stable Diffusion (local, free)
   - Adobe Firefly (no copyright concerns)
3. Save PNG files to:
   - Characters: `characters/sprites/{id}.png`
   - Backgrounds: `assets/backgrounds/{label}.png`
   - Props: `assets/props/{name}.png`
   - Thumbnails: `outputs/shorts/{date}/thumbnail.png`
