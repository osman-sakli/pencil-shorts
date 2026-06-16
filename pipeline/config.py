"""Central configuration: paths, env, character registry."""
from __future__ import annotations
import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)

# Video format
FPS = 30
WIDTH = 1080
HEIGHT = 1920
BEAT_GAP_S = 0.35      # silence inserted between beats for pacing
TAIL_PAD_S = 0.8       # trailing padding after last beat

# Binaries
FFMPEG = os.getenv("FFMPEG_BIN", "ffmpeg")
RHUBARB = os.getenv("RHUBARB_BIN", "rhubarb")
RHUBARB_RECOGNIZER = os.getenv("RHUBARB_RECOGNIZER", "phonetic")

# LLM
LLM_MODEL = os.getenv("LLM_MODEL", "claude-haiku-4-5-20251001")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# TTS
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "edge")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")


def load_registry() -> dict:
    with open(ROOT / "characters.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


REGISTRY = load_registry()
CHARACTERS = REGISTRY["characters"]
BACKGROUNDS = REGISTRY["backgrounds"]
