import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";

// ── Single floating particle ────────────────────────────────────────────────
interface ParticleProps {
  x: number;
  y: number;
  delay: number;
  emoji: string;
  size: number;
}

const Particle: React.FC<ParticleProps> = ({ x, y, delay, emoji, size }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f = frame - delay;
  if (f < 0 || f > 55) return null;

  const sc = spring({ frame: f, fps, config: { damping: 9, stiffness: 200, mass: 0.4 } });
  const opacity = interpolate(f, [0, 6, 38, 55], [0, 1, 1, 0], { extrapolateRight: "clamp" });
  const drift = interpolate(f, [0, 55], [0, -55], { extrapolateRight: "clamp" });
  const sway = Math.sin((f / 55) * Math.PI * 2) * 14;

  return (
    <div style={{
      position: "absolute",
      left: `${x}%`,
      top: `${y}%`,
      fontSize: size,
      transform: `translate(${sway}px, ${drift}px) scale(${sc})`,
      opacity,
      pointerEvents: "none",
      userSelect: "none",
      lineHeight: 1,
    }}>
      {emoji}
    </div>
  );
};

// ── Emotion-specific burst of particles ────────────────────────────────────
const EMOTION_CFG: Record<string, { emojis: string[]; count: number }> = {
  happy:     { emojis: ["⭐", "✨", "💫", "🌟"], count: 6 },
  surprised: { emojis: ["✨", "💥", "⚡", "✨"], count: 7 },
  angry:     { emojis: ["💢", "🔥", "⚡", "💢"], count: 4 },
  sad:       { emojis: ["💧", "💧", "😢", "💧"], count: 4 },
  neutral:   { emojis: ["✨", "✦", "✨", "✦"],   count: 3 },
};

export const EmotionBurst: React.FC<{ emotion: string; beatStart: number }> = ({ emotion, beatStart }) => {
  const frame = useCurrentFrame();
  const local = frame - beatStart;
  if (local < 0 || local > 55) return null;

  const cfg = EMOTION_CFG[emotion] ?? EMOTION_CFG.neutral;
  const particles = Array.from({ length: cfg.count }, (_, i) => {
    const angle = (i / cfg.count) * 2 * Math.PI + 0.3;
    return {
      x: 50 + Math.cos(angle) * 28,
      y: 40 + Math.sin(angle) * 20,
      delay: beatStart + i * 2,
      emoji: cfg.emojis[i % cfg.emojis.length],
      size: 22 + (i % 3) * 8,
    };
  });

  return (
    <>
      {particles.map((p, i) => <Particle key={i} {...p} />)}
    </>
  );
};

// ── Brief white flash on scene change ──────────────────────────────────────
export const ScreenFlash: React.FC<{ beatStart: number }> = ({ beatStart }) => {
  const frame = useCurrentFrame();
  const f = frame - beatStart;
  if (f < 0 || f > 10) return null;

  const opacity = interpolate(f, [0, 2, 10], [0.55, 0.25, 0], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: `rgba(255,255,255,${opacity})`, pointerEvents: "none" }} />
  );
};

// ── Always-on floating decorative stars (cartoon mode only) ─────────────────
const STAR_DEFS = [
  { x: 7,  y: 10, period: 90,  phase: 0,  size: 18 },
  { x: 87, y: 7,  period: 115, phase: 28, size: 22 },
  { x: 4,  y: 52, period: 100, phase: 14, size: 15 },
  { x: 91, y: 58, period: 80,  phase: 43, size: 19 },
  { x: 50, y: 4,  period: 105, phase: 60, size: 14 },
  { x: 15, y: 82, period: 95,  phase: 22, size: 16 },
  { x: 82, y: 85, period: 120, phase: 50, size: 17 },
];

export const FloatingStars: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      {STAR_DEFS.map((s, i) => {
        const t = (frame + s.phase) / s.period;
        const floatY = Math.sin(t * 2 * Math.PI) * 10;
        const opacity = 0.45 + Math.sin(t * 2 * Math.PI + 1.2) * 0.25;
        const rotate = ((frame + s.phase) * 1.8) % 360;
        return (
          <div key={i} style={{
            position: "absolute",
            left: `${s.x}%`,
            top: `${s.y}%`,
            fontSize: s.size,
            transform: `translateY(${floatY}px) rotate(${rotate}deg)`,
            opacity,
            pointerEvents: "none",
            userSelect: "none",
          }}>✦</div>
        );
      })}
    </>
  );
};

