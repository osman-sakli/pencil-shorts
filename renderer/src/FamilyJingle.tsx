import React from "react";
import {
  AbsoluteFill, Audio, Img, staticFile, useCurrentFrame, useVideoConfig, interpolate,
} from "remotion";

export interface FamilyJingleData {
  audio: string;
  title: string;
  totalDurationFrames: number;
  fps: number;
  width: number;
  height: number;
}

export const EMPTY_FAMILY_JINGLE: FamilyJingleData = {
  audio: "", title: "THE PEN FAMILY",
  totalDurationFrames: 1, fps: 30, width: 1920, height: 1080,
};

// Boy sırası + gerçek boy oranları (referans sayfası: cm) — kalem-ucu ayak dahil
const FAMILY = [
  { id: "oz",   emo: "happy", cm: 18.5, color: "#3f6fc4" },
  { id: "mas",  emo: "happy", cm: 17.0, color: "#ff6faa" },
  { id: "bas",  emo: "happy", cm: 15.0, color: "#22b3b3" },
  { id: "saf",  emo: "happy", cm: 10.5, color: "#9b59d0" },
  { id: "sem",  emo: "happy", cm: 7.5,  color: "#4caf3f" },
  { id: "mira", emo: "happy", cm: 5.0,  color: "#ffcf3f" },
];
const MAX_CM = 18.5;

const Note: React.FC<{ x: number; delay: number; emoji: string }> = ({ x, delay, emoji }) => {
  const frame = useCurrentFrame();
  const f = (frame + delay) % 90;
  const y = interpolate(f, [0, 90], [100, 15]);
  const op = interpolate(f, [0, 12, 70, 90], [0, 0.9, 0.9, 0]);
  const sway = Math.sin(f * 0.12) * 22;
  return (
    <div style={{
      position: "absolute", left: `${x}%`, top: `${y}%`,
      fontSize: 46, opacity: op, transform: `translateX(${sway}px)`,
    }}>{emoji}</div>
  );
};

export const FamilyJingle: React.FC<{ data: FamilyJingleData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps, height: vh } = useVideoConfig();
  const t = frame / fps;
  const MAX_H_PX = vh * 0.46; // en uzun karakter ekran yüksekliğinin %46'sı

  // Karakterler sırayla "pop" ederek girer (0.25sn arayla), sonra zıplar
  const popStart = 0.3;
  const titlePop = interpolate(t, [0, 0.6], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{
      background: "linear-gradient(180deg,#8ED8FF 0%,#B8E8FF 45%,#7CC96A 62%,#5CB84A 100%)",
      overflow: "hidden",
    }}>
      {data.audio ? <Audio src={staticFile(data.audio)} /> : null}

      {/* güneş */}
      <div style={{
        position: "absolute", top: "8%", left: "8%", width: 130, height: 130,
        borderRadius: "50%", background: "radial-gradient(circle,#FFF3A0,#FFD84A)",
        boxShadow: "0 0 60px #FFD84A", filter: "blur(1px)",
      }} />
      {/* bulutlar */}
      {[{x:60,y:12,s:1},{x:80,y:20,s:0.7},{x:35,y:8,s:0.8}].map((c,i)=>(
        <div key={i} style={{
          position:"absolute", left:`${c.x}%`, top:`${c.y}%`, width:180*c.s, height:60*c.s,
          background:"#fff", borderRadius:40, opacity:0.9,
          transform:`translateX(${Math.sin((frame+i*40)*0.01)*30}px)`,
        }} />
      ))}

      {/* uçuşan müzik notaları */}
      {["🎵","🎶","⭐","🎵","🎶","⭐","🎵"].map((e,i)=>(
        <Note key={i} x={8+i*13} delay={i*22} emoji={e} />
      ))}

      {/* Başlık */}
      <div style={{
        position: "absolute", top: "6%", left: 0, right: 0, textAlign: "center",
        fontFamily: "Arial Black, Impact, sans-serif", fontWeight: 900, fontSize: 92,
        color: "#fff", transform: `scale(${0.6 + titlePop * 0.4})`, opacity: titlePop,
        letterSpacing: 2,
        textShadow: "0 0 30px #FFD84A, 5px 5px 0 #E8408A, -2px -2px 0 #3f6fc4",
        WebkitTextStroke: "3px #2a2a4e", paintOrder: "stroke fill",
      }}>{data.title}</div>

      {/* AİLE — 6 karakter boy sırasıyla, zıplayarak */}
      <div style={{
        position: "absolute", bottom: "6%", left: 0, right: 0,
        display: "flex", alignItems: "flex-end", justifyContent: "center", gap: 0,
      }}>
        {FAMILY.map((c, i) => {
          const appear = interpolate(t, [popStart + i * 0.22, popStart + i * 0.22 + 0.4],
            [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          const bounce = appear > 0.9 ? Math.abs(Math.sin((frame * 0.14) + i * 0.9)) * 26 : 0;
          const hpx = (c.cm / MAX_CM) * MAX_H_PX; // piksel yükseklik (boy oranıyla)
          return (
            <div key={c.id} style={{
              height: `${hpx}px`, transform: `translateY(${-bounce}px) scale(${appear})`,
              transformOrigin: "bottom center", position: "relative",
              marginLeft: i === 0 ? 0 : "-2.2%",  // kare padding'ini kapat
              filter: "drop-shadow(0 12px 18px rgba(0,0,0,0.28))",
            }}>
              <Img src={staticFile(`characters/sprites/${c.id}_${c.emo}.png`)}
                   style={{ height: "100%", width: "auto", objectFit: "contain" }} />
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
