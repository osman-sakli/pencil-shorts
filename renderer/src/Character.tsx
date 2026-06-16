import React from "react";
import { CAST } from "./cast";
import { MouthShape, Position } from "./types";

const POSITION_STYLE: Record<Position, React.CSSProperties> = {
  left: { left: "6%" },
  right: { right: "6%", transform: "scaleX(-1)" }, // mirror so they face each other
  center: { left: "50%", transform: "translateX(-50%)" },
};

export const Character: React.FC<{
  characterId: string;
  mouth: MouthShape;
  position: Position;
  speaking: boolean;
  bob: number; // px vertical bob while speaking
  scale?: number;
}> = ({ characterId, mouth, position, speaking, bob, scale = 1 }) => {
  const Cmp = CAST[characterId];
  if (!Cmp) return null;
  return (
    <div
      style={{
        position: "absolute",
        bottom: `${10 + (speaking ? bob : 0)}%`,
        width: 360 * scale,
        ...POSITION_STYLE[position],
        filter: speaking ? "none" : "brightness(0.84) saturate(0.9)",
        transition: "filter 120ms linear",
      }}
    >
      <Cmp shape={mouth} />
    </div>
  );
};
