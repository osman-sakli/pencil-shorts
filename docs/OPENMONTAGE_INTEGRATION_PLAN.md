# OpenMontage Integration Plan — The Pen Family

## What is OpenMontage?
OpenMontage is a Python-based agentic AI video production system that uses:
- Remotion + FFmpeg for rendering/editing
- 52 skill files (tools) for everything: script → voice → render → export
- Claude AI as the orchestrator (agent-driven)
- Checkpoint-based progress so interrupted jobs can resume

## How It Helps Our Workflow

### Current limitation
Our pipeline is **linear and single-scene**: one script → one video ≤ 75 seconds.

### What OpenMontage adds
- **Multi-scene orchestration**: chain multiple scene renders into one file
- **Agent-driven editing decisions**: transitions, pacing, cut timing
- **Checkpoint system**: if long render fails at scene 6, resume from scene 6
- **Parallel scene processing**: scenes 1-5 can render while scene 6 is being voiced

## Integration Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    DAILY WORKFLOW                        │
│                                                          │
│  SHORT VIDEO (unchanged):                                │
│  run.py → generate_script → voice → lipsync → render → upload │
│                                                          │
│  LONG EPISODE (new — OpenMontage layer):                 │
│  long_episode.py → 8-10 × run.py scenes                 │
│                  → FFmpeg concat                         │
│                  → upload to YouTube only                │
└──────────────────────────────────────────────────────────┘
```

## Which Parts to Connect

| Component | Keep in Our System | Use OpenMontage |
|-----------|-------------------|-----------------|
| Script generation | ✅ `generate_script.py` | Use our prompts, not OM's |
| Voice synthesis | ✅ EdgeTTS | — |
| Lip sync | ✅ Rhubarb | — |
| Short render | ✅ Remotion | — |
| Multi-scene concat | — | ✅ OM's FFmpeg concat |
| Transition effects | — | ✅ OM's transition tools |
| Long-form agent | — | ✅ OM's orchestrator |
| Upload | ✅ upload-post.com | — |

## Which Parts STAY in Our System
- All existing `pipeline/` scripts — do not touch
- `renderer/` Remotion code — do not touch
- `publish/upload.py` — do not touch
- `characters.yaml` — single source of truth for all characters/voices
- `run.py` — still the main short-video entry point

## Implementation Plan (Step by Step)

### Phase 1 — Scene Concatenation (Week 1)
1. Create `pipeline/long_episode.py`
2. Runs our existing pipeline 8-10 times, each with a different scene script
3. Concatenates output videos with FFmpeg
4. No OpenMontage required for this phase

### Phase 2 — Agentic Orchestration (Week 2-3)
1. Install OpenMontage alongside our project (separate directory)
2. Wrap our `run.py` as an OpenMontage "skill"
3. Use OM's agent to decide: which scenes to generate, what transitions to use, how to pace cuts
4. OM's checkpoint system handles failures

### Phase 3 — Transition Effects (Week 3-4)
1. Add scene-change transitions via OM's FFmpeg skills
2. Add title cards between scenes (Remotion overlay)
3. Add end-screen (subscribe prompt) as final scene

## Risks and Limitations
| Risk | Mitigation |
|------|-----------|
| OpenMontage API changes | Pin to specific commit hash |
| Long render time (8-10 min video) | Use ECS Fargate with larger instance |
| Memory issues on Fargate Spot | Set 4GB container limit; use checkpoint |
| FFmpeg codec mismatch | Standardize on H.264/AAC in all renders |
| Our `run.py` not reentrant | Pass `--out-dir` per scene to isolate outputs |

## Secret Values
**Sır değerleri ASLA repoya/log'a yazma — sadece SSM'e**  
OpenMontage needs the same `ANTHROPIC_API_KEY`. Already in SSM. Do not duplicate.
