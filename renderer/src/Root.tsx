import React from "react";
import { Composition } from "remotion";
import { PencilShort } from "./PencilShort";
import { Manifest, EMPTY_MANIFEST } from "./types";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="PencilShort"
      component={PencilShort}
      defaultProps={{ manifest: EMPTY_MANIFEST }}
      // Pull duration/dimensions/fps from the manifest passed via --props.
      calculateMetadata={({ props }) => {
        const m = props.manifest as Manifest;
        return {
          durationInFrames: Math.max(1, m.totalDurationFrames) + 90, // +3s end card
          fps: m.fps,
          width: m.width,
          height: m.height,
        };
      }}
    />
  );
};
