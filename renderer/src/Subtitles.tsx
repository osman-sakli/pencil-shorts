import React from "react";
import { interpolate, spring, useVideoConfig } from "remotion";
import { Word } from "./types";

const ActiveWord: React.FC<{ word: string; color: string }> = ({ word, color }) => {
  const { fps } = useVideoConfig();
  const scale = spring({ fps, frame: 0, config: { damping: 10, stiffness: 280 } });
  return (
    <span style={{
      color,
      display: "inline-block",
      transform: `scale(${interpolate(scale, [0, 1], [1.0, 1.18])})`,
      transformOrigin: "center bottom",
      textShadow: `0 0 20px ${color}, 0 0 40px ${color}88`,
      WebkitTextStroke: "4px #000",
      paintOrder: "stroke fill",
      margin: "0 5px",
      transition: "color 0.05s",
    }}>
      {word}
    </span>
  );
};

export const Subtitles: React.FC<{
  text: string;
  words: Word[];
  t: number;
  color: string;
  speakerName: string;
}> = ({ text, words, t, color, speakerName }) => {
  const content =
    words.length > 0 ? (
      words.map((w, i) => {
        const active = t >= w.start && t < w.end;
        return active
          ? <ActiveWord key={i} word={w.word} color={color} />
          : (
            <span key={i} style={{
              color: "#FFFFFF",
              WebkitTextStroke: "4px #000",
              paintOrder: "stroke fill",
              margin: "0 5px",
            }}>
              {w.word}
            </span>
          );
      })
    ) : (
      <span style={{ WebkitTextStroke: "4px #000", paintOrder: "stroke fill" }}>{text}</span>
    );

  return (
    <div style={{
      position: "absolute",
      bottom: 0,
      left: 0,
      right: 0,
      paddingBottom: 44,
      paddingTop: 28,
      paddingLeft: 28,
      paddingRight: 28,
      background: "linear-gradient(transparent, rgba(0,0,0,0.80) 32%)",
    }}>
      {/* Speaker chip */}
      <div style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 8,
        backgroundColor: color,
        color: "#fff",
        fontFamily: "Arial Black, Impact, sans-serif",
        fontWeight: 900,
        fontSize: 24,
        borderRadius: 999,
        padding: "4px 18px",
        marginBottom: 8,
        letterSpacing: 1,
        boxShadow: `0 4px 16px ${color}88, 0 2px 4px rgba(0,0,0,0.4)`,
        WebkitTextStroke: "1px rgba(0,0,0,0.3)",
      }}>
        {speakerName}
      </div>

      {/* Dialogue */}
      <div style={{
        fontFamily: "Arial Black, Impact, sans-serif",
        fontWeight: 900,
        fontSize: 42,
        lineHeight: 1.25,
        color: "#fff",
        textAlign: "center",
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        alignItems: "baseline",
        gap: 0,
      }}>
        {content}
      </div>
    </div>
  );
};
