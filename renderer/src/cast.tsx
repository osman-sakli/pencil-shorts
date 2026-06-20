import React from "react";
import { useCurrentFrame } from "remotion";
import { MouthShape } from "./types";
import { Mouth } from "./mouths";

const OUT = "#2a1e14";

// ── Eye ───────────────────────────────────────────────────────────────────────

type EyeProps = { cx: number; cy: number; r?: number; lash?: boolean; blink: number; emotion: string };

const Eye: React.FC<EyeProps> = ({ cx, cy, r = 18, lash = false, blink, emotion }) => {
  const scaleY = 1 - blink;
  const pupilShift = emotion === "surprised" ? -3 : emotion === "sad" ? 2 : 0;
  const pupilR = emotion === "surprised" ? r * 0.58 : emotion === "happy" ? r * 0.46 : r * 0.52;
  return (
    <g transform={`translate(${cx},${cy}) scale(1,${scaleY}) translate(${-cx},${-cy})`}>
      {/* white */}
      <circle cx={cx} cy={cy} r={r} fill="#fff" stroke={OUT} strokeWidth={2.5} />
      {/* iris */}
      <circle cx={cx} cy={cy + pupilShift} r={pupilR * 1.18} fill="#3a2060" />
      {/* pupil */}
      <circle cx={cx} cy={cy + pupilShift} r={pupilR} fill="#0d0a14" />
      {/* highlights */}
      <circle cx={cx - r * 0.28} cy={cy - r * 0.3 + pupilShift} r={r * 0.22} fill="#fff" opacity={0.92} />
      <circle cx={cx + r * 0.18} cy={cy + r * 0.12 + pupilShift} r={r * 0.12} fill="#fff" opacity={0.65} />
      {lash && (
        <>
          <line x1={cx - r * 0.9} y1={cy - r * 0.3} x2={cx - r * 1.35} y2={cy - r * 0.85} stroke={OUT} strokeWidth={2.8} strokeLinecap="round" />
          <line x1={cx - r * 0.3} y1={cy - r * 0.95} x2={cx - r * 0.42} y2={cy - r * 1.45} stroke={OUT} strokeWidth={2.4} strokeLinecap="round" />
          <line x1={cx + r * 0.28} y1={cy - r * 0.94} x2={cx + r * 0.28} y2={cy - r * 1.42} stroke={OUT} strokeWidth={2.2} strokeLinecap="round" />
        </>
      )}
    </g>
  );
};

// ── Brow ──────────────────────────────────────────────────────────────────────

type BrowProps = { cx: number; cy: number; emotion: string; flip?: boolean };
const Brow: React.FC<BrowProps> = ({ cx, cy, emotion, flip = false }) => {
  const angle = emotion === "angry" ? (flip ? 14 : -14)
    : emotion === "sad" ? (flip ? -10 : 10)
    : emotion === "surprised" ? -6 : 0;
  const dy = emotion === "surprised" ? -7 : emotion === "angry" ? 2 : 0;
  return (
    <rect x={cx - 14} y={cy + dy - 4} width={28} height={5.5} rx={2.8}
      fill={OUT} transform={`rotate(${angle},${cx},${cy + dy})`} />
  );
};

// ── Arms ──────────────────────────────────────────────────────────────────────

type ArmPose = "hip" | "wave" | "cross" | "peace" | "idle";
type ArmsProps = { color: string; pose?: ArmPose };

const Arms: React.FC<ArmsProps> = ({ color, pose = "idle" }) => {
  const s = { fill: color, stroke: OUT, strokeWidth: 4 };
  const h = { fill: color, stroke: OUT, strokeWidth: 3 };
  if (pose === "hip") return (
    <>
      <ellipse cx={24} cy={232} rx={20} ry={12} {...s} transform="rotate(-28,24,232)" />
      <ellipse cx={136} cy={232} rx={20} ry={12} {...s} transform="rotate(28,136,232)" />
    </>
  );
  if (pose === "wave") return (
    <>
      <ellipse cx={22} cy={240} rx={18} ry={11} {...s} transform="rotate(-22,22,240)" />
      <ellipse cx={138} cy={210} rx={18} ry={11} {...s} transform="rotate(-52,138,210)" />
      {/* waving hand */}
      <circle cx={142} cy={196} r={10} {...h} />
    </>
  );
  if (pose === "cross") return (
    <>
      <ellipse cx={56} cy={258} rx={26} ry={11} {...s} transform="rotate(-10,56,258)" />
      <ellipse cx={104} cy={258} rx={26} ry={11} {...s} transform="rotate(10,104,258)" />
    </>
  );
  if (pose === "peace") return (
    <>
      <ellipse cx={22} cy={235} rx={18} ry={11} {...s} transform="rotate(-22,22,235)" />
      <ellipse cx={138} cy={200} rx={18} ry={11} {...s} transform="rotate(-58,138,200)" />
      {/* peace-sign hand hint */}
      <line x1={133} y1={188} x2={138} y2={179} stroke={OUT} strokeWidth={3} strokeLinecap="round" />
      <line x1={141} y1={187} x2={146} y2={178} stroke={OUT} strokeWidth={3} strokeLinecap="round" />
    </>
  );
  // idle
  return (
    <>
      <ellipse cx={24} cy={240} rx={18} ry={11} {...s} transform="rotate(-16,24,240)" />
      <ellipse cx={136} cy={240} rx={18} ry={11} {...s} transform="rotate(16,136,240)" />
    </>
  );
};

