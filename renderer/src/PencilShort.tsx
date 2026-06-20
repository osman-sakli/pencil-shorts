import React, { useMemo } from "react";
import { AbsoluteFill, Audio, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Manifest, MouthShape, Beat, Position } from "./types";
import { CharacterSprite } from "./CharacterSprite";
import { Subtitles } from "./Subtitles";
import { SceneBg } from "./backgrounds";
import { EndCard } from "./EndCard";

const END_CARD_FRAMES = 90; // 3 seconds

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
  const speakerId = beats[activeIdx]?.character;
  for (let i = activeIdx - 1; i >= 0; i--) {
    if (beats[i].character !== speakerId) return beats[i];
  }
  for (let i = activeIdx + 1; i < beats.length; i++) {
    if (beats[i].character !== speakerId) return beats[i];
  }
  return undefined;
}

export const PencilShort: React.FC<{ manifest: Manifest }> = ({ manifest }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const contentFrames = manifest.totalDurationFrames;
  const showEndCard = frame >= contentFrames;

  // Precompute first-appearance frame per character for spring entrance
  const entryFrames = useMemo(() => {
    const map: Record<string, number> = {};
    for (const beat of manifest.beats) {
      if (!(beat.character in map)) map[beat.character] = beat.startFrame;
    }
    return map;
  }, [manifest.beats]);

  if (showEndCard) {
    return <EndCard />;
  }

  const beats = manifest.beats;
  let activeIdx = findActive(beats, frame);
  const speaking = activeIdx !== -1;
  if (activeIdx === -1) activeIdx = findLastEnded(beats, frame);
  if (activeIdx === -1) return null;

  const active = beats[activeIdx];
  const speakerDef = active ? manifest.characters[active.character] : undefined;
  const mouth: MouthShape = active && speaking ? mouthAt(active, t) : "X";
  const sceneLabel = active?.background ?? "home";
  const listenerBeat = findListener(beats, activeIdx);

  const speakerPos = active?.position ?? "left";
  const listenerPos: Position = listenerBeat
    ? listenerBeat.position === speakerPos
      ? speakerPos === "left" ? "right" : "left"
      : listenerBeat.position
    : "right";

  return (
    <AbsoluteFill style={{ backgroundColor: "#111" }}>
      <Audio src={staticFile(manifest.audio)} />
      <SceneBg label={sceneLabel} />

      {listenerBeat && (
        <CharacterSprite
          characterId={listenerBeat.character}
          position={listenerPos}
          speaking={false}
          mouth="X"
          scale={manifest.characters[listenerBeat.character]?.scale ?? 1}
          emotion="neutral"
          entryFrame={entryFrames[listenerBeat.character] ?? 0}
        />
      )}

      {active && (
        <CharacterSprite
          characterId={active.character}
          position={active.position}
          speaking={speaking}
          mouth={mouth}
          scale={speakerDef?.scale ?? 1}
          emotion={(active as any).emotion ?? "neutral"}
          entryFrame={entryFrames[active.character] ?? 0}
        />
      )}

      {speaking && active && speakerDef && (
        <Subtitles
          text={active.text}
          words={active.words}
          t={t}
          color={speakerDef.color}
          speakerName={speakerDef.name}
        />
      )}
    </AbsoluteFill>
  );
};
