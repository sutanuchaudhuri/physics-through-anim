# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `.gitignore` so only source code and documentation are version-controlled
  (rendered videos under `media/` and audio under `assets/audio/` are excluded).
- `CHANGELOG.md` and this versioning convention.
- `plans/README.md` index of all planning/spec documents, with a link to the
  Jira project (**PAC — Physics Animation Creator**) that tracks the asset-library
  and fluids roadmap.
- Self-documenting `make help` that lists every target and its description.

### Changed
- Merged `documents/plan.md` into `plans/ROADMAP.md`; removed the `documents/`
  folder so all planning lives under `plans/`.
- Rewrote `README.md`: added a Jira reference, a full table of `make` commands,
  and corrected the repository-layout section.

## [0.1.0] — 2026-09-05

### Added
- Offline-first Manim studio CLI (`main.py`) with per-scene rendering, stitching,
  named compilations, and a publish workflow.
- Flagship 28-scene "Rolling, Slipping and Friction" lesson.
- Composable physics asset-library plan (M1 shipped; M1.5–M18 + fluids F1–F6
  planned) under `plans/`.
