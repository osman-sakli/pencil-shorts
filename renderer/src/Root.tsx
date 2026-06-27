import React from "react";
import { Composition } from "remotion";
import { PencilShort } from "./PencilShort";
import { PencilLong } from "./PencilLong";
import { Manifest, EMPTY_MANIFEST } from "./types";

const metaFromManifest = ({ props }: { props: { manifest: Manifest } }) => {
  const m = props.manifest;
  return {
    durationInFrames: Math.max(1, m.totalDurationFrames) + 150, // +5s end card
    fps: m.fps,
    width: m.width,
    height: m.height,
  };
};

const LANDSCAPE_MANIFEST: Manifest = {
  ...EMPTY_MANIFEST,
  width: 1920,
  height: 1080,
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="PencilShort"
        component={PencilShort}
        defaultProps={{ manifest: EMPTY_MANIFEST }}
        calculateMetadata={metaFromManifest}
      />
      <Composition
        id="PencilLong"
        component={PencilLong}
        defaultProps={{ manifest: LANDSCAPE_MANIFEST }}
        calculateMetadata={metaFromManifest}
      />
    </>
  );
};
