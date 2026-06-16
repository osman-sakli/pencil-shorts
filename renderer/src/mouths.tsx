import React from "react";
import { MouthShape } from "./types";

// Kawaii mouths drawn around local origin (0,0). Dark mauve fill.
// Rhubarb emits A-H + X; we map them onto 4 visual variants.
const FILL = "#7a2e3a";

const Closed = () => (
  <path d="M-9 0 Q0 6 9 0" stroke={FILL} strokeWidth={4} fill="none" strokeLinecap="round" />
);
const Small = () => <ellipse cx={0} cy={2} rx={6} ry={5} fill={FILL} />;
const Open = () => <ellipse cx={0} cy={3} rx={9} ry={8} fill={FILL} />;
const Wide = () => <ellipse cx={0} cy={4} rx={11} ry={11} fill={FILL} />;

const MAP: Record<MouthShape, React.FC> = {
  X: Closed,
  A: Closed, // closed (p, b, m)
  B: Small,  // slightly open
  C: Open,   // open
  D: Wide,   // wide open (a)
  E: Small,  // rounded slight (e, o)
  F: Small,  // tight rounded (u, w)
  G: Open,   // f, v
  H: Open,   // l
};

export const Mouth: React.FC<{ shape: MouthShape }> = ({ shape }) => {
  const Cmp = MAP[shape] ?? Closed;
  return <Cmp />;
};
