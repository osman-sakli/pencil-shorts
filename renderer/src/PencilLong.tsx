/**
 * PencilLong — landscape (1920×1080) renderer for long-form episodes.
 * Differences from PencilShort:
 *  - Horizontal layout: characters spread across width
 *  - Up to 3 visible characters (speaker + 2 listeners)
 *  - Background cycles every 4s matching scene dialogue
 *  - More effects real estate
 *  - Subtitle bar at bottom with name chip
 */
import React, { useMemo } from "react";
import { AbsoluteFill, Audio, Img, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Manifest, MouthShape, Beat, Position } from "./types";
import { CharacterSprite } from "./CharacterSprite";
import { Subtitles } from "./Subtitles";
import { SceneTransitionBg } from "./backgrounds";
import { EndCard } from "./EndCard";
import {
  EmotionBurst, ScreenFlash, FloatingStars, ColorOrbs,
  SceneParticles, BigEmotionPop,
} from "./effects";

const END_CARD_FRAMES = 150; // 5s end card for long episodes

// Landscape positions: spread across the width
const LANDSCAPE_POS: Record<Position, React.CSSProperties> = {
  left:   { left: "6%" },
  center: { left: "50%", transform: "translateX(-50%)" },
  right:  { right: "6%", transform: "scaleX(-1)" },
};

// Assign positions for up to 3 visible characters in landscape
function assignPositions(
  speakerId: string,
  listenerId: string | undefined,
  prevListenerId: string | undefined,
): Record<string, Position> {
  const map: Record<string, Position> = {};
  map[speakerId] = "left";
  if (listenerId) map[listenerId] = "right";
  if (prevListenerId && prevListenerId !== speakerId && prevListenerId !== listenerId) {
    map[prevListenerId] = "center";
  }
  return map;
}

// ── Landscape walking background characters ──────────────────────────────────
const BG_WALKERS_LAND = [
  { char: "saf",  pxPerFrame: 0.30, yPct: 68, widthPct: 0.055, phaseOffset: 0,   flip: false },
  { char: "sem",  pxPerFrame: 0.20, yPct: 72, widthPct: 0.045, phaseOffset: 900,  flip: true  },
  { char: "mira", pxPerFrame: 0.15, yPct: 76, widthPct: 0.038, phaseOffset: 500,  flip: false },
];

const WalkingBgCharsLandscape: React.FC = () => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  return (
    <>
      {BG_WALKERS_LAND.map((w, i) => {
        const cw = width * w.widthPct;
        const span = width + cw * 2;
        const rawPos = (frame * w.pxPerFrame + w.phaseOffset) % span;
        const x = w.flip ? (span - rawPos - cw) : (rawPos - cw);
        const bob = Math.sin(frame * 0.25 + i * 1.4) * 4;
        return (
          <div key={i} style={{
            position: "absolute", left: x, top: `${w.yPct}%`, width: cw,
            opacity: 0.18, transform: `translateY(${bob}px)${w.flip ? " scaleX(-1)" : ""}`,
            pointerEvents: "none",
          }}>
            <Img src={staticFile(`characters/sprites/${w.char}_neutral.png`)}
                 style={{ width: "100%", height: "auto" }} />
          </div>
        );
      })}
    </>
  );
};

// ── Helpers ──────────────────────────────────────────────────────────────────
function mouthAt(beat: Beat, t: number): MouthShape {
  for (const c of beat.mouthCues) if (t >= c.start && t < c.end) return c.value;
  return "X";
}
function findActive(beats: Beat[], frame: number) {
  return beats.findIndex((b) => frame >= b.startFrame && frame < b.endFrame);
}
function findLastEnded(beats: Beat[], frame: number) {
  let idx = -1;
  beats.forEach((b, i) => { if (b.endFrame <= frame) idx = i; });
  return idx;
}

