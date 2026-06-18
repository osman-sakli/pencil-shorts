import React from "react";
import { useCurrentFrame } from "remotion";
import { MouthShape } from "./types";
import { Mouth } from "./mouths";

// ── Shared primitives ─────────────────────────────────────────────────────────

const OUT = "#3a2e24";

type EyeProps = {
  cx: number; cy: number; r?: number;
  lash?: boolean; blink: number; // blink: 0=open 1=closed
  emotion: string;
};

const Eye: React.FC<EyeProps> = ({ cx, cy, r = 15, lash = false, blink, emotion }) => {
  const scaleY = 1 - blink;
  const pupilOffset = emotion === "surprised" ? -2 : emotion === "sad" ? 2 : 0;
  const pupilR = emotion === "surprised" ? r * 0.65 : emotion === "happy" ? r * 0.5 : r * 0.58;
  return (
    <g transform={`translate(${cx},${cy}) scale(1,${scaleY}) translate(${-cx},${-cy})`}>
      <circle cx={cx} cy={cy} r={r} fill="#fff" stroke={OUT} strokeWidth={2} />
      <circle cx={cx + 2} cy={cy + pupilOffset} r={pupilR} fill="#1e1a28" />
      <circle cx={cx - 2} cy={cy - 3} r={r * 0.22} fill="#fff" />
      {lash && (
        <>
          <line x1={cx - r} y1={cy - 6} x2={cx - r - 7} y2={cy - 13} stroke={OUT} strokeWidth={2.5} strokeLinecap="round" />
          <line x1={cx} y1={cy - r} x2={cx - 2} y2={cy - r - 7} stroke={OUT} strokeWidth={2} strokeLinecap="round" />
        </>
      )}
    </g>
  );
};

type BrowProps = { cx: number; cy: number; emotion: string; flip?: boolean };
const Brow: React.FC<BrowProps> = ({ cx, cy, emotion, flip = false }) => {
  const angle = emotion === "angry" ? (flip ? 12 : -12)
    : emotion === "sad" ? (flip ? -8 : 8)
    : emotion === "surprised" ? -4
    : 0;
  const dy = emotion === "surprised" ? -5 : emotion === "angry" ? 3 : 0;
  return (
    <rect
      x={cx - 12} y={cy + dy - 4} width={24} height={5} rx={2.5}
      fill={OUT}
      transform={`rotate(${angle},${cx},${cy + dy})`}
    />
  );
};

// ── Base pen body ─────────────────────────────────────────────────────────────

type PenProps = {
  shape: MouthShape; emotion: string; blink: number;
  color: string; cap: string;
  acc?: React.ReactNode; lash?: boolean;
  cheekColor?: string;
};

const PenBody: React.FC<PenProps> = ({
  shape, emotion, blink, color, cap, acc, lash = false, cheekColor = "#ff96af"
}) => (
  <svg viewBox="0 0 160 360" width="100%" overflow="visible">
    {/* cap */}
    <rect x="40" y="36" width="80" height="66" rx="18" fill={cap} stroke={OUT} strokeWidth="5" />
    <rect x="104" y="46" width="9" height="48" rx="4" fill={cap} stroke={OUT} strokeWidth="2.5" />
    {/* highlight stripe */}
    <rect x="50" y="108" width="13" height="210" rx="6" fill="#fff" opacity="0.18" />
    {/* body */}
    <rect x="40" y="100" width="80" height="226" rx="18" fill={color} stroke={OUT} strokeWidth="5" />
    {/* tip */}
    <polygon points="68,326 92,326 80,350" fill="#3a3a44" stroke={OUT} strokeWidth="4" />
    {/* accessories */}
    {acc}
    {/* brows */}
    <Brow cx={61} cy={155} emotion={emotion} />
    <Brow cx={99} cy={155} emotion={emotion} flip />
    {/* eyes */}
    <Eye cx={61} cy={172} r={15} lash={lash} blink={blink} emotion={emotion} />
    <Eye cx={99} cy={172} r={15} lash={lash} blink={blink} emotion={emotion} />
    {/* cheeks */}
    <ellipse cx="46" cy="196" rx="11" ry="7" fill={cheekColor} opacity="0.5" />
    <ellipse cx="114" cy="196" rx="11" ry="7" fill={cheekColor} opacity="0.5" />
    {/* mouth */}
    <g transform="translate(80,206)"><Mouth shape={shape} /></g>
  </svg>
);

