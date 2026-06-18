import React from "react";
import { Word } from "./types";

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
        return (
          <span key={i} style={{
            color: active ? color : "#fff",
            margin: "0 4px",
            textShadow: active ? `0 0 14px ${color}88` : "none",
          }}>
            {w.word}
          </span>
        );
      })
    ) : (
      text
    );

  return (
    // Fixed bar at the VERY BOTTOM — never overlaps characters
    <div style={{
      position: "absolute",
      bottom: 0,
      left: 0,
      right: 0,
      paddingBottom: 36,
      paddingTop: 20,
      paddingLeft: 32,
      paddingRight: 32,
      background: "linear-gradient(transparent, rgba(0,0,0,0.72) 28%)",
    }}>
      {/* Speaker chip */}
      <div style={{
        display: "inline-block",
        backgroundColor: color,
        color: "#fff",
        fontFamily: "Arial Black, Impact, sans-serif",
        fontWeight: 900,
        fontSize: 34,
        borderRadius: 24,
        padding: "4px 22px",
        marginBottom: 10,
        letterSpacing: 1,
        boxShadow: "0 2px 8px rgba(0,0,0,0.35)",
      }}>
        {speakerName}
      </div>

      {/* Dialogue */}
      <div style={{
        fontFamily: "Arial Black, Impact, sans-serif",
        fontWeight: 900,
        fontSize: 56,
        lineHeight: 1.2,
        color: "#fff",
        WebkitTextStroke: "5px #000",
        paintOrder: "stroke fill",
        textAlign: "center",
      }}>
        {content}
      </div>
    </div>
  );
};
