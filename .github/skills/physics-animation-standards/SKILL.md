---
name: physics-animation-standards
description: 'Production standards for Manim physics animation scenes in this repo (src/physics_through_anim/lessons/**). Use when creating or editing a Manim scene, adding force/kinematic vectors, deriving a formula, laying out multiple equations, animating rolling/rotation, simulating rigid-body/pendulum motion with manim-physics, reviewing a specific scene for standards compliance, scaffolding a brand-new lesson from a plan document, stitching a lesson''s rendered scenes into one final video from the command line, adding/using per-scene event-transcript logging to debug "what happened when", composing a scene from smaller sub-scenes played sequentially (fade in/out) or all at once, creating a 3D scene or transforming a 2D shape into 3D with manim''s ThreeDScene camera, or updating this skill by learning from an external file/folder of example Manim animation code. Covers reference-frame icons, FBD-vs-kinematics vector colors, assumption-checked derivations, quadrant layout for multi-formula scenes, exact perpendicular velocity vectors, mandatory real rolling animation, the manim-physics plugin (SpaceScene/Pendulum/Wave), the overlap-avoidance layout contract, the lessons.toml/LessonRegistry scaffold workflow, the per-scene review checklist, the render/stitch/Makefile command-line workflow, the SceneEventLogMixin transcript-logging utility, the sub-scene composition helper (sequential/together), the ThreeDLessonScene 3D base class with the 2D-to-3D lift_to_3d transform, the finish_with_narration audio/video sync rule, and the self-updating learn-from-example workflow.'
---

# Physics Animation Production Standards (Manim)

Applies to every scene under `src/physics_through_anim/lessons/**`. These are
non-negotiable production rules discovered from reviewing the rolling/slipping
lesson, not suggestions. New scenes must follow them from the start; existing
scenes should be brought into compliance opportunistically.

## 1. Reference frame and observer icons

When a scene compares reference frames or observers (ground vs. moving frame,
inertial vs. accelerating frame), show a small icon instead of only a text
label. Three ready-made SVG icons live in `assets/icons/` and are loaded via
`SVGMobject`:

```python
from manim import SVGMobject

icon = SVGMobject("assets/icons/inertial_observer.svg")
icon.set_color(WHITE)
icon.scale(0.4)
```

Loader helpers already exist in `common.py` — use these instead of calling
`SVGMobject` directly:

- `inertial_observer_icon(scale=1.0)` — eye-on-a-stand glyph. Use for an
  observer at rest or moving at constant velocity.
