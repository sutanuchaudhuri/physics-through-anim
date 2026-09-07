# Architecture & Namespace — Physics Framework

How the physics modeling + rendering framework is organized so it can grow from
mechanics today to **optics, electromagnetism, acoustics, thermodynamics, and
modern physics** tomorrow — while letting those domains share and reuse assets
without tangling into each other.

Package root: `src/physics_through_anim/physics/`
Import root: `physics_through_anim.physics`

> Note: this replaces the earlier `physics_through_anim.assets.physics.*`
> namespace. The physics framework is now a top-level package, separate from
> `assets/` (which holds only narration/visual scene helpers).

## Layered namespace

```text
physics_through_anim/
  physics/                     # the physics modeling + rendering framework
    core/                      # (1) FOUNDATION — domain-neutral, no physics domain
                               #     geometry (pose, transforms, frames, vectors),
                               #     state/trajectory/timeline/events/signals/refs,
                               #     load specs, presentation contract, base palette
    kinematics/                # (1) FOUNDATION — generic rigid-body/point kinematics
                               #     + pose/attachment/path animation bindings
    shared/                    # (2) CROSS-DOMAIN PRIMITIVES — reused by 2+ domains
      waves/                   #     wavefronts, rays, standing/travelling waves
      fields/                  #     scalar/vector fields, field lines, flux
      oscillations/            #     SHM, driven, damped, coupled oscillators
      particles/               #     point particles, charges, wave packets
    mechanics/                 # (3) DOMAIN — bodies, supports, contacts, connectors  [M1 shipped]
    fluids/                    # (3) DOMAIN — regions, containers, pipes, control volumes
    optics/                    # (3) DOMAIN — sources, lenses, mirrors, rays
    electromagnetism/          # (3) DOMAIN — charges, currents, circuits, E/B fields
    acoustics/                 # (3) DOMAIN — sources, media, standing waves, resonance
    thermodynamics/            # (3) DOMAIN — gases, pistons, heat engines, PV/TS diagrams
    modern/                    # (3) DOMAIN — special relativity + quantum
    overlays/                  # (4) CROSS-DOMAIN UI — FBD, vectors, graphs, energy, field lines
    recipes/                   # (5) COMPOSITIONS — textbook setups returning a Recipe
    problems/                  # (6) ORCHESTRATION — ProblemRef -> ProblemScenePlan -> Recipe
    serialization/             # (7) SPEC I/O — plan <-> JSON/XML (codec), asset registry,
                               #     assembly_io, state snapshots, deterministic validator
    render/                    # (8) MANIM RENDERERS — specs -> Manim mobjects/scenes
    rendering/                 # (8) PLUGGABLE ENGINES — plan -> SVG/PNG/MP4 (svg, manim, ...),
                               #     styling, masks (+ manim masks), label placement
  assets/                      # narration + generic visual scene helpers (NOT physics)
```

## The dependency rule (one way only)

```text
core  <-  kinematics  <-  shared  <-  domains  <-  recipes  <-  problems
                                         ^
                          overlays ------|------> depend on core + domains + shared
render depends on specs from any layer; NOTHING depends on render.
serialization depends on problems + domains; rendering depends on serialization
+ problems. mechanics NEVER imports serialization, render, or rendering.
```

- A **domain never imports another domain.** Optics does not import
  electromagnetism; mechanics does not import fluids.
- **Cross-domain reuse flows through `shared/` (or `core/`).** If two domains
  need the same physics — e.g. optics *and* acoustics *and* EM all need waves —
  that primitive lives in `shared/waves`, not in whichever domain wrote it first.
- **Foundation layers know nothing about domains.** `core/` and `kinematics/`
  contain geometry and generic kinematics only; they never import a domain.
- **`problems/` is the only place that knows about a source corpus** (F=ma,
  Krotov, …); nothing imports `problems/`.

This is what keeps the framework scalable: adding *optics* is adding one leaf
package plus, at most, a new `shared/` primitive — never edits rippling across
existing domains.

## Why `shared/` exists (interlinked domains)

Physics domains overlap heavily, and a teaching video may combine them:

| Reused primitive | Lives in | Used by |
| --- | --- | --- |
| Waves / wavefronts / rays | `shared/waves` | optics, acoustics, electromagnetism, mechanics (wave-on-string) |
| Scalar/vector fields, field lines, flux | `shared/fields` | electromagnetism, gravity (mechanics), fluids, thermodynamics |
| Oscillators (SHM/driven/damped/coupled) | `shared/oscillations` | mechanics (SHM), acoustics, electromagnetism (LC/RLC) |
| Particles / charges / packets | `shared/particles` | mechanics, electromagnetism, modern |
| Pose, transforms, frames, state, trajectory | `core` | every domain |
| Rigid-body / point kinematics + bindings | `kinematics` | mechanics, fluids, optics (moving parts), any moving asset |

A scene that shows a charge oscillating and radiating an EM wave composes
`shared/particles` + `shared/oscillations` + `shared/waves` + `electromagnetism`
— each piece owned once, reused everywhere.

## Domain roadmap

