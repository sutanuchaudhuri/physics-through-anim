# Spec-driven serialization: build scenes from JSON/XML

Every physics **spec** in this framework is a plain dataclass. The
`physics/serialization/` package round-trips those specs through JSON or XML and
turns them into live mechanics objects — so an `Assembly` (and therefore a scene)
can be **authored as configuration** and **reconstructed** from it. No Pydantic,
no schema duplication: the codec drives entirely off the dataclass field type
hints.

This is Milestone **M17** (problem orchestration); the same codec also serialises
the M18 presentation specs (`core/scene_data.py`) for free.

## Layers

```
JSON / XML text
   ⇅  serialization.codec         to_json/from_json, to_xml/from_xml (generic dataclass codec)
ProblemScenePlan                  problems/scene_plan.py  (EntitySpec, RelationSpec, ...)
   ⇅  serialization.assembly_io   plan_to_assembly / assembly_to_plan
Assembly (members + relations)    mechanics/assembly.py
   →  problems.adapters.plan_to_recipe → Recipe → (renderer) → Manim scene → video
```

- `mechanics/` never imports `serialization/`; the dependency points one way.
- Assets are rebuilt from their **constructor params**, so a spec is the authoring
  source of truth. Author absolute positions in the spec — placement sugar such as
  `Assembly.hang` is *not* reverse-engineered on export.

## 1. Generic codec — `serialization.codec`

Round-trips any spec dataclass (nested dataclasses, `Enum`s, tuples, lists, dicts,
and `X | None` fields all supported):

```python
from physics_through_anim.physics.problems.scene_plan import ProblemScenePlan
from physics_through_anim.physics.serialization import to_json, from_json, to_xml, from_xml

text = to_json(plan)                       # dataclass -> JSON text
plan = from_json(ProblemScenePlan, text)   # JSON text -> dataclass  (lossless)

xml  = to_xml(plan, root="plan")           # dataclass -> type-tagged XML text
plan = from_xml(ProblemScenePlan, xml)     # XML text  -> dataclass  (lossless)
```

XML leaves carry a `type` attribute (`int`/`float`/`str`/`bool`/`null`/`list`/`dict`)
so numbers and strings survive the round-trip faithfully.

## 2. Asset registry — `serialization.assets`

Maps a stable `kind` string to a mechanics class and back:

```python
from physics_through_anim.physics.problems.scene_plan import EntitySpec
from physics_through_anim.physics.serialization import build_entity, entity_spec_of

disk = build_entity(EntitySpec(kind="disk", name="d",
                               params={"position": [0.0, 1.0], "radius": 0.5}))
spec = entity_spec_of(disk)   # -> EntitySpec(kind="disk", name="d", params={...})
```

Registered kinds live in `ASSET_BUILDERS` (`block`, `disk`, `ring`, `hoop`,
`sphere`, `cylinder`, `pulley`, `ceiling`, `incline`, `floor`, `rope`, `cable`).
Add an entry there (and to `CANONICAL_KIND` for export) to register more assets.
Non-serialisable fields (e.g. a Manim `skin` mobject) are dropped from an export.

## 3. Assembly ⇄ plan — `serialization.assembly_io`

```python
from physics_through_anim.physics.serialization import plan_to_assembly, assembly_to_plan

assembly = plan_to_assembly(plan)   # config -> wired scene graph
plan     = assembly_to_plan(assembly)   # built scene -> serialisable plan
```

`plan_to_assembly`:

1. builds every `EntitySpec` into an asset;
2. `add`s bodies/supports first, then `connect`s connectors (ropes) so their
   endpoints resolve by name (`"anchor.bottom" -> "load.top"`);
3. re-declares explicit constraints/contacts from each `RelationSpec`
   (`RelationKind` → constraint class; `touch` → `Contact`).

## 4. A full JSON scene

```json
{
  "entities": [
    {"kind": "ceiling", "name": "ceiling", "params": {"y": 3.2, "half_width": 4.5}},
    {"kind": "pulley",  "name": "pulley",  "params": {"center": [0.0, 2.0], "radius": 0.7}},
    {"kind": "block",   "name": "m_1",     "params": {"position": [-0.5, 0.4], "width": 0.8}},
    {"kind": "rope",    "name": "rope_a",  "params": {"from_ref": "pulley.left", "to_ref": "m_1.top"}}
  ],
  "relations": [
    {"kind": "rolling", "participants": ["m_1", "ceiling"], "params": {"radius": 0.7, "name": "roll1"}}
  ]
}
```

```python
from physics_through_anim.physics.serialization import from_json, plan_to_assembly
from physics_through_anim.physics.problems.adapters import plan_to_recipe

plan     = from_json(ProblemScenePlan, open("scene.json").read())
assembly = plan_to_assembly(plan)     # or: recipe = plan_to_recipe(plan)
```

## Tests

- `tests/test_serialization.py` — JSON/XML lossless round-trip, `build_entity` ⇄
  `entity_spec_of`, `plan_to_assembly` (members + constraints + connector wiring),
  `assembly_to_plan` export + rebuild.
- `tests/test_m17_problems.py` — `plan_to_recipe` builds an `Assembly` from a plan.

## Scope / caveats

- Geometry is authored, not snapshotted: a body shifted at runtime (or a pulley
  placed via `hang`) exports its **constructor** position, not its current one.
  For full runtime-state capture, use the M6 `StateSnapshot`/trajectory layer.
- `assembly_to_plan` only exports assets registered in `CANONICAL_KIND`.

## 5. Live state snapshots — `serialization.state_io`

Where a plan captures *authoring* params, a **snapshot** captures the *current*
world geometry (live keypoints + applied rotation) after placement/animation:

