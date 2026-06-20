"""Download a random kids-friendly background music track from Pixabay.

Requires PIXABAY_API_KEY in environment (free at pixabay.com).
Caches to /tmp/pencil_music/ so we don't re-download on every run.
Returns path to mp3, or None if unavailable.
"""
from __future__ import annotations
import hashlib
import json
import os
import random
import tempfile
import urllib.request
import urllib.parse
from pathlib import Path

CACHE_DIR = Path(tempfile.gettempdir()) / "pencil_music"
CACHE_DIR.mkdir(exist_ok=True)

QUERIES = ["happy children", "kids funny", "cartoon playful", "children upbeat"]


def _get_api_key() -> str:
    key = os.getenv("PIXABAY_API_KEY", "")
    if key:
        return key
    try:
        import boto3
        ssm = boto3.client("ssm", region_name="us-east-1")
        resp = ssm.get_parameter(Name="/pencil-shorts/pixabay_api_key", WithDecryption=True)
        return resp["Parameter"]["Value"]
    except Exception:
        return ""


def _pixabay_music(api_key: str, query: str) -> list[dict]:
    params = urllib.parse.urlencode({
        "key": api_key,
        "q": query,
        "per_page": 20,
    })
    url = f"https://pixabay.com/api/music/?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "PencilShorts/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())["hits"]


def get_music_path() -> Path | None:
    api_key = _get_api_key()
    if not api_key:
        return None

    try:
        query = random.choice(QUERIES)
        tracks = _pixabay_music(api_key, query)
        if not tracks:
            return None

        track = random.choice(tracks[:10])
        audio_url = track.get("audio", "")
        if not audio_url:
            return None

        # cache key = url hash
        cache_key = hashlib.md5(audio_url.encode()).hexdigest()[:12]
        cached = CACHE_DIR / f"{cache_key}.mp3"
        if cached.exists() and cached.stat().st_size > 10_000:
            return cached

        req = urllib.request.Request(audio_url, headers={"User-Agent": "PencilShorts/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            cached.write_bytes(r.read())
        return cached if cached.stat().st_size > 10_000 else None

    except Exception as e:
        print(f"[music] skip (fetch failed): {e}")
        return None