| Domain | Package | Status |
| --- | --- | --- |
| Mechanics | `physics/mechanics` | M1 shipped; M1.5–M18 planned (see [asset_library/](asset_library/)) |
| Fluids | `physics/fluids` | Planned F1–F6 (see [fluids/](fluids/)) |
| Optics | `physics/optics` | Scaffolded (future) |
| Electromagnetism | `physics/electromagnetism` | Scaffolded (future) |
| Acoustics | `physics/acoustics` | Scaffolded (future) |
| Thermodynamics | `physics/thermodynamics` | Scaffolded (future) |
| Modern | `physics/modern` | Scaffolded (future) |

Scaffolded packages currently hold only a docstring `__init__.py`; they define
the namespace and are filled in as each domain is planned and implemented.

## Spec-driven scenes (M17)

A scene can be authored as **data** (JSON/XML) instead of Python and rendered by
a pluggable engine. This is the `serialization/` + `rendering/` layers.

### The plan and its specs

A `ProblemScenePlan` (`physics/problems/scene_plan.py`) is a bundle of small,
typed, defaulted dataclasses — each round-trips losslessly through the codec:

| Spec | Role |
| --- | --- |
| `EntitySpec` | One asset: `kind` + `params`, plus `style`, `place`, `label` |
| `RelationSpec` | A physical link (`RelationKind`): rolling, hang, rope, pin, axle, distance, touch, … |
| `VectorSpec` (`core/scene_data.py`) | An arrow: anchor keypoint, role colour, `show_label`, `placement` |
| `MarkerSpec` | A highlighted point (dot + optional label + `placement`) |
| `PathSpec` | A traced curve: `polyline`, or a generated `parabola` arch |
| `MaskSpec` | A cosmetic, physics-free overlay (see mask library below) |
| `StepSpec` + `TransformSpec` | A timeline block of `translate`/`rotate` transforms (ghosts/animation) |
| `StyleSpec` | Display mode, fill mode, opacity, corner/end dots |
| `LabelSpec` / `LabelPlacement` | Label text/visibility/placement (+ a plan-wide default) |
| `PlacementSpec` | Relative placement: `on` a support, or snap `my` keypoint to another `at` + `offset` |

### Layers

- **`serialization/`** — `codec.py` (generic dataclass ⇄ dict / JSON / XML from
  type hints), `assets.py` (kind → `PhysicsAsset` registry, auto-covering every
  drawable subclass; `build_entity`/`entity_spec_of`), `assembly_io.py`
  (`plan_to_assembly`/`assembly_to_plan` — seats bodies, wires connectors,
  re-declares relations), `state_io.py` (serialisable `AssemblySnapshot`), and
  `validation.py` (`validate_plan` → an ordered list of `PlanError`, never
  raising on content). `problems/adapters.plan_to_recipe` wraps the assembly.
- **`rendering/`** — `base.py` (the `Renderer` ABC + registry + `render_plan_file`),
  `svg_renderer.py` (dependency-free, real: masks, relations, assets, ghosts,
  paths, vectors, markers, styling), `engines.py` (`ManimRenderer` — a styled
  still PNG, or an MP4 when `steps` animate — plus scaffolded matplotlib/plotly/
  pymunk), `style.py`, `masks.py` (`MASK_BUILDERS`), `manim_masks.py`
  (`MANIM_MASK_BUILDERS`, parity so both engines draw masks), and `manim_style.py`.

### The mask library (cosmetic, physics-free)

Masks carry no physics — pure decoration, transparent by default, drawn on the
bottom layer, registered with `@register_mask` (SVG) and `@register_manim_mask`
(manim) so both engines agree. Kinds: `plume`/`flame`/`exhaust`, `rocket`,
`ellipse`/`blob`, `box`/`rect`, `chain` (interlocked links between key points),
`spring`/`helix`/`coil` (massless coil between two key ends whose separation may
change — no CM), `hopper`/`funnel`, `belt`/`conveyor_belt`, and `sand`/`grains`
(a "block of sand" clump). `make list-masks` prints the live set.

### Registered entity kinds

Beyond the M1 bodies, the asset registry auto-covers every drawable
`PhysicsAsset` — bodies (`block`, `disk`, `ring`, `hoop`, `sphere`, `cylinder`,
`particle`), supports (`floor`, `wall`, `incline`, `ceiling`, `table`, `edge`,
`peg`, `conveyor`, `pulley`, `central_body`), connectors (`rope`, `cable`, `rod`,
`linear_spring`), and joints (`hinge`, `pin_joint`). `make list-assets` prints
the live set; on-surface bodies seated with `place: {on: …}` gain a real
`contact` keypoint so N/f anchor at the true contact point.

## Conventions

- One StrEnum per concept (ruff UP042); every dataclass field has a default.
- Colours come only from `core` / domain palettes, never hard-coded in a scene.
- New primitives graduate into `shared/` **only when a second domain needs
  them** — until then keep them in the domain that introduced them.
- Each milestone ID (`M1`, `F1`, …) maps 1:1 to a Jira epic in project **PAC**
  (see [README.md](README.md)); Jira tracks status, these docs track design.

## Migration note

The shipped M1 mechanics package moved from
`physics_through_anim.assets.physics.mechanics` to
`physics_through_anim.physics.mechanics` (imports updated, 19 tests still pass).
The `physics/core/` extraction that milestones M1.5/M1.6 describe now lands in
this `physics/core/` package.
