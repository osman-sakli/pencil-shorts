# Roadmap

## Pipeline
- [ ] Long-form episodes end to end (`pipeline/long_episode.py`, see `docs/LONG_FORM_VIDEO_ARCHITECTURE.md`)
- [ ] Character memory system so episodes reference past stories (`docs/CHARACTER_MEMORY_SYSTEM.md`)
- [ ] OpenMontage editing integration (`docs/OPENMONTAGE_INTEGRATION_PLAN.md`)
- [ ] Highlights: auto-cut long episodes into shorts (`cut_highlights.py`, `queue_highlights.py`)
- [ ] Original songs / jingles pipeline (`generate_song_fal.py`)
- [ ] English + Turkish versions of every episode

## Quality
- [ ] Automated QA step before publish (length, audio levels, lip-sync drift, subtitles)
- [ ] Tests for `pipeline/` (manifest builder, lip-sync parsing, config)
- [ ] Remotion render tests on a fixed manifest
- [ ] Retry / resume for failed daily runs

## Publishing & ops
- [ ] Publish queue with per-platform schedule (`publish/publish_queue.py`)
- [ ] Run notifications and a small cost/usage report
- [ ] Clean up legacy scripts not used by the code-drawn pipeline

## Docs
- [ ] English versions of `PRODUCTION.md` and `docs/`
- [ ] "Add a new character" guide
