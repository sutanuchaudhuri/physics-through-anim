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
    problems/                  # (6) ORCHESTRATION — ProblemRef -> ScenePlan -> Recipe
    render/                    # (7) RENDERERS — specs -> Manim mobjects/scenes
  assets/                      # narration + generic visual scene helpers (NOT physics)
```

## The dependency rule (one way only)

```text
core  <-  kinematics  <-  shared  <-  domains  <-  recipes  <-  problems
                                         ^
                          overlays ------|------> depend on core + domains + shared
render depends on specs from any layer; NOTHING depends on render.
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
