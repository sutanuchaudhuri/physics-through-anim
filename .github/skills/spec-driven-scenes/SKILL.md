---
name: spec-driven-scenes
description: 'Spec-driven authoring of physics scenes as JSON/XML data (a ProblemScenePlan) rendered by pluggable engines (SVG and Manim) in physics-through-anim. Use when creating or editing a JSON/XML scene plan under examples/plans/**, adding entities/relations/vectors/markers/paths/masks/steps to a plan, choosing or writing a render engine (svg vs manim), adding a new cosmetic mask kind (helix/spring, chain, hopper, belt, sand, plume, rocket, box, ellipse) to BOTH the SVG and Manim mask libraries, seating a body on a surface so N/f anchor at the true contact point, showing time-stepped ghost strobes of a moving body, scaffolding a starter plan, batch-rendering a folder of plans, validating a plan, or wiring new CLI/make targets for the plan workflow. Covers the ProblemScenePlan spec dataclasses (EntitySpec/RelationSpec/VectorSpec/MarkerSpec/PathSpec/MaskSpec/StepSpec/TransformSpec/StyleSpec/PlacementSpec/LabelSpec), the serialization layer (codec, asset registry, assembly_io, state_io, deterministic validator), the rendering layer (base/svg_renderer/engines/style/masks/manim_masks/manim_style), the mask library with SVG+Manim parity, on-surface seating and contact keypoints, ghost/animation from steps, relative placement, the layering rule (mechanics never imports serialization/render/rendering), and the render-plan/validate-plan/render-gallery/new-plan/list-masks/list-assets/list-renderers CLI + make targets. Interlinks with the physics-animation-standards skill for vector colors, cosmetic skins, and asset-library construction.'
---

# Spec-Driven Scenes (JSON/XML → SVG + Manim)

A scene can be authored as **data** — a `ProblemScenePlan` in JSON or XML — and
rendered by a **pluggable engine** with no Python. This skill governs everything
under `examples/plans/**` and the `serialization/` + `rendering/` layers of
`src/physics_through_anim/physics/`.

> **Interlink:** this skill is the *data/rendering* counterpart of the
> [`physics-animation-standards`](../physics-animation-standards/SKILL.md) skill,
> which governs hand-built Manim lesson scenes under
> `src/physics_through_anim/lessons/**`. Where the two overlap (vector colours,
> cosmetic skins, asset-library construction), the standards skill is the source
> of truth and is cross-referenced below. Full reference:
> [docs/spec_driven_serialization.md](../../../docs/spec_driven_serialization.md),
> [plans/ARCHITECTURE.md](../../../plans/ARCHITECTURE.md) (§ Spec-driven scenes),
> [plans/DIAGRAMS.md](../../../plans/DIAGRAMS.md) (§ 1b, § 2c).

## 1. The plan is a bundle of typed, defaulted specs

`physics/problems/scene_plan.py` defines `ProblemScenePlan`. Every field is a
small dataclass with defaults, and the whole plan round-trips losslessly through
JSON **and** XML via the generic codec. Author only what the scene needs.

| Field | Spec | Authors |
| --- | --- | --- |
| `entities` | `EntitySpec(kind, name, params, style, place, label)` | Any registered asset (`make list-assets`) |
| `relations` | `RelationSpec(kind, participants, params)` | Physical links: `rolling`, `hang`, `rope`, `pin`, `axle`, `distance`, `touch`, … |
| `vectors` | `VectorSpec` (`core/scene_data.py`) | Arrows: `anchor`, `vector`, `role`, `show_label`, `placement` |
| `markers` | `MarkerSpec(at, point, label, color, show_label, placement)` | Highlighted points (contact, CM, pivot) |
| `paths` | `PathSpec(points, color, label, kind, height, samples)` | `polyline` or generated `parabola` arch |
| `masks` | `MaskSpec(kind, at, point, points, length, width, direction, color, opacity, coils)` | Cosmetic, physics-free overlays |
| `steps` | `StepSpec(kind, at, dt, transforms)` + `TransformSpec(target, translate, rotate_deg, about)` | A timeline → ghosts (SVG) / animation (Manim) |
| per entity | `StyleSpec(display, fill, opacity, show_corners, corner_labels, end_dots)` | Display/fill/opacity/corner marks |
| per node | `LabelSpec(show, placement, at, text)`, `LabelPlacement` | Label text/visibility/placement (plan default: `label_placement`) |
| per entity | `PlacementSpec(on, at, my, offset)` | Relative placement |