// ── Accessories ───────────────────────────────────────────────────────────────

const Glasses: React.FC = () => (
  <g stroke={OUT} strokeWidth="3.5" fill="none">
    <circle cx="61" cy="172" r="20" />
    <circle cx="99" cy="172" r="20" />
    <line x1="81" y1="172" x2="79" y2="172" />
    <line x1="41" y1="172" x2="32" y2="168" />
    <line x1="119" y1="172" x2="128" y2="168" />
  </g>
);

const Curl: React.FC = () => (
  <path d="M80 38 q16-14 4-28 q0 14-12 18 z" fill="#caa06a" stroke={OUT} strokeWidth="2.5" />
);

const Bow: React.FC<{ c: string }> = ({ c }) => (
  <g stroke={OUT} strokeWidth="3.5">
    <polygon points="80,40 54,26 54,58" fill={c} />
    <polygon points="80,40 106,26 106,58" fill={c} />
    <circle cx="80" cy="42" r="8" fill={c} />
  </g>
);

const Cowlick: React.FC = () => (
  <path d="M80 38 q-6-24 18-28 q-12 10-4 26 z" fill="#3a8c46" stroke={OUT} strokeWidth="2.5" />
);

const Paci: React.FC = () => (
  <>
    <circle cx="80" cy="238" r="10" fill="#ffd1dc" stroke={OUT} strokeWidth="2.5" />
    <circle cx="80" cy="238" r="4" fill="#ffb3c6" />
    <rect x="74" y="244" width="12" height="5" rx="2.5" fill="#ffd1dc" stroke={OUT} strokeWidth="2" />
  </>
);

// ── Character components ──────────────────────────────────────────────────────

type Props = { shape: MouthShape; emotion?: string };

function useBlink() {
  const frame = useCurrentFrame();
  // blink every ~90 frames (3s), duration 5 frames
  const cycle = 90;
  const pos = frame % cycle;
  return pos >= 85 ? Math.sin(((pos - 85) / 5) * Math.PI) : 0;
}

const Oz: React.FC<Props> = ({ shape, emotion = "neutral" }) => {
  const blink = useBlink();
  return <PenBody shape={shape} emotion={emotion} blink={blink}
    color="#3f6fc4" cap="#2f5398" acc={<Glasses />} cheekColor="#9bc2ff" />;
};

const Mas: React.FC<Props> = ({ shape, emotion = "neutral" }) => {
  const blink = useBlink();
  return <PenBody shape={shape} emotion={emotion} blink={blink}
    color="#ff7fa0" cap="#e85f86" acc={<Curl />} lash cheekColor="#ffb3c6" />;
};

const Bas: React.FC<Props> = ({ shape, emotion = "neutral" }) => {
  const blink = useBlink();
  return <PenBody shape={shape} emotion={emotion} blink={blink}
    color="#a06cd8" cap="#8450bd" acc={<Bow c="#c089f0" />} lash cheekColor="#d4b0ff" />;
};

const Saf: React.FC<Props> = ({ shape, emotion = "neutral" }) => {
  const blink = useBlink();
  return <PenBody shape={shape} emotion={emotion} blink={blink}
    color="#34bfb0" cap="#239b8e" acc={<Bow c="#5fd9cc" />} lash cheekColor="#8fe6db" />;
};

const Sem: React.FC<Props> = ({ shape, emotion = "neutral" }) => {
  const blink = useBlink();
  return <PenBody shape={shape} emotion={emotion} blink={blink}
    color="#4cae5a" cap="#3a8c46" acc={<Cowlick />} cheekColor="#a8e6b0" />;
};

const Mira: React.FC<Props> = ({ shape, emotion = "neutral" }) => {
  const blink = useBlink();
  return <PenBody shape={shape} emotion={emotion} blink={blink}
    color="#ffcc4d" cap="#e8b133" acc={<Paci />} cheekColor="#ffe08a" />;
};

export const CAST: Record<string, React.FC<Props>> = {
  oz: Oz, mas: Mas, bas: Bas, saf: Saf, sem: Sem, mira: Mira,
};