// ── Main component ────────────────────────────────────────────────────────────
export const PencilLong: React.FC<{ manifest: Manifest }> = ({ manifest }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const showEndCard = frame >= manifest.totalDurationFrames;

  const bgLabels = useMemo(() => {
    const seen = new Set<string>();
    const labels: string[] = [];
    for (const beat of manifest.beats) {
      const bg = (beat as any).background ?? "home";
      if (!seen.has(bg)) { seen.add(bg); labels.push(bg); }
    }
    return labels;
  }, [manifest.beats]);

  const entryFrames = useMemo(() => {
    const map: Record<string, number> = {};
    for (const beat of manifest.beats) {
      if (!(beat.character in map)) map[beat.character] = beat.startFrame;
    }
    return map;
  }, [manifest.beats]);

  if (showEndCard) return <EndCard />;

  const beats = manifest.beats;
  let activeIdx = findActive(beats, frame);
  const speaking = activeIdx !== -1;
  if (activeIdx === -1) activeIdx = findLastEnded(beats, frame);
  if (activeIdx === -1) return null;

  const active = beats[activeIdx];
  const speakerDef = manifest.characters[active.character];
  const mouth: MouthShape = active && speaking ? mouthAt(active, t) : "X";
  const currentScene = (active as any).background ?? "home";
  const prevBeatItem = activeIdx > 0 ? beats[activeIdx - 1] : null;
  const prevScene = (prevBeatItem as any)?.background ?? currentScene;

  // Find the most recent OTHER character for listener role
  const listenerId = (() => {
    for (let i = activeIdx - 1; i >= 0; i--) {
      if (beats[i].character !== active.character) return beats[i].character;
    }
    for (let i = activeIdx + 1; i < beats.length; i++) {
      if (beats[i].character !== active.character) return beats[i].character;
    }
    return undefined;
  })();

  // Find a second listener (third character for richer scenes)
  const secondListenerId = (() => {
    if (!listenerId) return undefined;
    for (let i = activeIdx - 1; i >= 0; i--) {
      const c = beats[i].character;
      if (c !== active.character && c !== listenerId) return c;
    }
    return undefined;
  })();

  const listenerBeat = listenerId
    ? beats.slice(0, activeIdx).reverse().find(b => b.character === listenerId) ??
      beats.find(b => b.character === listenerId)
    : undefined;

  const secondListenerBeat = secondListenerId
    ? beats.slice(0, activeIdx).reverse().find(b => b.character === secondListenerId)
    : undefined;

  const sceneChanged = prevBeatItem !== null && prevScene !== currentScene;

  const speakerEmotion = (active as any).emotion ?? "neutral";
  const listenerEmotion = (listenerBeat as any)?.emotion ?? "neutral";
  const secondListenerEmotion = (secondListenerBeat as any)?.emotion ?? "neutral";

  return (
    <AbsoluteFill style={{ backgroundColor: "#111" }}>
      <Audio src={staticFile(manifest.audio)} />

      {/* Per-beat background — transitions with each scene change */}
      <SceneTransitionBg
        currentScene={currentScene}
        prevScene={prevScene}
        beatStartFrame={active?.startFrame ?? 0}
      />

      {/* Ambient glow */}
      <ColorOrbs />

      {/* Walking background characters */}
      <WalkingBgCharsLandscape />

      {/* Second listener (center, very dim) */}
      {secondListenerBeat && (
        <CharacterSprite
          characterId={secondListenerBeat.character}
          position="center"
          speaking={false}
          mouth="X"
          scale={(manifest.characters[secondListenerBeat.character]?.scale ?? 1) * 0.7}
          emotion={secondListenerEmotion}
          entryFrame={entryFrames[secondListenerBeat.character] ?? 0}
        />
      )}

      {/* Primary listener (right side) — static, dimmed, 60% scale */}
      {listenerBeat && (
        <CharacterSprite
          characterId={listenerBeat.character}
          position="right"
          speaking={false}
          mouth="X"
          scale={(manifest.characters[listenerBeat.character]?.scale ?? 1) * 0.60}
          emotion={listenerEmotion}
          entryFrame={entryFrames[listenerBeat.character] ?? 0}
        />
      )}

      {/* Active speaker (left side) — full size, zooms in at beat start */}
      {active && (
        <CharacterSprite
          characterId={active.character}
          position="left"
          speaking={speaking}
          mouth={mouth}
          scale={speakerDef?.scale ?? 1}
          emotion={speakerEmotion}
          entryFrame={entryFrames[active.character] ?? 0}
          beatStartFrame={active.startFrame}
        />
      )}

      {/* Subtitles */}
      {speaking && active && speakerDef && (
        <Subtitles
          text={active.text}
          words={active.words}
          t={t}
          color={speakerDef.color}
          speakerName={speakerDef.name}
        />
      )}

      {/* Effects */}
      <FloatingStars />

      {active && speaking && (
        <SceneParticles scene={currentScene} beatStart={active.startFrame} />
      )}

      {active && speaking && speakerEmotion !== "neutral" && (
        <BigEmotionPop emotion={speakerEmotion} beatStart={active.startFrame} side="left" />
      )}

      {active && speaking && (
        <EmotionBurst emotion={speakerEmotion} beatStart={active.startFrame} />
      )}

      {sceneChanged && active && <ScreenFlash beatStart={active.startFrame} />}
    </AbsoluteFill>
  );
};
