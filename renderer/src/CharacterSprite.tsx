import React from "react";
import { useCurrentFrame, Img, staticFile, spring, useVideoConfig } from "remotion";
import { MouthShape, Position } from "./types";

const SPRITE_H: Record<string, number> = {
  oz: 431, mas: 425, bas: 435, saf: 419, sem: 418, mira: 356,
  eli: 430, kit: 430, rex: 430, nib: 430,
};
const SPRITE_W: Record<string, number> = {
  oz: 163, mas: 220, bas: 237, saf: 246, sem: 300, mira: 236,
  eli: 220, kit: 220, rex: 220, nib: 220,
};
const CHAR_SCALE: Record<string, number> = {
  oz: 1.05, mas: 1.0, bas: 0.96, saf: 0.88, sem: 0.80, mira: 0.70,
  eli: 0.90, kit: 0.92, rex: 0.98, nib: 0.94,
};

const TARGET_H = 680;

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
}> = ({ characterId, position, speaking, mouth = "X", scale = 1, emotion = "neutral", entryFrame = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const sh = SPRITE_H[characterId] ?? 420;
  const sw = SPRITE_W[characterId] ?? 220;
  const baseScale = (CHAR_SCALE[characterId] ?? 1) * scale;
  const displayH = TARGET_H * baseScale;
  const displayW = displayH * (sw / sh);

  // Spring entrance: slides up from below when character first appears
  const entryProgress = spring({
    frame: Math.max(0, frame - entryFrame),
    fps,
    config: { damping: 18, stiffness: 180, mass: 0.8 },
  });
  const slideInY = (1 - entryProgress) * 320;
  const entryScale = 0.6 + entryProgress * 0.4;

  // Breathing — gentle idle float
  const breathe = Math.sin(frame * 0.06) * 4;

  // Speaking animations — more expressive
  const speakBob = speaking ? Math.sin(frame * 0.55) * 10 : 0;
  const lean = speaking ? Math.sin(frame * 0.12) * 3.5 : 0;
  const scalePulse = speaking ? 1 + Math.sin(frame * 0.32) * 0.03 : 1;

  // Emotion-based movement
  let emotionY = 0;
  let emotionShake = 0;
  let emotionBounce = 1;
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

  const bottomPx = 270 + breathe + speakBob + emotionY + slideInY;
  const posStyle = POS[position];

  // Combine all transforms
  const transforms: string[] = [];
  if (posStyle.transform) transforms.push(posStyle.transform as string);
  if (lean !== 0) transforms.push(`rotate(${lean + emotionShake}deg)`);
  else if (emotionShake !== 0) transforms.push(`rotate(${emotionShake}deg)`);

  return (
    <div style={{
      position: "absolute",
      bottom: bottomPx,
      width: displayW * scalePulse * emotionBounce * entryScale,
      height: displayH * scalePulse * emotionBounce * entryScale,
      filter: speaking
        ? "drop-shadow(0 8px 24px rgba(0,0,0,0.35))"
        : "brightness(0.70) saturate(0.75) drop-shadow(0 4px 12px rgba(0,0,0,0.20))",
      transform: transforms.filter(Boolean).join(" ") || undefined,
      transformOrigin: "bottom center",
      transition: "filter 0.15s ease",
      ...posStyle,
    }}>
      <Img
        src={staticFile(`characters/sprites/${characterId}.png`)}
        style={{ width: "100%", height: "100%", objectFit: "contain" }}
      />
    </div>
  );
};
