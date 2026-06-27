import React from "react";
import { useCurrentFrame, Img, staticFile, spring, useVideoConfig } from "remotion";
import { MouthShape, Position } from "./types";

// Family members with AI-generated emotion sprites
const AI_CHARS = new Set(["oz", "mas", "bas", "saf", "sem", "mira", "biscuit", "mittens", "snip"]);
const VALID_EMOTIONS = new Set(["neutral", "happy", "angry", "surprised", "sad"]);

const SPRITE_H: Record<string, number> = {
  oz: 431, mas: 425, bas: 435, saf: 419, sem: 418, mira: 356,
  eli: 430, kit: 430, rex: 430, nib: 430,
  biscuit: 420, mittens: 400, snip: 380,
};
const SPRITE_W: Record<string, number> = {
  oz: 163, mas: 220, bas: 237, saf: 246, sem: 300, mira: 236,
  eli: 220, kit: 220, rex: 220, nib: 220,
  biscuit: 280, mittens: 260, snip: 200,
};
const CHAR_SCALE: Record<string, number> = {
  oz: 1.05, mas: 1.0, bas: 0.96, saf: 0.88, sem: 0.80, mira: 0.70,
  eli: 0.90, kit: 0.92, rex: 0.98, nib: 0.94,
  biscuit: 0.72, mittens: 0.65, snip: 0.85,
};

// Responsive: 980px cap in portrait, 78% of height in landscape
const useTargetH = () => {
  const { height } = useVideoConfig();
  return Math.min(980, height * 0.78);
};

const POS: Record<Position, React.CSSProperties> = {
  left:   { left: "3%" },
  right:  { right: "3%", transform: "scaleX(-1)" },
  center: { left: "50%", transform: "translateX(-50%)" },
};

export const CharacterSprite: React.FC<{
  characterId: string;
  position: Position;
  speaking: boolean;
  mouth?: MouthShape;
  scale?: number;
  emotion?: string;
  entryFrame?: number;
  beatStartFrame?: number; // for per-beat zoom-in effect on speaker
}> = ({ characterId, position, speaking, mouth = "X", scale = 1, emotion = "neutral", entryFrame = 0, beatStartFrame }) => {
  const frame = useCurrentFrame();
  const { fps, height } = useVideoConfig();
  const BASE_BOTTOM = height > 1200 ? 270 : 65;

  const sh = SPRITE_H[characterId] ?? 420;
  const sw = SPRITE_W[characterId] ?? 220;
  const baseScale = (CHAR_SCALE[characterId] ?? 1) * scale;
  const TARGET_H = useTargetH();
  const displayH = TARGET_H * baseScale;
  const displayW = displayH * (sw / sh);

  // Spring entrance: slides up from below on first appearance
  const entryProgress = spring({
    frame: Math.max(0, frame - entryFrame),
    fps,
    config: { damping: 18, stiffness: 180, mass: 0.8 },
  });
  const slideInY = (1 - entryProgress) * 320;
  const entryScale = 0.6 + entryProgress * 0.4;

  // Speaker: zoom in at each beat start (0.82 → 1.0 over ~20 frames)
  const beatZoomProgress = (speaking && beatStartFrame !== undefined)
    ? spring({ frame: Math.max(0, frame - beatStartFrame), fps, config: { damping: 13, stiffness: 260, mass: 0.45 } })
    : 1;
  const beatZoom = speaking ? (0.76 + beatZoomProgress * 0.24) : 1;

  // Speaker: continuous animations. Listener: completely static.
  const breathe = speaking ? Math.sin(frame * 0.06) * 4 : 0;
  const speakBob = speaking ? Math.sin(frame * 0.55) * 10 : 0;
  const lean = speaking ? Math.sin(frame * 0.12) * 3.5 : 0;
  const scalePulse = speaking ? 1 + Math.sin(frame * 0.32) * 0.03 : 1;

  // Emotion movement (speaker only)
  let emotionY = 0;
  let emotionShake = 0;
  let emotionBounce = 1;
  if (speaking) {
    if (emotion === "happy") {
      emotionBounce = 1 + Math.abs(Math.sin(frame * 0.4)) * 0.06;
      emotionY = -Math.abs(Math.sin(frame * 0.4)) * 8;
    } else if (emotion === "angry") {
      emotionShake = Math.sin(frame * 1.2) * 4;
    } else if (emotion === "surprised") {
      emotionY = -12;
      emotionBounce = 1.08;
    } else if (emotion === "sad") {
      emotionY = 6;
    }
  }

  const bottomPx = BASE_BOTTOM + breathe + speakBob + emotionY + slideInY;
  const posStyle = POS[position];

  const transforms: string[] = [];
  if (posStyle.transform) transforms.push(posStyle.transform as string);
  if (lean !== 0) transforms.push(`rotate(${lean + emotionShake}deg)`);
  else if (emotionShake !== 0) transforms.push(`rotate(${emotionShake}deg)`);

  const totalScale = scalePulse * emotionBounce * entryScale * beatZoom;

  return (
    <div style={{
      position: "absolute",
      bottom: bottomPx,
      width: displayW * totalScale,
      height: displayH * totalScale,
      filter: speaking
        ? "drop-shadow(0 10px 28px rgba(0,0,0,0.40))"
        : "brightness(0.62) saturate(0.65) drop-shadow(0 2px 8px rgba(0,0,0,0.15))",
      transform: transforms.filter(Boolean).join(" ") || undefined,
      transformOrigin: "bottom center",
      transition: "filter 0.12s ease",
      zIndex: speaking ? 10 : 5,
      ...posStyle,
    }}>
      <Img
        src={staticFile(
          AI_CHARS.has(characterId)
            ? `characters/sprites/${characterId}_${VALID_EMOTIONS.has(emotion) ? emotion : "neutral"}.png`
            : `characters/sprites/${characterId}.png`
        )}
        style={{ width: "100%", height: "100%", objectFit: "contain" }}
      />
    </div>
  );
};
