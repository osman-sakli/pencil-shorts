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

const END_CARD_FRAMES = 90;

// ── Background-layer walking characters ─────────────────────────────────────
const WALKERS = [
  { char: "saf",     pxPerFrame: 0.38, yPct: 63, widthPct: 0.09, phaseOffset: 0,   flip: false },
  { char: "sem",     pxPerFrame: 0.24, yPct: 68, widthPct: 0.08, phaseOffset: 550,  flip: true  },
  { char: "mira",    pxPerFrame: 0.18, yPct: 72, widthPct: 0.07, phaseOffset: 300,  flip: false },
  { char: "biscuit", pxPerFrame: 0.55, yPct: 74, widthPct: 0.07, phaseOffset: 150,  flip: false },
  { char: "mittens", pxPerFrame: 0.14, yPct: 70, widthPct: 0.06, phaseOffset: 700,  flip: true  },
];

const WalkingBgChars: React.FC = () => {
  const frame = useCurrentFrame();
  const { width } = useVideoConfig();
  return (
    <>
      {WALKERS.map((w, i) => {
        const cw = width * w.widthPct;
        const span = width + cw * 2;
        const rawPos = (frame * w.pxPerFrame + w.phaseOffset) % span;
        const x = w.flip ? (span - rawPos - cw) : (rawPos - cw);
        const bob = Math.sin(frame * 0.28 + i * 1.6) * 5;
        return (
          <div key={i} style={{
            position: "absolute", left: x, top: `${w.yPct}%`, width: cw,
            opacity: 0.20, transform: `translateY(${bob}px)${w.flip ? " scaleX(-1)" : ""}`,
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
function findActive(beats: Beat[], frame: number): number {
  return beats.findIndex((b) => frame >= b.startFrame && frame < b.endFrame);
}
function findLastEnded(beats: Beat[], frame: number): number {
  let idx = -1;
  beats.forEach((b, i) => { if (b.endFrame <= frame) idx = i; });
  return idx;
}
function findListener(beats: Beat[], activeIdx: number): Beat | undefined {
  const sid = beats[activeIdx]?.character;
  for (let i = activeIdx - 1; i >= 0; i--) {
    if (beats[i].character !== sid) return beats[i];
  }
  for (let i = activeIdx + 1; i < beats.length; i++) {
    if (beats[i].character !== sid) return beats[i];
  }
  return undefined;
}

// ── Main component ───────────────────────────────────────────────────────────
export const PencilShort: React.FC<{ manifest: Manifest }> = ({ manifest }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const showEndCard = frame >= manifest.totalDurationFrames;

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
  const speakerDef = active ? manifest.characters[active.character] : undefined;
  const mouth: MouthShape = active && speaking ? mouthAt(active, t) : "X";
  const currentScene = (active as any)?.background ?? "home";
  const listenerBeat = findListener(beats, activeIdx);

  const prevBeat = activeIdx > 0 ? beats[activeIdx - 1] : null;
  const prevScene = (prevBeat as any)?.background ?? currentScene;
  const sceneChanged = prevBeat !== null && prevScene !== currentScene;

  const speakerPos = active?.position ?? "left";
  const listenerPos: Position = listenerBeat
    ? listenerBeat.position === speakerPos
      ? speakerPos === "left" ? "right" : "left"
      : listenerBeat.position
    : "right";

  const speakerEmotion = (active as any)?.emotion ?? "neutral";
  const listenerEmotion = (listenerBeat as any)?.emotion ?? "neutral";
  const listenerDef = listenerBeat ? manifest.characters[listenerBeat.character] : undefined;

  return (
    <AbsoluteFill style={{ backgroundColor: "#111" }}>
      <Audio src={staticFile(manifest.audio)} />

      {/* Beat-synced background — transitions smoothly per dialogue scene change */}
      <SceneTransitionBg
        currentScene={currentScene}
        prevScene={prevScene}
        beatStartFrame={active?.startFrame ?? 0}
      />

      {/* Ambient glow */}
      <ColorOrbs />

      {/* Walking background characters */}
      <WalkingBgChars />

      {/* Listener — static, dimmed, 65% scale (feels further away) */}
      {listenerBeat && (
        <CharacterSprite
          characterId={listenerBeat.character}
          position={listenerPos}
          speaking={false}
          mouth="X"
          scale={(listenerDef?.scale ?? 1) * 0.55}
          emotion={listenerEmotion}
          entryFrame={entryFrames[listenerBeat.character] ?? 0}
        />
      )}

      {/* Speaker — full size, animated, zooms in at each beat start */}
      {active && (
        <CharacterSprite
          characterId={active.character}
          position={speakerPos}
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
        <BigEmotionPop emotion={speakerEmotion} beatStart={active.startFrame} side={speakerPos === "left" ? "left" : "right"} />
      )}

      {active && speaking && (
        <EmotionBurst emotion={speakerEmotion} beatStart={active.startFrame} />
      )}

      {sceneChanged && active && <ScreenFlash beatStart={active.startFrame} />}
    </AbsoluteFill>
  );
};
