import React from "react";
import { AbsoluteFill, Audio, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Manifest, MouthShape, Beat } from "./types";
import { Character } from "./Character";
import { Subtitles } from "./Subtitles";
import { SceneBg } from "./backgrounds";

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

// Find the most recent OTHER-character beat (listener)
function findListener(beats: Beat[], activeIdx: number): Beat | undefined {
  const speakerId = beats[activeIdx]?.character;
  for (let i = activeIdx - 1; i >= 0; i--) {
    if (beats[i].character !== speakerId) return beats[i];
  }
  // fallback: look ahead
  for (let i = activeIdx + 1; i < beats.length; i++) {
    if (beats[i].character !== speakerId) return beats[i];
  }
  return undefined;
}

export const PencilShort: React.FC<{ manifest: Manifest }> = ({ manifest }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

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

  return (
    <AbsoluteFill style={{ backgroundColor: "#fcfaf2" }}>
      <Audio src={staticFile(manifest.audio)} />
      <SceneBg label={sceneLabel} />

      {/* Listener — dimmed, opposite side */}
      {listenerBeat && (
        <Character
          characterId={listenerBeat.character}
          mouth="X"
          position={listenerBeat.position}
          speaking={false}
          scale={manifest.characters[listenerBeat.character]?.scale ?? 1}
          emotion="neutral"
        />
      )}

      {/* Active speaker */}
      {active && (
        <Character
          characterId={active.character}
          mouth={mouth}
          position={active.position}
          speaking={speaking}
          scale={speakerDef?.scale ?? 1}
          emotion={active.emotion ?? "neutral"}
        />
      )}

      {/* Subtitles — anchored to bottom, never overlaps characters */}
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