## 2. Always validate before you render

`validate_plan(plan)` (in `serialization/validation.py`) returns an **ordered
list of `PlanError`** and never raises on content. `render-plan` runs it first
and refuses to draw an invalid plan. After editing any plan, run:

```bash
make validate-plan PLAN=examples/plans/asset_demo/s16_spring_banks.json
# then render:
make render-plan PLAN=examples/plans/asset_demo/s16_spring_banks.json RENDERER=svg OUTPUT=/tmp/s16.svg
```

The validator checks entity kinds+params (via the asset ctor type hints and a
build attempt), relation kinds/participants, connector keypoint refs, marker/
vector/path anchors, mask kinds+anchors+opacity, step targets, and placements.

## 3. Two engines, one plan — keep SVG and Manim at parity

`make list-renderers`:

- **`svg`** — the working, dependency-free snapshot engine
  (`rendering/svg_renderer.py`). Draws masks (bottom layer), relations, assets,
  ghosts, paths, vectors, markers, and styling. Use it for fast iteration and
  the committed gallery SVGs.
- **`manim`** — the prime engine (`rendering/engines.py::ManimRenderer`). Renders
  a **styled still PNG**, or an **MP4** when the plan has animated `steps`. It
  draws the same mask library.
- `matplotlib` / `plotly` / `pymunk` are scaffolds (`viz` extra for the first two).

**Rule:** any renderer-visible feature must behave the same in both real engines.
When you add a mask you MUST register it in **both** `masks.py` *and*
`manim_masks.py` (see § 4).

## 4. The mask library (cosmetic, physics-free) — register in BOTH renderers

Masks are pure decoration: transparent by default, drawn on the bottom layer,
carrying no physics. They are the spec-driven form of the "cosmetic skin over a
point/rigid model" idea in the standards skill (Rule 19,
`plans/asset_library/RENDER_MASK.md`). `make list-masks` prints the live set:

`plume`/`flame`/`exhaust`, `rocket`/`body`, `ellipse`/`blob`, `box`/`rect`,
`chain`, `spring`/`helix`/`coil`, `hopper`/`funnel`, `belt`/`conveyor_belt`,
`sand`/`grains`.

To add a new mask kind, add **two** builders (parity is mandatory):

```python
# rendering/masks.py  (SVG: draw with xml.etree SubElement + to_px)
@register_mask("myshape")
def _myshape(svg, spec, anchor, to_px) -> None: ...

# rendering/manim_masks.py  (Manim: return a VMobject in WORLD coords)
@register_manim_mask("myshape")
def _myshape(spec, anchor) -> VMobject: ...
```

Conventions for masks:
- Transparent — honour `spec.opacity` from the JSON; don't hard-code alpha.
- Anchor by `at` (an `asset.keypoint`), an explicit `point`, or a `points` list.
- **Massless bodies are masks, not entities.** A spring/chain is anchored to two
  key points whose separation may change and has **no CM** unless specified.
  A hopper/belt/sand scene can be entirely cosmetic masks plus one real particle.
- Add a render test in `tests/test_rendering.py` asserting the shape + its
  transparency, and validate one example plan that uses it.

## 5. Seat on-surface bodies so N/f anchor at the true contact point

