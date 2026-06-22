"""End-to-end orchestrator: script -> voice -> lipsync -> manifest -> render -> publish.

Usage:
  python pipeline/run.py --topic "The pencil is jealous of the eraser"
  python pipeline/run.py --auto
  python pipeline/run.py --topic "..." --no-render   # skip Remotion
  python pipeline/run.py --auto --no-publish         # skip upload
"""
from __future__ import annotations
import argparse
import json
import random
import subprocess
import sys
from pathlib import Path

import config
import generate_script
import synthesize_voice
import lipsync
import build_manifest
import notify

sys.path.insert(0, str(config.ROOT / "publish"))
import upload


def render(manifest_path: Path) -> Path:
    out_mp4 = config.OUT / "video.mp4"
    renderer = config.ROOT / "renderer"
    # Remotion expects { "manifest": {...} } matching the component prop name
    props_path = config.OUT / "props.json"
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    props_path.write_text(json.dumps({"manifest": manifest_data}), encoding="utf-8")
    subprocess.run(
        ["npx", "remotion", "render", "PencilShort", str(out_mp4),
         f"--props={props_path}", "--public-dir=../"],
        cwd=renderer, check=True,
    )
    return out_mp4


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic")
    ap.add_argument("--auto", action="store_true")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--no-publish", action="store_true")
    args = ap.parse_args()

    topic = args.topic or (random.choice(generate_script.AUTO_TOPICS) if args.auto else None)
    if not topic:
        ap.error("--topic ver veya --auto kullan")

    print(f"=== Konu: {topic} ===")
    script = generate_script.generate(topic)
    (config.OUT / "script.json").write_text(
        json.dumps(script, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[1/4] script: {script['title']} ({len(script['beats'])} beat)")

    synthesize_voice.synthesize(script)
    print("[2/4] ses üretildi")

    lipsync.lipsync(script)
    print("[3/4] dudak senkronu tamam")

    manifest = build_manifest.build(script)
    manifest_path = config.OUT / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[4/4] manifest: {manifest['totalDurationFrames']/config.FPS:.1f}s")

    if args.no_render:
        print("Render atlandı (--no-render). Manuel: cd renderer && npx remotion render ...")
        return

    mp4 = render(manifest_path)
    print(f"[5/5] render: {mp4}")

    if args.no_publish:
        print("=== Done (upload skipped) ===")
        return

    print("[5/5] uploading to all platforms...")
    try:
        upload.publish(["tiktok", "youtube", "instagram", "facebook"])
        notify.send(
            f"Short yüklendi: {script['title']}",
            f"The Pen Family kısa video yüklendi.\n\nBaşlık: {script['title']}\nSüre: {manifest['totalDurationFrames']/config.FPS:.0f}s\nPlatformlar: TikTok, YouTube, Instagram, Facebook",
        )
        print("=== Done: video live on all platforms ===")
    except Exception as e:
        notify.send(
            f"Short HATA: {script.get('title','?')}",
            f"Yükleme hatası:\n{e}",
        )
        raise


if __name__ == "__main__":
    main()
