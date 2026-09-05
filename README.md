# Physics Through Animation

Offline-first Manim studio for short, narrated physics lessons. See
[plans/ROADMAP.md](plans/ROADMAP.md) for the topic roadmap, [plans/README.md](plans/README.md)
for all design/spec docs, and [plans/ARCHITECTURE.md](plans/ARCHITECTURE.md) for the
scalable, multi-domain physics-framework namespace. The flagship 28-scene
"Rolling, Slipping and Friction" lesson follows
[plans/rolling_slipping_concepts_misconcepts.md](plans/rolling_slipping_concepts_misconcepts.md).

## Setup

```bash
brew install cairo pkg-config   # macOS system deps for pycairo
uv python install 3.11
uv sync --extra dev
uv run manim checkhealth        # confirm Manim + LaTeX + dvisvgm are working
```

Always run commands from this directory (`physics-through-anim`), not from a
sibling project. `main.py` only exists here.

## Issue tracking (Jira)

The composable **physics asset library** and **fluids** roadmap are tracked in
Jira project **PAC** (*Physics Animation Creator*):

- Board / issues: https://sutanuchaudhuri.atlassian.net/browse/PAC

Each milestone (`M1`, `M1.5`, `F1`, …) is an Epic whose Story description holds
the full plan; the [plans/](plans/) docs are the design source of truth and Jira
tracks status.

## Make commands

Run `make help` for a self-documenting list. Common variables: `QUALITY`
(`low`|`medium`|`high`), `NARRATION` (`off`|`auto`|`required`), `SCENE`
(`<id>`|`<chapter>`|`all`).

| Target | What it does |
| --- | --- |
| `make help` | List every target and its description (default goal) |
| `make setup` | Install Python 3.11 and sync dependencies (first-time) |
| `make sync` | Sync dependencies from `uv.lock` |
| `make health` | Verify Manim + LaTeX + dvisvgm |
| `make list` | List planned topics and scene names |
| `make render TOPIC=vectors` | Render a single foundations topic |
| `make render-rolling SCENE=III` | Render the rolling/slipping lesson (scene/chapter/all) |
| `make stitch-rolling` | Stitch rolling/slipping scenes into the final video |
| `make render-rod SCENE=all` | Render the rod-slipping lesson |
| `make stitch-rod` | Stitch rod-slipping scenes into the final video |
| `make render-lesson LESSON=<name>` | Render any lesson in `lessons.toml` |
| `make stitch-lesson LESSON=<name>` | Stitch any lesson in `lessons.toml` |
| `make compile LESSON= SCENES= NAME=` | Build a named, arbitrary-order compilation |
| `make stitch-compilation NAME=<name>` | Rebuild a compilation from `compilations.toml` |
| `make list-compilations` | List defined compilations |
| `make publish-prepare SOURCE= TITLE= DESCRIPTION=` | Persist a pending publish record |
| `make publish-complete SLUG= VIDEO_ID= URL=` | Record a completed upload |
| `make list-publications` | List publish records and status |
| `make test` | Run the test suite |
| `make check` | Lint (ruff) and run tests |
| `make clean` | Remove rendered media, caches, and draft audio |

## Project layout

```text
main.py                                     CLI entry point
Makefile                                    self-documenting task runner (make help)
plans/                                      design + spec docs (see plans/README.md)
  ROADMAP.md                                studio roadmap, course map, milestones
  ARCHITECTURE.md                           scalable multi-domain physics namespace
  asset_library/ fluids/                    per-milestone plans (M1-M18, F1-F6)
src/physics_through_anim/
  registry.py                               topic -> scene registry (foundations.py lessons)
  render.py                                 render + stitch orchestration, all path/quality logic
  physics/                                  physics modeling + rendering framework
    core/ kinematics/                       domain-neutral foundation
    shared/                                 cross-domain primitives (waves, fields, oscillations, particles)
    mechanics/                              M1 shipped; other domains scaffolded
    fluids/ optics/ electromagnetism/       domain packages (fill in as planned)
    acoustics/ thermodynamics/ modern/
    overlays/ recipes/ problems/ render/    cross-domain layers
  lessons/
    foundations.py                          single-file starter topics (vectors, kinematics, ...)
    rolling_slipping/                       the 28-scene "Rolling, Slipping and Friction" lesson
      common.py                             shared geometry, forces, camera zoom, layout helpers
      s00_opening_hook.py ... s27_*.py      one Manim Scene per file
      narration/s00_*.md ... s27_*.md       one narration script per scene (Markdown)
  assets/                                   narration + generic visual scene helpers (NOT physics)
tests/                                      registry + asset smoke tests

# Not version-controlled (see .gitignore): media/ (rendered videos),
# assets/audio/ (narration WAVs), and the usual Python/tool caches.
```

## Editing an individual scene

