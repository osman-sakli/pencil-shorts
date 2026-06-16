import { Config } from "@remotion/cli/config";

Config.setVideoImageFormat("jpeg");
Config.setOverwriteOutput(true);
// Repo root as public dir so staticFile("out/...") and staticFile("assets/...") resolve.
// (render script also passes --public-dir=../ explicitly)
Config.setPublicDir("../");