// ── Glowing color orbs that drift slowly (cartoon mode background glow) ─────
const ORB_DEFS = [
  { x: 8,  y: 12, r: 80,  color: "rgba(255,220,80,0.22)",  period: 130, phase: 0 },
  { x: 84, y: 16, r: 70,  color: "rgba(100,200,255,0.18)", period: 100, phase: 35 },
  { x: 6,  y: 68, r: 75,  color: "rgba(255,130,200,0.18)", period: 110, phase: 18 },
  { x: 88, y: 72, r: 65,  color: "rgba(120,255,150,0.18)", period: 90,  phase: 55 },
];

export const ColorOrbs: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <>
      {ORB_DEFS.map((o, i) => {
        const t = (frame + o.phase) / o.period;
        const floatY = Math.sin(t * 2 * Math.PI) * 16;
        const scale = 0.85 + Math.sin(t * 2 * Math.PI + 0.5) * 0.15;
        return (
          <div key={i} style={{
            position: "absolute",
            left: `${o.x}%`,
            top: `${o.y}%`,
            width: o.r * 2,
            height: o.r * 2,
            borderRadius: "50%",
            background: o.color,
            transform: `translateY(${floatY}px) scale(${scale})`,
            filter: "blur(28px)",
            pointerEvents: "none",
          }} />
        );
      })}
    </>
  );
};

// ── Scene-specific ambient particles ────────────────────────────────────────
const SCENE_EMOJIS: Record<string, string[]> = {
  kitchen:  ["🔥", "💨", "☁️", "✨"],
  park:     ["🍃", "🌸", "🌺", "🍀"],
  school:   ["⭐", "📚", "💡", "✏️"],
  bedroom:  ["💫", "🌙", "⭐", "💤"],
  bathroom: ["💧", "🫧", "💦", "✨"],
  shop:     ["💰", "🛍️", "⭐", "✨"],
  street:   ["🍃", "💨", "✨", "⭐"],
  home:     ["❤️", "💫", "⭐", "✨"],
};

export const SceneParticles: React.FC<{ scene: string; beatStart: number }> = ({ scene, beatStart }) => {
  const frame = useCurrentFrame();
  const local = frame - beatStart;
  if (local < 0 || local > 75) return null;

  const emojis = SCENE_EMOJIS[scene] ?? SCENE_EMOJIS.home;
  const seed = beatStart;

  const items = Array.from({ length: 4 }, (_, i) => ({
    x: 8 + ((seed * 31 + i * 23) % 84),
    y: 12 + ((seed * 17 + i * 41) % 55),
    delay: beatStart + i * 6,
    emoji: emojis[(seed + i) % emojis.length],
    size: 22 + (i % 3) * 8,
  }));

  return <>{items.map((p, i) => <Particle key={i} {...p} />)}</>;
};

// ── Big emotion burst — always fires on each speaking beat ───────────────────
export const BigEmotionPop: React.FC<{ emotion: string; beatStart: number; side: "left" | "right" }> = ({
  emotion, beatStart, side
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const f = frame - beatStart;
  if (f < 0 || f > 35) return null;

  const emojiMap: Record<string, string> = {
    happy: "😄", angry: "😤", surprised: "😱", sad: "😢", neutral: "💬",
  };
  const emoji = emojiMap[emotion] ?? "💬";
  const sc = spring({ frame: f, fps, config: { damping: 10, stiffness: 260, mass: 0.5 } });
  const fadeOut = interpolate(f, [18, 35], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const opacity = Math.min(sc, fadeOut);
  const xPct = side === "left" ? 22 : 72;

  return (
    <div style={{
      position: "absolute",
      left: `${xPct}%`,
      top: "28%",
      fontSize: 56,
      transform: `scale(${sc * 1.1})`,
      opacity,
      pointerEvents: "none",
      userSelect: "none",
      filter: "drop-shadow(0 4px 8px rgba(0,0,0,0.4))",
    }}>{emoji}</div>
  );
};