1. Open the scene file, e.g. `src/physics_through_anim/lessons/rolling_slipping/s09_center_pull.py`.
2. Reuse helpers from `common.py` instead of hand-rolling geometry:
   - `rough_ground()`, `wheel_setup()`, `thin_block()` -- all objects are placed
     *tangent* to `GROUND_Y`, don't override `y` unless you also move the ground.
   - `force_arrow()`, `velocity_arrow()`, `angular_arc()` -- keep force arrows and
     velocity arrows visually distinct (different colors/stroke widths already set).
   - `misconception_card()` / `correction_card()` -- fixed-size banner, text
     auto-shrinks to fit, so put these at the bottom band, not mid-diagram.
   - `self.zoom_to(point, width=...)` / `self.zoom_out()` -- for contact
     close-ups. Always pair a `zoom_to` with a later `zoom_out` in the same
     scene; the camera does not reset itself between scenes.
3. All equations must use `MathTex` (real LaTeX), never `Text` with symbols
   typed out. `Text` is only for plain-English labels/banners.
4. Keep new scene-specific mobjects inside the scene file. Only promote
   something to `common.py` once a second scene needs the same object.

## Testing/previewing one scene quickly

Render narration-free, low quality, for fast iteration:

```bash
uv run python main.py render-rolling 09 --quality low --narration off
```

This opens the rendered clip automatically (`manim -p`). Output lands at:

```text
media/videos/s09_center_pull/480p15/CenterPull.mp4
```

Once the visuals look right, add narration for a real preview:

```bash
uv run python main.py render-rolling 09 --quality low --narration auto
```

`--narration auto` generates a draft `.wav` via macOS `say` (cached under
`assets/audio/rolling_slipping/`) the first time, then reuses it. Delete the
`.wav` file to force regeneration after changing the narration script.

To lint/test the Python side after editing:

```bash
uv run ruff format .
uv run ruff check .
uv run pytest -q
```

## Editing narration

Narration lives in `src/physics_through_anim/lessons/rolling_slipping/narration/`,
one Markdown file per scene (`s09_center_pull.md`, etc.). The render pipeline
strips lines starting with `#` and joins the rest into one spoken block, so:

- Keep the `# Scene NN — Title` heading (it's stripped, but useful for humans).
- Write narration as plain prose paragraphs below it.
- For a reviewed/final narration file (not the `say` draft), record your own
  `.wav` at `assets/audio/rolling_slipping/<scene_stem>.wav` and render with
  `--narration required` so a missing reviewed file fails loudly instead of
  silently falling back to a draft.

## Rendering more than one scene

```bash
# one chapter (chapter ids: 0, I, II, III, IV, V, VI)
uv run python main.py render-rolling III --quality low --narration auto

# the entire 28-scene lesson
uv run python main.py render-rolling all --quality high --narration auto

# equivalent via Make
make render-rolling SCENE=III QUALITY=low NARRATION=auto
make render-rolling SCENE=all QUALITY=high NARRATION=auto
```

Quality maps to Manim's resolution folders: `low` -> `480p15`, `medium` ->
`720p30`, `high` -> `1080p60`. Rendering `all` at `high` re-renders every one
of the 28 scenes, which takes a while -- expected for a final pass.

## Stitching the final video

`stitch-rolling` concatenates every scene, in order (`s00` -> `s27`), using
ffmpeg's concat demuxer:

```bash
uv run python main.py stitch-rolling --quality high
# or
make stitch-rolling QUALITY=high
```

**Requirement:** every one of the 28 scenes must already be rendered at the
*same* quality you pass to `stitch-rolling`, because it looks for each scene's
clip under `media/videos/<scene_folder>/<resolution>/`. If any are missing you
get an explicit error listing the missing scene ids, e.g.:

```text
FileNotFoundError: Missing rendered scenes at 1080p60: 00, 01, 02, ...
```

Fix by rendering the missing scenes (or just rendering `all`) at that same
quality first, then stitch:

```bash
uv run python main.py render-rolling all --quality high --narration auto
uv run python main.py stitch-rolling --quality high
```

The output is written to `media/final/rolling_slipping_full.mp4`.

## Troubleshooting

- `can't open file '.../main.py'`: you ran the command from another project's
  directory (e.g. `physics-visualizer-engine`). `cd` into `physics-through-anim` first.
- `No such option: -l` from `manim`: you're on an older invocation pattern;
  the current CLI always builds `manim render -p -q<flag> <file> <Scene>`, so
  this shouldn't happen from `main.py` -- check for stray manual `manim` calls.
- Camera stays zoomed in for the rest of a scene: every `zoom_to()` must be
  followed by a `zoom_out()` before the scene ends; `zoom_out()` restores to
  the original frame width captured once at import time (`DEFAULT_FRAME_WIDTH`
  in `common.py`), not to whatever the camera's current width happens to be.