// ── Base pen body ─────────────────────────────────────────────────────────────

type PenProps = {
  shape: MouthShape; emotion: string; blink: number;
  color: string; cap: string;
  acc?: React.ReactNode; lash?: boolean;
  cheekColor?: string; armPose?: ArmPose;
};

const PenBody: React.FC<PenProps> = ({
  shape, emotion, blink, color, cap, acc, lash = false,
  cheekColor = "#ff96af", armPose = "idle",
}) => (
  <svg viewBox="0 0 160 360" width="100%" overflow="visible">
    {/* arms (behind body) */}
    <Arms color={color} pose={armPose} />

    {/* cap */}
    <rect x={40} y={36} width={80} height={66} rx={18} fill={cap} stroke={OUT} strokeWidth={5} />
    {/* clip ring */}
    <rect x={104} y={46} width={10} height={48} rx={4.5} fill={cap} stroke={OUT} strokeWidth={2.5} />

    {/* body */}
    <rect x={40} y={100} width={80} height={226} rx={18} fill={color} stroke={OUT} strokeWidth={5} />
    {/* gloss highlight */}
    <rect x={50} y={108} width={12} height={208} rx={6} fill="#fff" opacity={0.2} />

    {/* tip */}
    <polygon points="67,326 93,326 80,352" fill="#3a3a44" stroke={OUT} strokeWidth={4} />

    {/* accessories */}
    {acc}

    {/* brows */}
    <Brow cx={57} cy={145} emotion={emotion} />
    <Brow cx={103} cy={145} emotion={emotion} flip />

    {/* eyes — big & expressive */}
    <Eye cx={57} cy={166} r={18} lash={lash} blink={blink} emotion={emotion} />
    <Eye cx={103} cy={166} r={18} lash={lash} blink={blink} emotion={emotion} />

    {/* rosy cheeks */}
    <ellipse cx={40} cy={191} rx={13} ry={8} fill={cheekColor} opacity={0.5} />
    <ellipse cx={120} cy={191} rx={13} ry={8} fill={cheekColor} opacity={0.5} />

    {/* mouth */}
    <g transform="translate(80,203)"><Mouth shape={shape} /></g>
  </svg>
);

// ── Accessories ───────────────────────────────────────────────────────────────

const Glasses: React.FC = () => (
  <g stroke={OUT} strokeWidth={3.5} fill="none">
    <circle cx={57} cy={166} r={22} />
    <circle cx={103} cy={166} r={22} />
    <line x1={79} y1={166} x2={81} y2={166} />
    <line x1={35} y1={162} x2={26} y2={158} />
    <line x1={125} y1={162} x2={134} y2={158} />
  </g>
);

const Tie: React.FC<{ c: string }> = ({ c }) => (
  <g>
    <polygon points="80,208 74,224 80,298 86,224" fill={c} stroke={OUT} strokeWidth={2} />
    <polygon points="80,208 73,217 80,228 87,217" fill="#e8f4ff" stroke={OUT} strokeWidth={2} />
  </g>
);

const Pearls: React.FC = () => (
  <g>
    {[56, 63, 70, 77, 83, 90, 97, 104].map((x, i) => (
      <circle key={i} cx={x} cy={218} r={4.5} fill="#f5ede8" stroke="#c8b8a8" strokeWidth={1.5} />
    ))}
  </g>
);

const Curl: React.FC = () => (
  <path d="M78 38 q18-16 5-30 q1 15-12 20 z" fill="#cc9e62" stroke={OUT} strokeWidth={2.5} />
);

const BigBow: React.FC<{ c: string }> = ({ c }) => (
  <g stroke={OUT} strokeWidth={4}>
    <polygon points="80,34 46,13 46,55" fill={c} />
    <polygon points="80,34 114,13 114,55" fill={c} />
    <circle cx={80} cy={36} r={12} fill={c} />
    <circle cx={80} cy={36} r={5} fill="#fff" opacity={0.35} />
  </g>
);

const SmallBow: React.FC<{ c: string }> = ({ c }) => (
  <g stroke={OUT} strokeWidth={3.5}>
    <polygon points="80,40 62,28 62,52" fill={c} />
    <polygon points="80,40 98,28 98,52" fill={c} />
    <circle cx={80} cy={42} r={8} fill={c} />
  </g>
);

