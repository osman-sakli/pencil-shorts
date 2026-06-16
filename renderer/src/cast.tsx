import React from "react";
import { MouthShape } from "./types";
import { Mouth } from "./mouths";

// Each character is fully code-drawn (no image assets). viewBox 0 0 160 320.
// The mouth is placed at the character's anchor and swapped per Rhubarb cue.

type Props = { shape: MouthShape };

const Eye: React.FC<{ cx: number; cy: number; r?: number }> = ({ cx, cy, r = 13 }) => (
  <>
    <circle cx={cx} cy={cy} r={r} fill="#fff" />
    <circle cx={cx + 2} cy={cy + 2} r={r * 0.58} fill="#2b2b33" />
    <circle cx={cx - 1} cy={cy - 1} r={r * 0.2} fill="#fff" />
  </>
);

const Kursun: React.FC<Props> = ({ shape }) => (
  <svg viewBox="0 0 160 320" width="100%">
    <polygon points="38,118 122,118 104,84 56,84" fill="#f0bd86" />
    <polygon points="56,84 104,84 80,56" fill="#4a4a55" />
    <rect x="34" y="118" width="92" height="150" rx="34" fill="#ffd76b" />
    <rect x="34" y="262" width="92" height="22" rx="11" fill="#ef93ad" />
    <circle cx="20" cy="210" r="10" fill="#ffd76b" />
    <circle cx="140" cy="210" r="10" fill="#ffd76b" />
    <Eye cx={60} cy={172} />
    <Eye cx={100} cy={172} />
    <ellipse cx="46" cy="190" rx="7" ry="4.5" fill="#ff9bb0" opacity="0.7" />
    <ellipse cx="114" cy="190" rx="7" ry="4.5" fill="#ff9bb0" opacity="0.7" />
    <g transform="translate(80,196)"><Mouth shape={shape} /></g>
  </svg>
);

const Silgi: React.FC<Props> = ({ shape }) => (
  <svg viewBox="0 0 160 320" width="100%">
    <rect x="28" y="150" width="104" height="118" rx="26" fill="#ef93ad" />
    <path d="M28 176 q52 -22 104 0 v-9 q-52 -20 -104 0 z" fill="#d8728f" opacity="0.55" />
    <circle cx="16" cy="214" r="9" fill="#ef93ad" />
    <circle cx="144" cy="214" r="9" fill="#ef93ad" />
    <Eye cx={62} cy={196} />
    <Eye cx={98} cy={196} />
    <ellipse cx="48" cy="214" rx="7" ry="4.5" fill="#fff" opacity="0.4" />
    <ellipse cx="112" cy="214" rx="7" ry="4.5" fill="#fff" opacity="0.4" />
    <g transform="translate(80,220)"><Mouth shape={shape} /></g>
  </svg>
);

const Tukenmez: React.FC<Props> = ({ shape }) => (
  <svg viewBox="0 0 160 320" width="100%">
    <polygon points="66,272 94,272 80,300" fill="#c9d2dd" />
    <rect x="60" y="120" width="40" height="152" rx="16" fill="#3b7dd8" />
    <rect x="62" y="92" width="36" height="34" rx="12" fill="#2c63ad" />
    <rect x="96" y="98" width="7" height="40" rx="3" fill="#cfd8e6" />
    <circle cx="40" cy="178" r="9" fill="#3b7dd8" />
    <circle cx="120" cy="178" r="9" fill="#3b7dd8" />
    <Eye cx={71} cy={160} r={11} />
    <Eye cx={89} cy={160} r={11} />
    <ellipse cx="60" cy="176" rx="6" ry="4" fill="#9bc2ff" opacity="0.7" />
    <ellipse cx="100" cy="176" rx="6" ry="4" fill="#9bc2ff" opacity="0.7" />
    <g transform="translate(80,182)"><Mouth shape={shape} /></g>
  </svg>
);

const Kalemtras: React.FC<Props> = ({ shape }) => (
  <svg viewBox="0 0 160 320" width="100%">
    <rect x="40" y="172" width="80" height="92" rx="18" fill="#34c0b0" />
    <rect x="54" y="196" width="52" height="9" rx="4" fill="#1f2630" />
    <rect x="58" y="198" width="30" height="5" rx="2" fill="#cfd3da" />
    <circle cx="28" cy="214" r="8" fill="#34c0b0" />
    <circle cx="132" cy="214" r="8" fill="#34c0b0" />
    <Eye cx={63} cy={222} r={12} />
    <Eye cx={97} cy={222} r={12} />
    <ellipse cx="49" cy="240" rx="6" ry="4" fill="#8fe6db" opacity="0.8" />
    <ellipse cx="111" cy="240" rx="6" ry="4" fill="#8fe6db" opacity="0.8" />
    <g transform="translate(80,244)"><Mouth shape={shape} /></g>
  </svg>
);

export const CAST: Record<string, React.FC<Props>> = {
  kursun: Kursun,
  silgi: Silgi,
  tukenmez: Tukenmez,
  kalemtras: Kalemtras,
};
