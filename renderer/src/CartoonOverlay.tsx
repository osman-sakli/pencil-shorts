import React from "react";
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Subtitles } from "./Subtitles";
import { EndCard } from "./EndCard";
import { Word } from "./types";

export interface MusicSegment {
  src: string;        // repo-kökünden yol, ör. assets/music/mystery.mp3
  startFrame: number;
  endFrame: number;
}

export interface OverlayBeat {
  startFrame: number;
  endFrame: number;
  text: string;
  words: Word[];
  name: string;
  color: string;
}

export interface OverlayData {
  videoSrc: string;
  title: string;
  totalDurationFrames: number;
  fps: number;
  width: number;
  height: number;
  beats: OverlayBeat[];
  /** Bölüm parçaları (Part 1/2…): kaynak videonun bu karesinden başla */
  startFrom?: number;
  /** Sahne ruh haline göre arka plan müziği segmentleri */
  music?: MusicSegment[];
}

export const EMPTY_OVERLAY: OverlayData = {
  videoSrc: "out/cartoon.mp4",
  title: "",
  totalDurationFrames: 1,
  fps: 30,
  width: 1080,
  height: 1920,
  beats: [],
};

const TITLE_FRAMES = 80;

const TitleCard: React.FC<{ title: string }> = ({ title }) => {
  const frame = useCurrentFrame();
  if (frame > TITLE_FRAMES) return null;
  const opacity = interpolate(frame, [0, 12, TITLE_FRAMES - 18, TITLE_FRAMES], [0, 1, 1, 0]);
  const slide = interpolate(frame, [0, 14], [40, 0], { extrapolateRight: "clamp" });
  return (
    <div style={{
      position: "absolute", top: "10%", left: 0, right: 0,
      display: "flex", justifyContent: "center", opacity,
      transform: `translateY(${slide}px)`,
    }}>
      <div style={{
        fontFamily: "Arial Black, Impact, sans-serif",
        fontWeight: 900, fontSize: 64, color: "#fff", textAlign: "center",
        WebkitTextStroke: "6px #000", paintOrder: "stroke fill",
        padding: "12px 36px", lineHeight: 1.2,
        textShadow: "0 8px 32px rgba(0,0,0,0.5)",
      }}>
        {title}
      </div>
    </div>
  );
};

export const CartoonOverlay: React.FC<{ data: OverlayData }> = ({ data }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  if (frame >= data.totalDurationFrames) return <EndCard />;

  const active = data.beats.find((b) => frame >= b.startFrame && frame < b.endFrame);

  const MUSIC_VOL = 0.13; // diyaloğun altında kalacak seviye

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* objectFit cover: 16:9 master 9:16 tuvale ortadan kırpılarak oturur */}
      <OffthreadVideo
        src={staticFile(data.videoSrc)}
        startFrom={data.startFrom ?? 0}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
      />

      {/* Sahne ruh haline göre müzik — fade in/out'lu segmentler */}
      {(data.music ?? []).map((m, i) => {
        const segDur = m.endFrame - m.startFrame;
        return (
          <Sequence key={i} from={m.startFrame} durationInFrames={segDur}>
            <Audio
              src={staticFile(m.src)}
              loop
              volume={(f) =>
                interpolate(f, [0, 20, segDur - 20, segDur],
                  [0, MUSIC_VOL, MUSIC_VOL, 0],
                  { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
              }
            />
          </Sequence>
        );
      })}

      <TitleCard title={data.title} />
      {active && (
        <Subtitles
          text={active.text}
          words={active.words}
          t={t}
          color={active.color}
          speakerName={active.name}
        />
      )}
    </AbsoluteFill>
  );
};