// Hoodie zipper stripes for Sem
const HoodieStripes: React.FC<{ c: string }> = ({ c }) => (
  <g>
    {/* center zip line */}
    <line x1={80} y1={208} x2={80} y2={298} stroke={OUT} strokeWidth={3} strokeLinecap="round" />
    {/* left stripe */}
    <rect x={54} y={210} width={9} height={86} rx={4} fill={c} stroke={OUT} strokeWidth={2} opacity={0.7} />
    {/* right stripe */}
    <rect x={97} y={210} width={9} height={86} rx={4} fill={c} stroke={OUT} strokeWidth={2} opacity={0.7} />
  </g>
);

const Paci: React.FC = () => (
  <>
    <circle cx={80} cy={226} r={11} fill="#ffd1dc" stroke={OUT} strokeWidth={2.5} />
    <circle cx={80} cy={226} r={4.5} fill="#ffb3c6" />
    <rect x={73} y={233} width={14} height={6} rx={3} fill="#ffd1dc" stroke={OUT} strokeWidth={2} />
  </>
);

const Flower: React.FC = () => (
  <g transform="translate(118,44)">
    {[0, 60, 120, 180, 240, 300].map(a => (
      <ellipse key={a} cx={0} cy={-9} rx={5.5} ry={8.5} fill="#ffd966" stroke={OUT} strokeWidth={2}
        transform={`rotate(${a})`} />
    ))}
    <circle cx={0} cy={0} r={6.5} fill="#ffcc4d" stroke={OUT} strokeWidth={2} />
  </g>
);

// Heart necklace for Bas and Saf
const HeartNecklace: React.FC<{ c: string }> = ({ c }) => (
  <g>
    {[60,67,73,80,87,93,100].map((x, i) => (
      <circle key={i} cx={x} cy={217} r={3.5} fill="#e0d8f0" stroke="#c0b8d8" strokeWidth={1.2} />
    ))}
    {/* heart pendant */}
    <path d="M80,226 q-2-5 -6-5 q-5,0 -5,5 q0,3 5,7 q1,1 6,5 q5,-4 6,-5 q5,-4 5,-7 q0,-5 -5,-5 q-4,0 -6,5 z"
      fill={c} stroke={OUT} strokeWidth={2} />
  </g>
);

// ── Characters ────────────────────────────────────────────────────────────────

type Props = { shape: MouthShape; emotion?: string };

function useBlink() {
  const frame = useCurrentFrame();
  const pos = frame % 90;
  return pos >= 85 ? Math.sin(((pos - 85) / 5) * Math.PI) : 0;
}

const Oz: React.FC<Props> = ({ shape, emotion = "neutral" }) => {
  const blink = useBlink();
  return <PenBody shape={shape} emotion={emotion} blink={blink}
    color="#3f6fc4" cap="#2f5398" lash={false}
    acc={<><Glasses /><Tie c="#6aaeff" /></>}
    cheekColor="#9bc2ff" armPose="cross" />;
};

const Mas: React.FC<Props> = ({ shape, emotion = "neutral" }) => {
  const blink = useBlink();
  return <PenBody shape={shape} emotion={emotion} blink={blink}
    color="#ff7fa0" cap="#e85f86" lash
    acc={<><Curl /><Pearls /></>}
    cheekColor="#ffb3c6" armPose="wave" />;
};

const Bas: React.FC<Props> = ({ shape, emotion = "neutral" }) => {
  const blink = useBlink();
  return <PenBody shape={shape} emotion={emotion} blink={blink}
    color="#a06cd8" cap="#8450bd" lash
    acc={<><BigBow c="#c089f0" /><HeartNecklace c="#9955cc" /></>}
    cheekColor="#d4b0ff" armPose="peace" />;
};

const Saf: React.FC<Props> = ({ shape, emotion = "neutral" }) => {
  const blink = useBlink();
  return <PenBody shape={shape} emotion={emotion} blink={blink}
    color="#34bfb0" cap="#239b8e" lash
    acc={<><SmallBow c="#5fd9cc" /><HeartNecklace c="#1da898" /></>}
    cheekColor="#8fe6db" armPose="wave" />;
};

const Sem: React.FC<Props> = ({ shape, emotion = "neutral" }) => {
  const blink = useBlink();
  return <PenBody shape={shape} emotion={emotion} blink={blink}
    color="#4cae5a" cap="#3a8c46" lash={false}
    acc={<HoodieStripes c="#2e7a38" />}
    cheekColor="#a8e6b0" armPose="cross" />;
};

const Mira: React.FC<Props> = ({ shape, emotion = "neutral" }) => {
  const blink = useBlink();
  return <PenBody shape={shape} emotion={emotion} blink={blink}
    color="#ffcc4d" cap="#e8b133" lash
    acc={<><Flower /><Paci /></>}
    cheekColor="#ffe08a" armPose="wave" />;
};

export const CAST: Record<string, React.FC<Props>> = {
  oz: Oz, mas: Mas, bas: Bas, saf: Saf, sem: Sem, mira: Mira,
};