- `non_inertial_observer_icon(scale=1.0)` — same glyph plus a curved
  acceleration arrow. Use **only** when that observer's frame is actually
  accelerating or rotating (don't use it just because something looks fast).
- `reference_frame_icon(scale=1.0)` — simple x/y axes glyph. Use next to an
  `S`/`S'` label whenever a scene sets up a coordinate frame, even if both
  frames happen to be inertial (see `s06_two_frames.py`).

Never assert a frame is non-inertial unless the scene's physics actually
requires acceleration in that frame — check this before picking the icon.

## 2. FBD vectors vs. kinematic vectors — always different colors

Force-diagram (FBD) vectors and kinematics vectors must never share a color
family, so a viewer can tell at a glance which kind of arrow they're looking
at. Use the constants in `common.py`, never a bare color literal:

| Vector | Constant | Helper |
| --- | --- | --- |
| Applied force `F` | `COLOR_APPLIED` (yellow) | `force_arrow(..., color=COLOR_APPLIED)` |
| Friction `f` | `COLOR_FRICTION` (orange) | `force_arrow(...)` (default) |
| Normal force `N` | `COLOR_NORMAL` (green) | `force_arrow(..., color=COLOR_NORMAL)` |
| Weight `mg` | `COLOR_WEIGHT` (purple) | `force_arrow(..., color=COLOR_WEIGHT)` |
| Linear velocity `v` | `COLOR_VELOCITY` (blue) | `velocity_arrow(...)` |
| Angular velocity `omega` | `COLOR_ANGULAR` (teal) | `angular_arc(...)` |
| Linear acceleration `a` | `COLOR_ACCEL` (pink) | `acceleration_arrow(...)` |
| Angular acceleration `alpha` | `COLOR_ANGULAR_ACCEL` (violet) | `angular_accel_arc(...)` |

Force arrows use a heavier stroke (`stroke_width=6`) than velocity arrows
(`stroke_width=4`) so the two families are distinct even in grayscale.

## 3. Formulas must state their assumption, and derivations must substitute on screen

Never let a formula like `I = m R^2 / 2` appear without saying which shape it
assumes (solid disk vs. hoop vs. sphere). Never jump straight to a boxed
numeric result — show the substitution happening.

Use `derive_with_assumption(scene, general_tex, assumption_tex, result_tex,
position=None)` from `common.py`:

1. Writes the general relation (e.g. `f = I*alpha/R`, `a = alpha*R`).
2. Fades in the modeling assumption in a distinct color (e.g.
   `"solid disk:\ I=\tfrac12 mR^2"`).
3. Waits, then fades **both** out while fading the specific result in.

See `s10_center_pull_equations.py` for the reference implementation.

## 4. No screen may be "just text" — split multi-formula scenes into quadrants with a matching mini-animation

If a scene needs to show more than ~2 formulas in sequence, do not stack them
as a column of `MathTex`/`Text`. Use `quadrant_anchors(spread=3.2)` from
`common.py` to get four non-overlapping anchor points (top-left, top-right,
bottom-left, bottom-right), and pair each formula with a small animation that
gives the formula a visual referent (an orbiting particle, a growing arrow, a
transforming shape) — not a static equation.

See `s18_rotational_energy.py`: four particles orbit at four different radii,
each next to the line of the derivation it justifies, instead of four lines
of text stacked down the middle of the screen.

## 5. Kinematic vectors must be geometrically exact, and shown at more than one point

When illustrating rotation-plus-translation (rolling without slipping), do
not just label one arrow "v" and move on. Show several points around the rim
and make the geometry explicit: each point's velocity vector is **perpendicular
to the line joining that point to the contact point** (the instantaneous axis
of rotation), per `v_P = omega x r_(P/contact)`.

Use `rolling_point_velocities(disk, v_scale=1.0)` from `common.py` — it samples
the top, 3 o'clock, and 9 o'clock rim points, computes each velocity vector
perpendicular to the line from that point to the contact point, and marks the
contact point itself with `v = 0`. See `s20_bottom_center_top.py` for how this
follows up the specific bottom/center/top values with the general rule.

**The `omega x r` (rotational) contribution at *any* point must be drawn
tangential to the circle at that point — never a fixed direction like `UP`.**
A rotational velocity vector that doesn't visibly form a right angle with the
radius line to that point is wrong, no matter what the label says. Compute it
from the actual geometry, don't hardcode a direction:

```python
r_vec = point_p - disk.wheel_center  # radius vector to the point
tangent_dir = np.array([r_vec[1], -r_vec[0], 0.0])  # rotate 90 deg (clockwise sense)
tangent_dir = tangent_dir / np.linalg.norm(tangent_dir) * length
v_rot = velocity_arrow(point_p, point_p + tangent_dir, label)
```

This is the same `(r_y, -r_x)` pattern `rolling_point_velocities` already uses
— reuse that convention rather than inventing a new one. When showing a
single arbitrary point `P` (not one of the rim's cardinal points), also draw
a faint dashed radius line from the center to `P` so the right angle between
`r` and `omega x r` is visible, not just asserted by the label. See the fixed
version of `s19_velocity_of_point.py`.

## 6. Always show which observer/reference frame a kinematic vector is measured in

Velocity (and hence "who is moving") is frame-dependent — this is the whole
point of Scene 6. Every scene that draws a velocity, angular velocity, or
acceleration vector must make the reference frame explicit, not just imply
"the ground, obviously." Use the icons/helpers from Rule 1
(`reference_frame_icon`, `inertial_observer_icon`, `non_inertial_observer_icon`)
or, at minimum, a short label such as `\text{(ground frame)}` near the scene
header — never leave it unstated. This applies even to single-frame scenes
(e.g. "Velocity of Any Point" only makes sense once you've said the ground is
the observer computing `v_{\rm CM}`); it is not only for the two-frame scenes.

## 7. Wheels must actually roll — never fake it with a bare `.shift`

A wheel that translates without rotating is *sliding*, not rolling, and looks
wrong even at a glance. Never animate a wheel with `mobject.animate.shift(...)`
alone. Use `animate_rolling(scene, wheel_group, radius, distance, run_time=3.0,
rightward=True)` from `common.py`, which translates and spins the wheel
together at the correct rate `v = omega * R` using a `ValueTracker` + updater
(rebuilding from a stored copy each frame so there's no cumulative drift).

Any scene depicting "rolling at constant speed," "rolling toward a slip
threshold," etc. must show the actual rolling motion at least once — a static
`FadeIn` of a wheel is not sufficient on its own if the scene's point is
motion. See `s08_disk_rolling_constant.py`.

## 8. Layout contract (avoid overlaps — see also `common.py` module docstring)

- Title band: `y in [2.9, 3.8]` via `scene_header()`.
- Main visual band: `y in [-2.0, 2.6]` — wheels, blocks, force/kinematic arrows.
- Ground line: `y = GROUND_Y = -2.0`; objects from `wheel_setup()`/`thin_block()`
  are placed tangent to it automatically — don't override `y` without also
  moving the ground.
- Bottom band: `y in [-3.8, -2.4]` — equations, misconception/correction cards.
- **Never** let a misconception/correction card's shift put it inside the
  main visual band; a card is `10.5` wide and `0.95` tall, so verify its
  vertical center is at or below `-2.6` if a wheel (radius up to ~1.1, so
  spanning up to `y=0.2`) is present in the same scene.
- If two elements would occupy the same region at the same time (e.g. a
  misconception card and a friction meter), `FadeOut` the first before
  bringing in the second rather than letting them coexist "just in case."

## 9. No plain-English text may sit on top of, or immediately beside, a diagram/vector

Labels on force/velocity/angular arrows must be symbols only (`F`, `f_k`,
`v_{\rm CM}`, `\omega`), never English words like "tends forward" or "slides
back" — use `v_{\rm rel}` or similar symbolic labels instead, and let
narration/captions carry the qualitative meaning. Full-sentence captions
(prompts, conclusions, misconception/correction cards) belong in the bottom
band, spatially separate from the diagram, never overlapping a vector.

## 10. `manim-physics` plugin — what it's for and how to use it here

`manim-physics==0.2.4` is an installed dependency (see `pyproject.toml`). **Pin
it to `0.2.4`, never `>=0.4.0`**: manim-physics 0.4.0+ requires `manim<0.19`,
which conflicts with this repo's pinned `manim==0.21.0`; 0.2.4 declares no
upper bound on manim and is verified working (`from manim_physics import ...`
imports and renders cleanly against 0.21.0 as of this writing).

```python
from manim_physics import Pendulum, MultiPendulum, SpaceScene
```

What it gives us and when to reach for it instead of hand-computed kinematics:

- **`SpaceScene` + `make_rigid_body(...)`** — a pymunk-backed 2D physics engine.
  Bodies added via `make_rigid_body` fall, collide, and respond to friction
  coefficients automatically. Use this for scenes where the *point* is that
  motion emerges from the physics (e.g. a block released above the ground and
  settling, two disks colliding) rather than a scripted `.animate.shift`.
  **Caveat:** `SpaceScene` is a different base class from our
  `RollingLessonScene(MovingCameraScene)` — a scene using `SpaceScene` will not
  have `zoom_to`/`zoom_out`/`scene_header`/etc. for free; either don't mix them,
  or create a small `RollingSpaceScene(SpaceScene)` mixin that duplicates the
  handful of layout helpers it needs.
- **`Pendulum(length, initial_theta, pivot_point)` / `MultiPendulum(...)`** —
  physically simulated pendulum bobs (needs `SpaceScene` + `make_rigid_body`).
  This is the natural fit for the planned SHM lesson (`shm` topic in
  `registry.py`) instead of hand-animating a swinging bob.
- **`manim_physics.wave` (`LinearWave`, `RadialWave`, `StandingWave`)** —
  ready-made wave field animations; candidates for a future waves/SHM lesson
  rather than something to build from scratch with `ParametricFunction`.
- **`manim_physics.electromagnetism` (`Charge`, `ElectricField`,
  `MagneticField`, `Wire`) and `manim_physics.optics` (`Lens`, `Ray`)** —
  not needed by the current mechanics-only roadmap; note for if an EM/optics
  lesson is ever added, don't hand-roll field-line plotting first.

Do not reach for `manim-physics` to replace the deliberately-exact, hand-computed
vectors this skill mandates elsewhere (Rules 2 and 5) — those need to show a
*specific, checkable* value (e.g. `v = omega R` exactly at the contact point).
Use `manim-physics` when the pedagogical point is emergent/simulated behavior,
not when it's a precise textbook relationship being illustrated.

### 10.1 Real API surface (0.2.4) — the readthedocs layout is for a newer version

The installed `0.2.4` package is **flat modules**, not the nested
`manim_physics.rigid_mechanics.rigid_mechanics` package shown on the current
readthedocs site (that's the `0.4.0` layout, which we can't use — see above).
For `0.2.4`, everything is exported from the top level:

```python
from manim_physics import SpaceScene, Space, Pendulum, MultiPendulum
```

`SpaceScene.make_rigid_body(*mobs, elasticity=0.8, density=1, friction=0.8)`
only knows how to wrap `Circle`, `Line`, `Rectangle`/subclasses, and
`Polygram`/subclasses (see `get_shape` in `rigid_mechanics.py`) — passing any
other mobject type raises an `AttributeError` with no useful message pointing
at the cause. Stick to those shapes for rigid bodies.

### 10.2 Gotcha: attach visual-only markers *after* `make_rigid_body`, never before

`make_rigid_body` iterates `mob.family_members_with_points()` and turns
**every** shape-having member into its own independent pymunk body. If you
build `VGroup(disk, marker)` and call `make_rigid_body(that_group)`, the
marker becomes its own free-falling rigid body instead of a passenger that
rotates with the disk — it visibly flies off on its own.

Correct order:

```python
disk = Circle(radius=0.9, ...)
self.make_rigid_body(disk, friction=0.9, elasticity=0.1)   # wire physics first
disk.body.angular_velocity = -4.0                          # set initial spin
marker = Dot(disk.get_top(), ...)
disk.add(marker)  # attach AFTER — now a real submobject, moves/rotates for free
```

`manim_physics`'s own per-frame updater calls `disk.move_to(...)` and
`disk.rotate(...)` on the whole mobject family, so a marker added as a true
submobject (not a `VGroup` sibling) rides along automatically without needing
its own updater.

### 10.3 Gotcha: tune initial angular velocity from the physics, or it exits the frame

For a solid disk with zero initial `v_CM` released spinning at `omega_0` on a
surface with enough friction to reach pure rolling, conserving angular
momentum about the contact point gives the final rolling speed:

$$
v_f = \frac{\omega_0 R}{3}
$$

A first attempt with `omega_0 = -9` on a `radius=0.9` disk reached the edge of
frame in under 4 seconds during a 6-second `self.wait()` — completely off
screen for the second half of the clip. Fixed by solving for `omega_0` such
that `v_f * wait_time` fits inside the available travel distance, using
`omega_0 = -4.0` instead (see `s28_pymunk_spin_to_roll.py`). Before shipping
any `manim-physics` scene, calculate (don't guess) the expected final speed
and check it against the frame width and wait duration.

### 10.4 Gotcha: long `MathTex` captions can visibly overflow the frame edge

A closing caption written as one long sentence (`"Friction acted until
v_CM=omega R -- no applied force needed"` at `font_size=30`) rendered wider
than the frame and was cut off past the right edge — Manim does not
auto-shrink or wrap `MathTex`/`Text` to fit. Caught by rendering a still frame
*after* the `Write` animation had fully completed (not mid-`Write`, which
naturally looks "cut off" too and is easy to misdiagnose as the same bug).
Fix: keep captions short enough to fit at the given `font_size`, or explicitly
call `.scale_to_fit_width(...)` the way `misconception_card`/`correction_card`
already do in `common.py`.

### 10.5 `SpaceScene` doesn't get narration for free

`RollingLessonScene.add_narration()` lives on our own base class; a scene
built on `SpaceScene` (a plain `Scene` subclass from `manim_physics`) needs
its own one-line copy of the same `PHYSICS_NARRATION_FILE` → `add_sound(...)`
check in its `construct()` — it is not inherited. See
`s28_pymunk_spin_to_roll.py` for the copy-pasted (intentionally small,
not worth a shared mixin for one line) version.

### 10.6 Gotcha: a static `Line`'s collision cushion is `stroke_width - 3.95` thick

`make_static_body(line)` turns the line into a `pymunk.Segment` whose collision
**radius** is `line.stroke_width - 3.95` (see `get_shape` in
`rigid_mechanics.py`). A ground drawn with the repo-default `stroke_width=6`
therefore has a **~2.05-unit-thick invisible collision cushion** bulging above
and below the visible line. Any rigid body placed "resting on" that line is
actually buried ~2 units deep inside the cushion, and pymunk resolves the
overlap with a huge separating impulse that visibly launches the body up and
off screen on the very first step (with several bodies, the whole scene
explodes at once).

Fix: give the **physics** ground/incline `Line`s a `stroke_width` near `4.0`
(e.g. `4.05` → radius ≈ `0.1`), not `6`. `stroke_width` below `3.95` gives a
**negative** radius and is just as broken — stay a hair above `4`. If you want
a visually thicker ground, draw a separate thick cosmetic `Line` and run
`make_static_body` on a thin (`~4.05`) invisible one underneath. Then place
each body with its contact surface at `ground_y + (stroke_width - 3.95) + R`
(disks) or `+ height/2` (boxes), plus a small settle gap (see 10.7).
Discovered rebuilding `s00_opening_hook.py` into a four-quadrant pymunk scene.

### 10.7 Gotcha: pymunk steps at the frame dt — low-quality (15 fps) sims are unreliable

`_step(space, dt)` calls `space.space.step(dt)` with the **render frame's** dt,
and manim-physics' own docstring warns that a low frame rate lets fast or
in-contact objects pass through / mis-resolve against static bodies. At
`--quality low` (`480p15`, dt ≈ `0.067 s`) a pymunk scene that is correct at
`--quality high` (`1080p60`, dt ≈ `0.017 s`) can tunnel, jitter, or eject —
**the low-quality render does not crash, it just lies.** So:

- Always verify a `manim-physics` scene at `--quality high`, and extract a few
  still frames (`ffmpeg -ss <t> -i out.mp4 -frames:v 1 frame.png`) across the
  simulation window to confirm bodies settle and stay in frame — do not trust
  a low-quality dry-run for physics correctness (it's still fine for proving a
  *non-physics* scene merely renders, per Rule 11).
- Because of this, a `manim-physics` scene is effectively **high-quality-only**;
  note that in the scene's module docstring so a future low-quality stitch
  isn't mistaken for a regression.
- Give every body a small **settle gap** (≈`0.15`) above its collision surface
  so it drops a hair and settles, rather than starting flush/embedded — this
  is gentler than an exact-contact start at any frame rate, and combined with
  low `elasticity` (≈`0.05`) avoids first-step bounce.

Discovered rebuilding `s00_opening_hook.py`; its docstring records the
high-quality-only caveat.

## 11. Scaffolding a brand-new lesson from a plan/instruction

Trigger phrases: *"Create a scaffold based on the following instruction/plan
…"*, *"scaffold a new lesson for …"*. The user is handing you a plan document
(a path, or pasted text) describing a sequence of scenes; produce a
**renderable skeleton**, not prose describing what you'd build.

Read the plan in full first and enumerate every scene it describes (its own
numbering/ids, one-line summary, and which chapter/section it belongs to).
Then create, under `src/physics_through_anim/lessons/<lesson_name>/`:

- `__init__.py` — one-line docstring, nothing else.
- `common.py` — a `<Lesson>Scene(SceneEventLogMixin, MovingCameraScene)` base
  class (mix in `SceneEventLogMixin` from `physics_through_anim.scene_logging`
  — see Rule 14 — and set `LESSON_NAME = "<lesson_name>"`) with
  `add_narration()`, `zoom_to()`/`zoom_out()` (snapshot
  `DEFAULT_FRAME_WIDTH = config.frame_width` at import time, never read
  `camera.frame_width` dynamically — see the rolling/slipping lesson's fix for
  why), `scene_header()`, `chapter_banner()`, plus whatever geometry/force/graph
  helpers this specific lesson's plan implies (mirror the shape of
  `rolling_slipping/common.py` or `rod_slipping/common.py`, don't invent a new
  pattern). Apply Rules 1–10 to every helper you add here, not just to scenes.
  If the plan is fundamentally 3D (fields, gyroscopes, orbital mechanics,
  surfaces), base the class on `ThreeDLessonScene` from
  `physics_through_anim.threed` instead of `MovingCameraScene` — see Rule 17.
- `chapters.py` — a `CHAPTERS` dict/dataclass whose keys mirror the plan's own
  phase/section headings (don't invent your own grouping).
- One `sNN_<slug>.py` file per scene from the plan, each a **working stub**:

  ```python
  from physics_through_anim.lessons.<lesson_name>.common import <Lesson>Scene


  class SceneNN<Slug>(<Lesson>Scene):
      """Scene NN -- <one-line summary from the plan>."""

      def construct(self) -> None:
          self.add_narration()
          header = self.scene_header("NN", "<Title>", "<Subtitle>")
          self.play(FadeIn(header))
          # TODO: <bullet list, copied from the plan, of what this scene must show>
          self.wait(2)
  ```

  A stub must actually render (correct imports, correct base class, no syntax
  errors) — the `# TODO` block is the content checklist for filling it in
  later, not a placeholder for broken code.
- `narration/sNN_<slug>.md` per scene — the plan's own narration text if it
  supplies one, otherwise a short `# TODO narration` placeholder plus a
  one-line summary of what should be said.
- Register every scene in **`lessons/lessons.toml`** (the factory manifest —
  see `lesson_registry.py`): add a `[lessons.<lesson_name>]` table with `dir`,
  `audio_subdir`, `final_output`, and one `[lessons.<lesson_name>.scenes."NN"]`
  sub-table per scene (`file`, `class_name`, `narration`, `chapter`). **Never
  hand-edit `render.py`** to register a new lesson — it has no per-lesson
  code left; everything is driven by this manifest through `LessonRegistry`.
- A new, well-formed lesson needs **no changes to `main.py`**: the generic
  `render-lesson <lesson_name> <scene|chapter|all>` and
  `stitch-lesson <lesson_name>` subcommands work for anything in
  `lessons.toml`. Only add lesson-specific `render-<name>`/`stitch-<name>`
  subcommands (mirroring `render-rolling`/`render-rod`) and matching Makefile
  targets if the user wants the shorter, memorable command form.

After scaffolding, immediately dry-run the whole lesson at low quality with
narration off to prove every stub actually renders before considering the
scaffold done:

```bash
uv run python main.py render-lesson <lesson_name> all --quality low --narration off
```

Fix any crash before handing the scaffold back — a stub that doesn't render is
not a finished scaffold.

## 12. Reviewing a specific scene against these standards

Trigger phrases: *"review scene NN"*, *"how can `sNN_....py` be improved"*, or
any request to work on one named/numbered scene. Read that one scene file (and
the `common.py` helpers it calls) and walk it against every rule in this
document as an explicit checklist, citing the actual file and line for each
finding — generic advice ("consider better colors") is not acceptable, a
finding must say what's wrong and where:

1. **Rule 1** — are reference-frame/observer icons present wherever frames or
   observers are compared, and is `non_inertial_observer_icon` only used where
   that frame is actually accelerating?
2. **Rule 2** — does every force arrow and every kinematic vector use the
   correct named color constant (`COLOR_APPLIED`/`COLOR_FRICTION`/etc.), never
   a bare hex/color literal?
3. **Rule 3** — does every formula that bakes in a modeling assumption state
   that assumption on screen via `derive_with_assumption`, instead of jumping
   straight to a boxed result?
4. **Rule 4** — if the scene shows more than ~2 formulas, are they laid out
   with `quadrant_anchors` plus a paired mini-animation, rather than stacked as
   bare text down the middle of the screen?
5. **Rule 5** — is every rotational/tangential vector computed from the actual
   point geometry (the `(r_y, -r_x)` pattern), never a hardcoded direction like
   `UP`/`RIGHT`?
6. **Rule 6** — is the observer/reference frame for every kinematic vector
   stated explicitly (icon or label), not left implicit?
7. **Rule 7** — does any rotating/rolling body move via `animate_rolling` (or
   this lesson's equivalent), never a bare `.animate.shift`?
8. **Rule 8** — do all elements respect the title/main/bottom `y` bands, with
   nothing overlapping (check misconception/correction card placement against
   any wheel/diagram in frame)?
9. **Rule 9** — is all plain-English text confined to the bottom band, with
   only symbols on/beside diagrams and vectors?
10. **Rule 10** (only if `manim-physics` is used) — pinned `0.2.4` API surface,
    markers attached *after* `make_rigid_body`, initial velocities tuned
    against frame width/wait time, no caption overflow, narration wired
    manually since `SpaceScene` doesn't inherit it.
11. **Rule 18** — does `construct()` end with `self.finish_with_narration()`,
    and do the visuals span (not just freeze at the end of) the narration?
    Render with `--narration auto` and confirm the clip duration `>=` the
    narration WAV with only a small `pad_s` in the transcript.

Then report a **prioritized fix list**, ordered crashes/incorrect-physics
first, then layout/overlap, then cosmetic/color issues last — not a rewritten
file. Apply fixes only after presenting findings, unless the user has already
asked you to just fix it.

## 13. Stitching a lesson's rendered scenes into one final video

Trigger phrases: *"stitch the videos in this folder"*, *"combine the rendered
scenes into one video"*. Never hand-roll a new `ffmpeg` invocation — always go
through the existing `stitch_lesson`/`stitch-<lesson>` pipeline (ffmpeg concat
demuxer, `-c copy`, no re-encode), since that is what already guarantees scene
order and validates that every scene in `lessons.toml` actually rendered.

Preferred commands, in order:

```bash
# 1. Makefile target (create it first if this lesson doesn't have one yet —
#    see below)
make stitch-<lesson_name> QUALITY=high

# 2. Equivalent direct CLI call
uv run python main.py stitch-<lesson_name> --quality high

# 3. Generic form — works for any lesson in lessons.toml, no main.py/Makefile
#    changes needed
uv run python main.py stitch-lesson <lesson_name> --quality high
```

Rules to follow every time:

- Render every scene first — `stitch-*` refuses to run and reports exactly
  which scene ids are missing if any scene's
  `media/videos/<lesson_name>/<file_stem>/<resolution>/<ClassName>.mp4`
  doesn't exist:

  ```bash
  uv run python main.py render-<lesson_name> all --quality high --narration auto
  ```

  Every lesson's videos are grouped under their own
  `media/videos/<lesson_name>/` folder, never flattened together — see
  Rule 13.1 for how and why.

- **Quality must match** between the render and stitch steps — `stitch`
  only looks in the resolution folder for the chosen `--quality`
  (`low`→`480p15`, `medium`→`720p30`, `high`→`1080p60`). A "missing scenes"
  error is very often a quality mismatch, not an actual missing render —
  check the resolution folder before assuming scenes need re-rendering.
- Output lands at `media/final/<lesson_name>_full.mp4` (or the
  `lessons.toml` entry's `final_output` override, if set).
- If the `Makefile` has no target for this lesson yet, add one before telling
  the user to run `make stitch-<lesson>` — never reference a target that
  doesn't exist. Follow the existing `render-rolling`/`stitch-rolling` pattern
  exactly:

  ```makefile
  render-<lesson_name>:
  	uv run python main.py render-<lesson_name> $(or $(SCENE),all) --quality $(or $(QUALITY),low) --narration $(or $(NARRATION),auto)

  stitch-<lesson_name>:
  	uv run python main.py stitch-<lesson_name> --quality $(or $(QUALITY),low)
  ```

  (Tabs, not spaces, for the recipe lines — Make requires it.) Remember to add
  both new target names to the `.PHONY:` line at the top of the file. If the
  repo has no `Makefile` at all yet, create one with at least `help`, the two
  targets above, and `test`/`check`, matching this repo's existing layout.
  Generic `render-lesson`/`stitch-lesson` Makefile targets (parameterized by
  `LESSON=`) already exist and work for any lesson without adding anything —
  prefer pointing the user at those if a lesson-specific target isn't worth
  creating.

### 13.1 Videos are grouped by lesson under `media/videos/<lesson_name>/` — never flattened

Manim's own default `video_dir` template
(`{media_dir}/videos/{module_name}/{quality}`) knows nothing about lessons —
left alone, it dumps every scene from every lesson into the same flat
`media/videos/` folder, keyed only by scene file stem, so two lessons that
happen to reuse a filename (or just dozens of scenes from different lessons)
end up impossible to tell apart at a glance.

Fixed by `render_lesson_scene()` in `render.py`, which calls
`_ensure_video_dir_config(lesson)` before every `manim render` invocation.
That helper (re)writes a small `manim.cfg` inside the lesson's own directory:

```ini
[CLI]
video_dir = {media_dir}/videos/<lesson_name>/{module_name}/{quality}
```

and passes it via `-c <lesson_dir>/manim.cfg` on the `manim render` command
line (`--media_dir` itself is left at its default, so `images`/`Tex`/`texts`
are unaffected — only videos are grouped). This is **fully automatic for any
lesson in `lessons.toml`**, including ones scaffolded later per Rule 11 — do
not hand-maintain a `manim.cfg` per lesson yourself, and do not pass
`--media_dir` per-lesson as an alternative (that would also move `images`/
`Tex`/`texts` under a per-lesson path, which is not what's being asked for
here and would be a bigger, unrequested layout change).

The resulting path is
`media/videos/<lesson_name>/<file_stem>/<resolution>/<ClassName>.mp4` —
`stitch_lesson()` looks for clips at exactly this path, so if you ever see a
"missing scenes" error after moving/copying rendered output by hand, check
that it landed under the lesson's subfolder, not directly under
`media/videos/`.

## 14. Custom Python event logging — an append-only transcript of "what happened when"

Manim's own render log and the narration audio are not enough to answer "what
was the rod's actual angle in scene 23 when that vector looked wrong" after
the fact, without re-rendering with breakpoints. Because every on-screen
object is a plain Python `Mobject`, log its state straight to a text file as
the scene runs, using Python's stdlib `logging` module — independent of
narration and independent of manim's own (very verbose) render log:

```python
from manim import *
import logging

logging.basicConfig(filename="extensive_transcript.txt", level=logging.INFO)

class MetadataScene(Scene):
    def construct(self):
        circle = Circle(color=BLUE)
        # self.renderer.num_plays is the correct attribute name (not
        # num_played_animations — that name doesn't exist on manim's renderer).
        logging.info(
            f"Animation {self.renderer.num_plays}: Created Circle at "
            f"{circle.get_center()} with color {circle.color}"
        )
        self.play(Create(circle))
```

**Don't hand-roll this per scene.** The pattern above is wired up once, project-wide,
as `physics_through_anim.scene_logging`:

- `SceneEventLogMixin` — mix into every lesson's `<Lesson>Scene` base class
  (`class RodLessonScene(SceneEventLogMixin, MovingCameraScene)`, with
  `LESSON_NAME = "rod_slipping"` as a class attribute). Its `setup()` looks up
  this scene's own id from `lessons.toml` by class name (no per-scene-file
  wiring needed) and opens a fresh log file at
  `media/logs/<lesson_name>/<scene_id>_<ClassName>.log`; its `tear_down()`
  logs a closing `scene_teardown` event. Both hooks are called automatically
  by manim's own render pipeline (`Scene.render()` calls `setup()` then
  `construct()` then `tear_down()`), so every scaffolded scene gets a
  transcript for free with zero code in the scene file itself.
- `self.log_event(label, **fields)` — call this by hand from inside any
  scene's `construct()` wherever the automatic setup/teardown events aren't
  enough, e.g. right after computing a value you want a permanent record of:
  `self.log_event("slip_detected", theta_deg=24.15, t=1.175)`. This is the
  **manual extension point** — add calls here whenever you need to trace a
  specific value, it is not meant to be exhaustively auto-generated.
- `self.log_mobject(label, mobject)` — logs a mobject's type, `get_center()`,
  and `color` in one call, e.g. `self.log_mobject("rod_at_slip", rod)`.
- Every log line includes `animation=N` (`self.renderer.num_plays` at the time
  of the call) and a wall-clock timestamp, so a transcript line can always be
  matched back to a specific `self.play(...)` call and a specific moment.

**This must be part of every new lesson's scaffold (Rule 11)**: the
`<Lesson>Scene` base class created during scaffolding mixes in
`SceneEventLogMixin` and sets `LESSON_NAME` — do not scaffold a lesson without
it. It is safe to retrofit onto an existing lesson's base class too (just add
the mixin and `LESSON_NAME`); no changes to individual scene files are
required for the automatic setup/teardown transcript to start working.

Transcripts live under `media/logs/<lesson_name>/` (alongside the other
generated artifacts in `media/`) and are overwritten (`mode="w"`) each time a
scene is re-rendered, so a transcript always reflects the most recent run —
never manually diff against a stale one from a previous render.

## 15. Learning from an external file or folder to improve this skill

Trigger phrases: *"learn from `<path>` how to write better manimation"*,
*"update this skill based on `<path>`"*. This is the **only** instruction type
in this document that edits `SKILL.md` itself — every other rule edits scene
or lesson code. Only run this workflow on an explicit request naming a
concrete file or folder; never rewrite this document opportunistically just
because you noticed good code somewhere else while doing other work.

1. Read the named file in full, or, for a folder, survey it broadly first
   (`list_dir`/`file_search`) and then read every file that looks like it
   contains scene/animation code, not just the first one or two — a technique
   that only shows up in the third example is just as valid as one in the
   first.
2. Extract concrete, generalizable techniques: a layout trick, a helper
   function shape, a way of animating something, a plugin usage pattern, a bug
   class and its fix — not vague impressions. For each one, check it against
   Rules 1–14 already in this document:
   - If it's a specific case of an existing rule, don't add a new rule —
     at most add one worked example/reference to the existing rule's prose.
   - If it genuinely conflicts with an existing rule (e.g. a different color
     convention, a different base-class shape, positioning without the layout
     bands from Rule 8), **do not import the conflicting convention as-is**.
     Reconcile it: adapt the external technique to this repo's established
     patterns (`common.py` helpers, `COLOR_*` constants, the layout bands,
     `SceneEventLogMixin`, the `lessons.toml` factory) rather than
     introducing a second, inconsistent way of doing the same thing.
   - If it's genuinely new, add it as a new top-level numbered rule (or a
     `N.M` gotcha under an existing rule, following the style of the `10.1`–
     `10.5` sub-rules) at the end of the document, in the same voice and
     format as the existing rules: a short rationale, a minimal code
     example if one clarifies it, and a citation of the source file/folder
     path so a future reader knows where the convention came from.
3. Never delete or weaken an existing rule as part of this workflow —
   only add. If the source material seems to contradict a rule, flag that
   explicitly to the user instead of silently overwriting it.
4. Update the YAML frontmatter `description` if the newly added rule(s)
   change what kinds of requests this skill should be discovered for (mirror
   how Rules 11–14 were each added along with a frontmatter update).
5. After editing, report a short summary of exactly what was learned and
   added (rule numbers and one line each) — do not silently rewrite the file
   and say nothing, and do not present it as a full rewrite when it was an
   incremental addition.

## 16. Composing a scene from sub-scenes (sequential fades or all-at-once)

When a scene is really several small visual segments — "show case A, then B,
then C" or "show all four cases at once" — don't hand-write the
`FadeIn`/`wait`/`FadeOut` chain each time. Use the framework helper
`physics_through_anim.subscenes`:

```python
from physics_through_anim.subscenes import SubScene

segments = [
    SubScene(build=lambda: block_demo(), hold=1.5, name="block"),
    SubScene(build=lambda: disk_demo(), hold=1.5, name="disk"),
]
# one at a time, each fades in -> holds sub.hold -> fades out -> next
self.play_subscenes(segments, mode="sequential")
# or all on screen together, auto-placed into quadrant/row anchors
self.play_subscenes(segments, mode="together", hold=2.0)
```

Key points:

- `SubScene.build` is a **deferred** builder (a callable returning the
  mobject), so in `sequential` mode only one segment's mobjects exist on
  screen at a time — never build all the mobjects up front and add them.
- `mode="sequential"` fades each in, holds its own `sub.hold`, fades it out,
  then the next. Pass `keep_last=True` to leave the final segment on screen
  (it's returned so you can keep animating it).
- `mode="together"` fades every segment in at once, holds `hold` seconds, then
  fades them out together (unless `fade_out=False`, which returns the mobjects
  for further animation). Centers come from `default_anchors(n)` (1→center,
  2→left/right, 3–4→quadrants, 5–6→two rows), or from explicit `positions=`
  / each `SubScene.position`. This is the programmatic form of the Rule 4
  quadrant layout — for four labelled cases, prefer this over hand-placing.
- `self.play_subscenes(...)` exists on both lesson base classes
  (`RollingLessonScene`, `RodLessonScene`); for a `SpaceScene` (Rule 10) call
  the module function `play_subscenes(self, segments, mode=...)` directly,
  since it isn't inherited there. Either way it auto-logs each segment through
  the Rule 14 `log_event` hook when the scene has one.

See `tests/test_subscenes.py` for the exact fade/hold ordering each mode
guarantees.

## 17. 3D scenes and the 2D→3D transform

The lesson base classes (`RollingLessonScene`, `RodLessonScene`) extend
`MovingCameraScene`, which is 2D-only — its `zoom_to`/`zoom_out` drive a flat
camera frame. 3D needs manim's separate `ThreeDScene` camera, so a 3D scene
uses `ThreeDLessonScene` from `physics_through_anim.threed` — the same
"special base class" relationship a `SpaceScene` (Rule 10) has to the 2D base
classes. Reach for 3D only when the physics is genuinely 3D (fields, a
gyroscope's precession, orbital mechanics, a surface/wavefront) — a flat FBD
or a rolling wheel must stay 2D; a tilted camera on inherently-2D content just
makes vectors harder to read (Rules 2, 5).

### New 3D scene

```python
from manim import BLUE, Circle, Sphere, Text, Write
from physics_through_anim.threed import ThreeDLessonScene, lift_to_3d, physics_axes_3d


class FieldScene(ThreeDLessonScene):
    LESSON_NAME = "em_fields"  # transcript still lands under media/logs/<lesson>/ (Rule 14)

    def construct(self) -> None:
        self.add_narration()          # narration hook, same as the 2D bases
        title = Text("Field of a charge", font_size=30, weight="BOLD").to_edge(UP)
        self.hud(title)               # PIN captions/titles to the screen (see below)
        self.standard_view()          # raised isometric look (phi=70, theta=-45)
        self.add(physics_axes_3d())
        # ... build Sphere/Arrow3D/Surface, etc.
        self.orbit(rate=0.2)          # slow ambient camera rotation
        self.wait(3)
        self.stop_orbit()
```

`ThreeDLessonScene` gives you: `add_narration()` and `SceneEventLogMixin`
logging (Rule 14) for free; `standard_view(phi, theta)` / `top_down_view()`;
`orbit(rate)` / `stop_orbit()`; `hud(*mobs)`; and `self.play_subscenes(...)`
(Rule 16). `phi` is the polar angle from +z (0 = straight top-down,
~70° = isometric); `theta` is the azimuth.

### The 2D→3D transform

To *start flat and gain depth* (the "extrude / lift into 3D" move), begin in a
top-down view so the scene reads as 2D, draw the flat shape, then call
`lift_to_3d(scene, flat_mob, solid_mob)` — it tilts the camera up to the
isometric view **and** `ReplacementTransform`s the flat mobject into its solid
counterpart in one motion, so the shape visibly acquires depth as the
viewpoint rises:

```python
self.top_down_view()                 # phi=0 -> looks 2D
flat = Circle(color=BLUE)
self.play(Write(flat))
solid = lift_to_3d(self, flat, Sphere(radius=1.0))   # camera tilts + circle -> sphere
```

### 3D gotchas

- **Pin all text with `self.hud(...)`** (a `ThreeDScene.add_fixed_in_frame_
  mobjects` wrapper). A title or caption added normally is placed *in the 3D
  world* and tilts/rotates with the camera, becoming unreadable. The bottom-
  band text rule (Rule 9) still applies — the text just also needs this call.
- **A 3D scene will not inherit the 2D lesson helpers** (`rough_ground`,
  `force_arrow`, `wheel_setup`, `zoom_to`, …). Those are 2D constructs; use
  `ThreeDAxes`, `Surface`, `Sphere`, `Arrow3D`, `Line3D`, `Prism`, `Cube`,
  `Cylinder`, `Dot3D` and build the lesson's own 3D helpers in its `common.py`.
- **Register a 3D scene in `lessons.toml` exactly like any other** (Rule 11) —
  `render-lesson`/`stitch-lesson` and the per-lesson `media/videos/<lesson>/`
  grouping (Rule 13.1) work unchanged; nothing about 3D touches `render.py`.

See `tests/test_threed.py` for the camera-move / transform contract
`lift_to_3d` guarantees.

## 18. Narration and video must stay in sync — never end the video before the voice-over

The TTS voice-over (generated from `narration/sNN_*.md`) is usually **longer**
than a scene's animated timeline. If the animations finish first, the rendered
clip ends while the narrator is still talking — narration playing over nothing,
or (worse) the tail of the voice-over truncated at stitch time. Both are wrong:
audio and video must end together.

Two things are required of every narrated scene:

1. **Hold the final frame until the narration finishes.** Make
   `self.finish_with_narration()` the **last line** of `construct()`. It reads
   the active narration WAV's length, compares it to `self.time` (manim's
   accumulated rendered time), and waits exactly long enough that the video
   reaches `narration_length + a short tail` — or a small floor hold when
   narration is off. This alone guarantees the video is never shorter than the
   audio. Lives in `physics_through_anim.narration`; the method is on every
   lesson base class (`RollingLessonScene`, `RodLessonScene`,
   `ThreeDLessonScene`). A `SpaceScene` (Rule 10) must call the module function
   `hold_for_narration(self)` directly, since it isn't inherited there.

2. **Pace the visuals to span the narration — don't rely on one giant frozen
   hold at the end.** `finish_with_narration()` makes audio/video *end*
   together, but if the animations only take 25 s against a 70 s voice-over,
   you get 45 s of a frozen final frame while the narrator keeps talking —
   technically "in sync" but a dead scene. Fix the imbalance at the source:
   slow the key animations' `run_time` (a graph dot or vector that climbs over
   8–12 s reads far better than a 2 s snap and fills the narration naturally),
   and/or trim the narration `.md`. Aim for the animated timeline to reach
   within a few seconds of the narration length, so `finish_with_narration()`
   only adds a small tail (a handful of seconds on the takeaway frame is fine;
   30+ seconds of freeze is not).

**Reviewing for this (add to the Rule 12 checklist):** render the scene with
`--narration auto`, then compare durations —
`ffprobe -show_entries format=duration <clip>` vs the narration WAV under
`assets/audio/<lesson>/`. The clip must be `>=` the WAV, and the `pad_s` value
in the scene's `media/logs/<lesson>/` transcript (logged by the narration
hold) should be small (a few seconds), not tens of seconds. If `pad_s` is
large, the visuals are too short for the script — slow them down or trim the
narration, don't just accept the freeze. Discovered rebuilding
`s02_why_not_backward.py`.

