import React, { useMemo } from "react";
import {
  AbsoluteFill, Audio, Img, staticFile, useCurrentFrame, useVideoConfig,
  interpolate,
} from "remotion";

export interface NurseryWord { word: string; start: number; end: number; }
export interface NurseryData {
  audio: string;
  title: string;
  words: NurseryWord[];
  characterSprite: string;   // e.g. "characters/sprites/twinkle.png"
  totalDurationFrames: number;
  fps: number;
  width: number;
  height: number;
}

export const EMPTY_NURSERY: NurseryData = {
  audio: "", title: "", words: [], characterSprite: "characters/sprites/twinkle.png",
  totalDurationFrames: 1, fps: 30, width: 1080, height: 1920,
};

// Kelimeleri satırlara böl: 0.6sn'den büyük boşlukta ya da 6 kelimede yeni satır
function groupLines(words: NurseryWord[]): NurseryWord[][] {
  const lines: NurseryWord[][] = [];
  let cur: NurseryWord[] = [];
  for (let i = 0; i < words.length; i++) {
    const w = words[i];
    if (cur.length > 0) {
      const gap = w.start - cur[cur.length - 1].end;
      if (gap > 0.6 || cur.length >= 6) { lines.push(cur); cur = []; }
    }
    cur.push(w);
  }
  if (cur.length) lines.push(cur);
  return lines;
}

const StarField: React.FC = () => {
  const frame = useCurrentFrame();
  const stars = useMemo(() =>
    Array.from({ length: 60 }, (_, i) => ({
      x: (i * 97) % 100, y: (i * 53) % 70,
      size: 2 + (i % 4) * 2, period: 40 + (i % 5) * 18, phase: (i * 13) % 60,
    })), []);
  return (
    <>
      {stars.map((s, i) => {
        const t = (frame + s.phase) / s.period;
        const op = 0.3 + Math.abs(Math.sin(t * Math.PI)) * 0.7;
        return (
          <div key={i} style={{
            position: "absolute", left: `${s.x}%`, top: `${s.y}%`,
            width: s.size, height: s.size, borderRadius: "50%",
            background: "#FFF8D0", opacity: op,
            boxShadow: `0 0 ${s.size * 2}px #FFE88A`,
          }} />
        );
      })}
    </>
  );
};

export const NurseryMusic: React.FC<{ data: NurseryData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const lines = useMemo(() => groupLines(data.words), [data.words]);

  // Aktif satır: içinde bulunulan zamanı kapsayan satır
  let activeLineIdx = lines.findIndex(
    (ln) => t >= ln[0].start - 0.3 && t <= ln[ln.length - 1].end + 0.3);
  if (activeLineIdx === -1) {
    // en yakın gelecek/geçmiş satırı göster
    activeLineIdx = lines.findIndex((ln) => t < ln[0].start);
    if (activeLineIdx === -1) activeLineIdx = lines.length - 1;
  }
  const line = lines[activeLineIdx] ?? [];

  // Twinkle süzülme + parlama + hafif ritim nabzı
  const bob = Math.sin(frame * 0.05) * 24;
  const sway = Math.sin(frame * 0.03) * 12;
  const glowPulse = 0.6 + Math.abs(Math.sin(frame * 0.08)) * 0.4;
  const scalePulse = 1 + Math.sin(frame * 0.16) * 0.03;
  const titleOpacity = interpolate(t, [0, 1, 5, 6.5], [0, 1, 1, 0.25],
    { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{
      background: "linear-gradient(180deg,#0A0E2A 0%,#1A1550 45%,#2A1E6A 100%)",
    }}>
      {data.audio ? <Audio src={staticFile(data.audio)} /> : null}
      <StarField />

      {/* Ay */}
      <div style={{
        position: "absolute", top: "7%", right: "12%", width: 150, height: 150,
        borderRadius: "50%", background: "radial-gradient(circle at 40% 40%,#FFF8E0,#FFE9A8)",
        boxShadow: "0 0 60px #FFE9A8, 0 0 120px rgba(255,233,168,0.4)",
      }} />

      {/* Başlık */}
      <div style={{
        position: "absolute", top: "6%", left: 0, right: 0, textAlign: "center",
        fontFamily: "Arial Black, Impact, sans-serif", fontWeight: 900, fontSize: 64,
        color: "#FFE88A", opacity: titleOpacity,
        textShadow: "0 0 24px #FFC94A, 3px 3px 0 rgba(0,0,0,0.4)", padding: "0 40px",
      }}>
        {data.title}
      </div>

      {/* Twinkle — merkezde süzülüyor, parlıyor */}
      <div style={{
        position: "absolute", left: "50%", top: "34%",
        transform: `translate(-50%,-50%) translate(${sway}px,${bob}px) scale(${scalePulse})`,
        width: 460, height: 460,
        filter: `drop-shadow(0 0 ${40 * glowPulse}px rgba(255,220,90,${glowPulse}))`,
      }}>
        <Img src={staticFile(data.characterSprite)}
             style={{ width: "100%", height: "100%", objectFit: "contain" }} />
      </div>

      {/* Yükselen ışık parçacıkları */}
      {Array.from({ length: 10 }).map((_, i) => {
        const p = ((frame * 0.6 + i * 40) % 260) / 260;
        const x = 30 + ((i * 61) % 40);
        return (
          <div key={i} style={{
            position: "absolute", left: `${x}%`, top: `${60 - p * 40}%`,
            width: 10, height: 10, borderRadius: "50%", background: "#FFE88A",
            opacity: (1 - p) * 0.7, boxShadow: "0 0 12px #FFE88A",
          }} />
        );
      })}

      {/* Karaoke sözleri */}
      <div style={{
        position: "absolute", bottom: "12%", left: 0, right: 0, padding: "0 50px",
        display: "flex", flexWrap: "wrap", justifyContent: "center", alignItems: "center",
        gap: "0 18px",
      }}>
        {line.map((w, i) => {
          const active = t >= w.start && t <= w.end;
          const sung = t > w.end;
          return (
            <span key={i} style={{
              fontFamily: "Arial Black, Impact, sans-serif", fontWeight: 900,
              fontSize: 66, lineHeight: 1.3,
              color: active ? "#FFE23A" : sung ? "#FFFFFF" : "rgba(255,255,255,0.55)",
              transform: active ? "scale(1.18)" : "scale(1)",
              display: "inline-block", transition: "transform 0.08s",
              WebkitTextStroke: "5px #000", paintOrder: "stroke fill",
              textShadow: active ? "0 0 26px #FFC94A" : "none",
            }}>
              {w.word}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
