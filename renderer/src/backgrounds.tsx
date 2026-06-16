import React from "react";
import { AbsoluteFill } from "remotion";

// Three code-drawn scenes (no image assets). Selected per beat for variety.
const Notebook: React.FC = () => (
  <AbsoluteFill
    style={{
      background:
        "repeating-linear-gradient(180deg,#fcfaf2 0 56px,#e6eef6 56px,#e6eef6 58px)",
    }}
  >
    <div style={{ position: "absolute", top: 0, bottom: 0, left: 70, width: 4, background: "#f2b8b8", opacity: 0.6 }} />
  </AbsoluteFill>
);

const Desk: React.FC = () => (
  <AbsoluteFill
    style={{
      background: "linear-gradient(180deg,#caa06a 0%,#b88a52 60%,#a87c46 100%)",
    }}
  >
    {/* wood grain hints */}
    {Array.from({ length: 10 }).map((_, i) => (
      <div key={i} style={{ position: "absolute", left: 0, right: 0, top: `${i * 11}%`, height: 2, background: "rgba(0,0,0,0.06)" }} />
    ))}
    {/* desk surface lower band */}
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, height: "26%", background: "rgba(255,255,255,0.06)" }} />
  </AbsoluteFill>
);

const PencilCase: React.FC = () => (
  <AbsoluteFill style={{ background: "linear-gradient(180deg,#3a4256 0%,#2a3142 100%)" }}>
    {/* zipper line near top */}
    <div style={{ position: "absolute", top: "10%", left: "8%", right: "8%", height: 6, background: "#8a93a8", borderRadius: 3 }} />
    {Array.from({ length: 24 }).map((_, i) => (
      <div key={i} style={{ position: "absolute", top: "10%", left: `${8 + i * 3.6}%`, width: 4, height: 6, background: "#aeb6c8" }} />
    ))}
    {/* fabric sheen */}
    <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse at 50% 120%, rgba(255,255,255,0.08), transparent 60%)" }} />
  </AbsoluteFill>
);

const SCENES: Record<string, React.FC> = {
  notebook: Notebook,
  desk: Desk,
  pencilcase: PencilCase,
};

export const SceneBg: React.FC<{ label: string }> = ({ label }) => {
  const Cmp = SCENES[label] ?? Notebook;
  return <Cmp />;
};
