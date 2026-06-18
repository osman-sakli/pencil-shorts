import React from "react";
import { useCurrentFrame } from "remotion";
import { CAST } from "./cast";
import { MouthShape, Position } from "./types";

const POSITION_STYLE: Record<Position, React.CSSProperties> = {
  left:   { left: "4%" },
  right:  { right: "4%", transform: "scaleX(-1)" },
  center: { left: "50%", transform: "translateX(-50%)" },
};

export const Character: React.FC<{
  characterId: string;
  mouth: MouthShape;
  position: Position;
  speaking: boolean;
  scale?: number;
  emotion?: string;
}> = ({ characterId, mouth, position, speaking, scale = 1, emotion = "neutral" }) => {
  const Cmp = CAST[characterId];
  const frame = useCurrentFrame();
  if (!Cmp) return null;

  // Gentle idle breathing bob (all characters)
  const breathe = Math.sin(frame * 0.05) * 3;
  // Extra bounce while speaking
  const speakBob = speaking ? Math.sin(frame * 0.5) * 5 : 0;
  // Slight lean-in while speaking
  const lean = speaking ? Math.sin(frame * 0.12) * 1.5 : 0;
  // Scale pulse on speaking character
  const scalePulse = speaking ? 1 + Math.sin(frame * 0.3) * 0.012 : 1;

  const bottomPx = 260 + breathe + speakBob;

  return (
    <div style={{
      position: "absolute",
      bottom: bottomPx,
      width: 300 * scale * scalePulse,
      ...POSITION_STYLE[position],
      filter: speaking ? "none" : "brightness(0.78) saturate(0.85)",
      transform: [
        POSITION_STYLE[position].transform ?? "",
        `rotate(${lean}deg)`,
      ].filter(Boolean).join(" "),
      transformOrigin: "bottom center",
    }}>
      <Cmp shape={mouth} emotion={emotion} />
    </div>
  );
};
