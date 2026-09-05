# Physics Through Animation

This project is an offline-first Manim video studio. Each lesson should explain one
idea visually, use the smallest useful amount of algebra, and end with a short
worked example or prediction.

## Production rules

- Render in short scenes of 30-120 seconds so a lesson can be revised without
	rerendering a whole chapter.
- Keep equations, diagrams, and narration synchronized. The animation is the source
	of truth; narration should describe what is on screen rather than introduce a
	second explanation.
- Prefer reusable objects from `src/physics_through_anim/assets/` over one-off
	geometry in lesson files.
- Keep narration local. A checked-in `.wav` file is the reliable offline path;
	`say` on macOS can generate a first draft and `manim-voiceover` can sync it.
- Render draft videos with low quality first, then render the final lesson at the
	chosen resolution.
- Every lesson gets a smoke test that imports the scene and renders a short clip.

## Course map

| Order | Topic | Core visual sequence | Suggested first lesson |
| --- | --- | --- | --- |
| 01 | Vectors | components -> addition -> resultant -> dot product | `vectors` |
| 02 | Kinematics | position -> velocity -> acceleration -> motion graphs | `kinematics` |
| 03 | Newton's Laws of Motion | free-body diagram -> net force -> acceleration -> friction | `newtons_laws` |
| 04 | Circular Motion | tangent velocity -> centripetal acceleration -> force budget | `circular_motion` |
| 05 | Conservation of Momentum | isolated system -> impulse -> elastic/inelastic collision | `momentum` |
| 06 | Conservation of Energy | work -> kinetic/potential energy -> energy accounting | `energy` |
| 07 | Rotational Motion | angular variables -> torque -> rotational inertia -> rolling | `rotational_motion` |
| 08 | Orbital Mechanics | inverse-square gravity -> orbit speed -> escape speed | `orbital_mechanics` |
| 09 | Simple Harmonic Motion | restoring force -> phase -> energy exchange | `shm` |
| 10 | Fluid Mechanics | pressure -> continuity -> Bernoulli -> lift/flow | `fluid_mechanics` |

## Lesson template

1. Hook: show the physical question without an equation.
2. Model: declare the system boundary, axes, and assumptions.
3. Derive: introduce one relationship at a time and keep symbols stable.
4. Predict: ask what changes when one parameter changes.
5. Check: compare the prediction to a graph, vector, or measured value.
6. Recap: display three takeaways and a next-lesson link.

## Repository layout

```text
main.py                         CLI entry point
src/physics_through_anim/
	assets/                       reusable arrows, labels, axes, narration helpers
	lessons/                      one module per topic
	registry.py                   stable topic-to-scene registry
	render.py                     render and narration orchestration
assets/audio/                   generated or checked-in narration files
media/                          Manim output (ignored by git)
tests/                          import and registry smoke tests
```

## Commands

```bash
# Manim Community's recommended local setup uses uv.
brew install cairo pkg-config
uv python install 3.12
uv sync
uv run manim checkhealth
uv run python main.py --help
uv run python main.py list
uv run python main.py render vectors --quality low --narration auto
uv run pytest -q
```

The official guide says Mac users need Homebrew's `cairo` and `pkg-config` for
Manim's `pycairo` dependency. LaTeX is optional for `Text`, but install MacTeX
before rendering `MathTex` lessons. The pinned `manim==0.21.0` matches the
Community documentation version used by this studio.

`--narration auto` uses an existing local WAV when present and otherwise creates a
draft with macOS `say`. For a fully reproducible offline build, replace that draft
with a reviewed file under `assets/audio/` and use `--narration required`.

## Rolling, slipping and friction lesson

The complete 28-scene lesson (following `plans/rolling_slipping_concepts_misconcepts.md`
scene-for-scene, across its six chapters) lives in
`src/physics_through_anim/lessons/rolling_slipping/`. Every scene is its own file
(`s00_opening_hook.py` ... `s27_final_challenge.py`), sharing one geometry/asset
module (`common.py`) and one chapter metadata module (`chapters.py`):

| Chapter | Scenes | Theme |
| --- | --- | --- |
| 0 | 00 | Opening hook: which way does friction point? |
| I | 01-06 | What friction really does (static limit, sliding, slipping definition, frames) |
| II | 07-08 | From sliding to rolling (zero friction at rest and at constant speed) |
| III | 09-15 | Where friction direction comes from (center pull vs. top pull, general rule) |
| IV | 16-18 | Why rotation responds to torque (`tau=I alpha`, moment of inertia, rotational energy) |
| V | 19-22 | Translation plus rotation (`v_P=v_CM+omega x r`, instantaneous center) |
| VI | 23-27 | Two coupled problems (the six-step solver, four-situation recap, final challenge) |

Fixes from the previous 12-scene draft:

- Wheels and blocks are now placed *tangent* to the ground line (no floating
  circles) via `wheel_setup()` / `thin_block()` in `common.py`.
- All equations use `MathTex` (real LaTeX), not `Text` with literal symbols.
- Contact close-ups use a genuine camera zoom (`RollingLessonScene.zoom_to` /
  `zoom_out`, backed by `MovingCameraScene`), not a separate static diagram.
- Misconception/correction cards and force/velocity labels have fixed layout
  bands (title, main visual, bottom) so they no longer overlap.
- All 28 scenes from the source plan are implemented, grouped by chapter, and
  can be stitched into one continuous video.

Narration is Markdown, one file per scene under `narration/` (heading + prose;
the render pipeline strips heading lines before generating speech). Render one
scene, one chapter, or everything, then stitch the final cut:

```bash
uv run python main.py render-rolling 09 --quality low --narration auto
uv run python main.py render-rolling III --quality low --narration auto   # whole chapter
uv run python main.py render-rolling all --quality high --narration auto
uv run python main.py stitch-rolling --quality high
make render-rolling SCENE=22 QUALITY=medium NARRATION=auto
make stitch-rolling QUALITY=high
```

`stitch-rolling` uses ffmpeg's concat demuxer to join every rendered scene, in
scene order, into `media/final/rolling_slipping_full.mp4`. It requires every
scene 00-27 to already be rendered at the chosen quality.

The shared geometry, force/velocity arrows, misconception/correction cards,
friction meter, translation/rotation panels, and the rolling-constraint bridge
are in `rolling_slipping/common.py`. Add new helpers there only when an object
is genuinely reused; keep lesson-specific diagrams inside their scene file. The
physical decision rule is `f_required <= mu_s R` for no slipping, and
`f_required > mu_s R` when slipping must occur.

## Milestones

- [x] Studio CLI and reusable asset boundary
- [x] Narrated vector smoke-test lesson
- [ ] Finish the vector chapter and record reviewed narration
- [ ] Add kinematics and Newton's Laws with graph assets
- [ ] Add momentum, energy, and circular motion
- [ ] Add rotation, orbital mechanics, SHM, and fluids
- [ ] Add chapter-level assembly and captions
