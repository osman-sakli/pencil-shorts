import React from "react";
import { Word } from "./types";

export const Subtitles: React.FC<{
  text: string;
  words: Word[];
  t: number; // current time in seconds (global)
  color: string;
}> = ({ text, words, t, color }) => {
  // If we have word timings, render karaoke-style; else show full line.
  const content =
    words.length > 0 ? (
      <>
        {words.map((w, i) => {
          const active = t >= w.start && t < w.end;
          return (
            <span
              key={i}
              style={{
                color: active ? color : "white",
                margin: "0 6px",
                textShadow: active ? `0 0 18px ${color}` : "none",
              }}
            >
              {w.word}
            </span>
          );
        })}
      </>
    ) : (
      text
    );

  return (
    <div
      style={{
        position: "absolute",
        bottom: "16%",
        width: "84%",
        left: "8%",
        textAlign: "center",
        fontFamily: "Arial Black, Impact, sans-serif",
        fontWeight: 900,
        fontSize: 64,
        lineHeight: 1.15,
        color: "white",
        WebkitTextStroke: "6px black",
        paintOrder: "stroke fill",
      }}
    >
      {content}
    </div>
  );
};
