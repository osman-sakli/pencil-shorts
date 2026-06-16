export type MouthShape = "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H" | "X";

export interface MouthCue {
  start: number; // seconds, global timeline
  end: number;
  value: MouthShape;
}

export interface Word {
  word: string;
  start: number;
  end: number;
}

export type Position = "left" | "right" | "center";

export interface Beat {
  character: string; // cast id (kursun, silgi, ...)
  text: string;
  emotion: string;
  position: Position;
  background: string; // scene label (notebook, desk, pencilcase)
  startFrame: number;
  endFrame: number;
  mouthCues: MouthCue[];
  words: Word[];
}

// Characters are code-drawn (see cast.tsx); the manifest only carries metadata.
export interface CharacterDef {
  name: string;
  color: string; // used for subtitle highlight
  scale?: number;
}

export interface Manifest {
  title: string;
  fps: number;
  width: number;
  height: number;
  audio: string;
  background: string;
  totalDurationFrames: number;
  characters: Record<string, CharacterDef>;
  beats: Beat[];
  description: string;
  hashtags: string[];
}

export const EMPTY_MANIFEST: Manifest = {
  title: "",
  fps: 30,
  width: 1080,
  height: 1920,
  audio: "out/audio_full.wav",
  background: "assets/backgrounds/desk.png",
  totalDurationFrames: 1,
  characters: {},
  beats: [],
  description: "",
  hashtags: [],
};
