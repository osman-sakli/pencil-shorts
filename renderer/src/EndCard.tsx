import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";

export const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 18], [0, 1], { extrapolateRight: "clamp" });
  const rise = interpolate(frame, [0, 22], [40, 0], { extrapolateRight: "clamp" });

  const chars = [
    { c: "#3f6fc4", h: 130 }, { c: "#ff7fa0", h: 120 },
    { c: "#a06cd8", h: 110 }, { c: "#34bfb0", h: 100 },
    { c: "#4cae5a", h: 108 }, { c: "#ffcc4d", h: 88 },
  ];

  return (
    <AbsoluteFill style={{
      opacity,
      background: "linear-gradient(160deg, #0d1b4b 0%, #1a3a7c 40%, #0d1b4b 100%)",
      display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center",
    }}>
      {/* Stars */}
      {[10,25,38,55,70,82,90,15,45,65].map((x,i) => (
        <div key={i} style={{
          position: "absolute",
          left: `${x}%`, top: `${8 + (i*7) % 22}%`,
          width: i % 3 === 0 ? 6 : 4, height: i % 3 === 0 ? 6 : 4,
          borderRadius: "50%", background: "#fff",
          opacity: 0.4 + (i % 3) * 0.2,
        }} />
      ))}

      {/* "The" */}
      <div style={{
        transform: `translateY(${rise}px)`,
        color: "#c8d8ff",
        fontFamily: "Arial Black, Impact, sans-serif",
        fontWeight: 900, fontSize: 68,
        letterSpacing: 8, marginBottom: 0,
      }}>
        THE
      </div>

      {/* "Pen" */}
      <div style={{
        transform: `translateY(${rise}px)`,
        color: "#ffdd44",
        fontFamily: "Arial Black, Impact, sans-serif",
        fontWeight: 900, fontSize: 196,
        lineHeight: 0.88,
        WebkitTextStroke: "6px #cc8800",
        paintOrder: "stroke fill",
        textShadow: "0 8px 32px rgba(255,200,0,0.4)",
      }}>
        Pen
      </div>

      {/* "Family" */}
      <div style={{
        transform: `translateY(${rise}px)`,
        color: "#fff",
        fontFamily: "Arial Black, Impact, sans-serif",
        fontWeight: 900, fontSize: 112,
        letterSpacing: 10,
        WebkitTextStroke: "4px rgba(0,0,40,0.5)",
        paintOrder: "stroke fill",
      }}>
        FAMILY
      </div>

      {/* Glowing divider */}
      <div style={{
        width: 220, height: 4, background: "#ffdd44",
        borderRadius: 2, margin: "28px 0",
        boxShadow: "0 0 20px #ffdd44, 0 0 40px #ffaa00",
        opacity: interpolate(frame, [12, 28], [0, 1], { extrapolateRight: "clamp" }),
      }} />

      {/* "New episode tomorrow!" */}
      <div style={{
        opacity: interpolate(frame, [18, 32], [0, 1], { extrapolateRight: "clamp" }),
        color: "#ffe88a",
        fontFamily: "Arial Black, Impact, sans-serif",
        fontWeight: 700, fontSize: 48,
        textAlign: "center", padding: "0 60px",
        letterSpacing: 1,
      }}>
        New part every morning — 6 AM! ⏰
      </div>

      {/* Character silhouettes */}
      <div style={{
        display: "flex", gap: 18, marginTop: 56,
        alignItems: "flex-end",
        opacity: interpolate(frame, [20, 38], [0, 1], { extrapolateRight: "clamp" }),
        transform: `translateY(${interpolate(frame, [20, 38], [20, 0], { extrapolateRight: "clamp" })}px)`,
      }}>
        {chars.map(({ c, h }, i) => (
          <div key={i} style={{
            width: 46, height: h,
            background: `linear-gradient(180deg, ${c} 0%, ${c}cc 100%)`,
            borderRadius: "14px 14px 6px 6px",
            boxShadow: `0 4px 20px ${c}66`,
            border: `2px solid ${c}`,
          }} />
        ))}
      </div>
    </AbsoluteFill>
  );
};
