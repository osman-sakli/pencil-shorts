import React from "react";
import {
  AbsoluteFill,
  Audio,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
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

export const PencilShort: React.FC<{ manifest: Manifest }> = ({ manifest }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const beats = manifest.beats;
  let activeIdx = findActive(beats, frame);
  const speaking = activeIdx !== -1;
  if (activeIdx === -1) activeIdx = findLastEnded(beats, frame);

  const active = beats[activeIdx];
  const speakerDef = active ? manifest.characters[active.character] : undefined;
  const mouth: MouthShape = active && speaking ? mouthAt(active, t) : "X";
  const bob = Math.sin(frame * 0.6) * 1.0;
  const sceneLabel = active?.background ?? "notebook";

  let listenerBeat: Beat | undefined;
  for (let i = activeIdx - 1; i >= 0; i--) {
    if (beats[i].character !== active?.character) { listenerBeat = beats[i]; break; }
  }

  return (
    <AbsoluteFill style={{ backgroundColor: "#fcfaf2" }}>
      <Audio src={staticFile(manifest.audio)} />
      <SceneBg label={sceneLabel} />

      {listenerBeat && (
        <Character
          characterId={listenerBeat.character}
          mouth="X"
          position={listenerBeat.position}
          speaking={false}
          bob={0}
          scale={manifest.characters[listenerBeat.character]?.scale}
        />
      )}

      {active && (
        <Character
          characterId={active.character}
          mouth={mouth}
          position={active.position}
          speaking={speaking}
          bob={bob}
          scale={speakerDef?.scale}
        />
      )}

      {speaking && active && speakerDef && (
        <Subtitles text={active.text} words={active.words} t={t} color={speakerDef.color} />
      )}
    </AbsoluteFill>
  );
};