Prefer the constraint over coordinates. `place: {on: <support>}` seats a body to
tangency and creates a real `contact` keypoint; anchor `normal`/`friction`
vectors and a contact marker there (mirrors the standards skill's "place with the
constraint, not coordinates"):

```json
{"kind": "disk", "name": "m", "params": {"radius": 0.5}, "place": {"on": "ramp"}}
```
```json
{"anchor": "m.contact", "vector": [-0.47, 0.88], "role": "normal", "label": "N"}
```

`Floor`, `Wall`/`Incline`, `Conveyor` (a `Floor`), and `Table` are seatable.
Relative placement without a support: snap `my` keypoint to another node's `at`
plus an `offset` — never hand-author absolute coordinates when a keypoint exists.

## 6. Motion = `steps`; ghosts (SVG) and animation (Manim) come free

A `StepSpec` timeline of `translate`/`rotate` `transforms` on a target entity is
rendered as a **faded ghost strobe** in SVG (`_resolve_ghosts` accumulates the
transforms) and as an **MP4 animation** in Manim. For a physical strobe (e.g. a
projectile), keep `dt` constant and let the per-step deltas encode the physics
(constant `dx`, linearly-shrinking `dy` = gravity). Label time steps with
markers; a `parabola` path can trace the same arc so ghosts land on it.

## 7. Vector roles reuse the standards colour palette

`VectorSpec.role` maps to a colour so a viewer can tell force from kinematics at
a glance — the **same distinction** the standards skill mandates (Rule 2:
FBD vs kinematic vectors never share a colour family). Roles: `weight`,
`normal`, `friction`, `force`, `tension`, `velocity`, `acceleration`, `angular`,
`momentum`, `position`, `radius`. Use the role; don't invent per-scene colours.

## 8. CLI + make workflow

`make help` lists all targets. The spec-driven ones:

| Command | Purpose |
| --- | --- |
| `make new-plan OUT=<f> MASK= KIND=` | Scaffold a valid starter plan (floor + body + one mask) |
| `make validate-plan PLAN=<f>` | List every key/value error (render refuses on error) |
| `make render-plan PLAN=<f> RENDERER=svg OUTPUT=` | Render one plan via an engine |
| `make render-gallery DIR=<folder>` | Batch-render every plan in a folder to SVG |
| `make list-renderers` / `list-masks` / `list-assets` | Introspect the live registries |

Regenerate the committed gallery after mask/engine changes:

```bash
make render-gallery DIR=examples/plans/asset_demo OUTPUT_DIR=examples/plans/asset_demo/svg
```

## 9. Layering rule (do not break)

`mechanics/` must **never** import `serialization/`, `render/`, or `rendering/`.
Canonical enums (`Bearing`, `Keypoint`, `RelationKind`, …) live in `mechanics/`;
`render.tokens` re-exports them. `serialization/` depends on `problems/` +
domains; `rendering/` depends on `serialization/` + `problems/`. Keep ruff
line-length 100 and one `StrEnum` per concept.

## 10. Review checklist for a spec-driven scene

1. `make validate-plan PLAN=…` → **no errors**.
2. `make render-plan … RENDERER=svg` and view the SVG (rasterise with
   `qlmanage -t -s 900 -o /tmp <file>.svg`) — labels don't overlap (use
   `placement`), masks are transparent, seated bodies rest exactly on the surface.
3. If it animates, `make render-plan … RENDERER=manim` and confirm the MP4.
4. New mask kind → registered in **both** `masks.py` and `manim_masks.py`, with a
   render test; new entity kind appears in `make list-assets`.
5. `make check` (ruff + full suite) is green; regenerate gallery SVGs if a shared
   renderer/mask changed.

## 11. Updating this skill

When you add a spec field, mask kind, entity kind, engine, or CLI/make target,
update the relevant table here **and** the mirror in
[plans/ARCHITECTURE.md](../../../plans/ARCHITECTURE.md) and the README's
"Spec-driven scenes" section. If the change also affects hand-built lessons
(colours, skins, asset construction), reconcile it with the
[`physics-animation-standards`](../physics-animation-standards/SKILL.md) skill so
the two never contradict.