```python
from physics_through_anim.physics.serialization import snapshot_assembly, to_json

snap = snapshot_assembly(assembly, t=1.5)   # AssemblySnapshot(t, assets=[AssetSnapshot, ...])
text = to_json(snap)                         # serialisable like any spec
```

`AssetSnapshot` holds `name`, `kind` (class name), `angle`, and
`keypoints: {name: (x, y)}` in world coordinates. Snapshots are what the
non-Manim renderers draw.

## 6. Timeline blocks — `steps`

`ProblemScenePlan.steps` is an ordered list of typed `StepSpec` blocks a renderer
executes in turn. `StepKind` distinguishes the three block types:

| `StepKind` | meaning |
| --- | --- |
| `INITIALIZE` | build/seat entities, set the opening state |
| `TIMESTEP` | advance the scene by `dt` (physics step / interpolate) |
| `SCENE_CHANGE` | toggle relations, swap a view, or run a transition |

```json
"steps": [
  {"kind": "initialize",   "at": 0.0, "label": "seat bodies"},
  {"kind": "timestep",     "at": 0.0, "dt": 0.5, "label": "advance"},
  {"kind": "scene_change", "at": 2.0, "params": {"deactivate": ["roll"]}}
]
```

### Transform/vector-driven animation

A `timestep` block carries `transforms` — per-entity **motion vectors** the `manim`
engine plays (translate by a vector, or rotate by `rotate_deg` about a pivot
keypoint). Rotation carries the body along its arc about `about`:

```json
{"kind": "timestep", "at": 0.0, "dt": 1.5, "label": "rotate about the hinge",
 "transforms": [{"target": "cyl", "rotate_deg": -80, "about": "corner.E"}]}
```

When a plan has transforms, `render-plan --renderer manim` writes an **mp4**
(playing the timeline); otherwise it writes a still `.png`. The `svg` engine stays
a static snapshot. See [examples/plans/cylinder_pivot_anim.json](../examples/plans/cylinder_pivot_anim.json)
(a cylinder rotates about the table corner, then free-falls). The validator checks
each transform's `target`, `about` pivot ref, and that it has a translate or rotate.

## 7. Render engines — `physics/rendering/` and the `render-plan` CLI

One plan, many back-ends behind a common `Renderer` interface
(`render(plan, output) -> Path`), registered by name:

| engine | kind | status |
| --- | --- | --- |
| `manim` | video | **working** — renders a styled still frame (`.png`) |
| `svg` | snapshot | **working**, dependency-free (real "plan -> picture") |
| `matplotlib` | snapshot | scaffold (needs the `viz` extra) |
| `plotly` | snapshot | scaffold (needs the `viz` extra) |
| `pymunk` | snapshot | scaffold |

```python
from physics_through_anim.physics.rendering import render_plan_file, available_renderers
available_renderers()                       # ['manim', 'matplotlib', 'plotly', 'pymunk', 'svg']
render_plan_file("scene.xml", renderer="svg", output="scene.svg")
```

From the CLI (renders straight from a JSON/XML plan):

```bash
python main.py render-plan scene.json --renderer svg --output scene.svg
python main.py render-plan scene.xml  --renderer manim   # prints the scaffold notice
```

The `svg` engine builds the assembly, freezes a snapshot, and draws blocks as
rectangles, round bodies as circles, and every rope/relation as a line — proving
a JSON/XML plan becomes a real viewable image without Manim. Add a new engine by
subclassing `Renderer` and decorating it with `@register`.

## 8. Validation — `serialization.validation`

Before a plan is built or rendered it is validated **deterministically**:
`validate_plan(plan) -> list[PlanError]` returns an ordered list of
`PlanError(path, message)` (empty == valid) — it never crashes on bad content.

```python
from physics_through_anim.physics.serialization import validate_plan
for err in validate_plan(plan):
    print(err)   # e.g. "entities[1].params.width: expected a number, got str"
```

Checks include: unknown entity `kind`; missing/duplicate entity `name`; unknown
or wrongly-typed params (against each asset's constructor type hints); constructor
failures; unknown relation `kind`; relations needing ≥2 participants; dangling
participant names; connector `from_ref`/`to_ref` pointing at an unknown asset or a
non-existent keypoint; and step `kind`/`at`/`dt` values.

From the CLI (and `render-plan` refuses to render an invalid plan):

```bash
python main.py validate-plan scene.json      # lists every error, exit 1 if any
make validate-plan PLAN=scene.json
```

The plan loader parses **leniently** (`from_json(..., strict=False)`) so an invalid
enum value is preserved for the validator to report by path rather than crashing
the parse; programmatic `from_json`/`from_xml` remain strict by default.

## 9. Per-entity styling — `StyleSpec`

Each `EntitySpec` carries an optional `style` honoured by **both** renderers
(resolved once in `rendering/style.py`):

```json
{"kind": "disk", "name": "ghost", "params": {"radius": 0.5},
 "style": {"display": "fade", "fill": "hashed", "show_corners": true, "corner_labels": true}}
```

- `display`: `solid` | `fade` (low opacity) | `dotted` | `dashed`.
- `fill`: `solid` | `hashed` (diagonal hatch) | `none`.
- `opacity`: explicit `0..1` override.
- `show_corners` / `corner_labels`: mark a polygon body's corners (or a rope/rod's
  ends) with dots and optional labels.
- `end_dots`: dot a spring/rope/rod's end points.

The schema validator checks `display`/`fill` options and the `opacity` range
(`entities[i].style.*`). The `manim` engine applies the same styles to its
mobjects and renders a still frame; `svg` maps them to stroke/fill/dash attributes.


