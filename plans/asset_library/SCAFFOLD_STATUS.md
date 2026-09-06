# Asset Library — Scaffold Status & How to Test (M1–M18)

TDD scaffold for the whole mechanics asset library. Every milestone has stub
modules under `src/physics_through_anim/physics/` and an executable spec under
`tests/`. Behavioural specs are `xfail` (RED until implemented) so the shipped
suite stays **green**; structural specs pass now and guard the public shape.

Current state: **50 passed, 38 xfailed** (`uv run pytest -q`). M1 is shipped; M1.5
onward are scaffolds awaiting implementation. Design lives in each milestone's
plan doc; namespace/layering in [ARCHITECTURE.md](ARCHITECTURE.md); Jira project
**PAC** tracks status.

## What is done, per milestone

| Milestone | Modules (`physics/…`) | Spec file (`tests/…`) | Status |
| --- | --- | --- | --- |
| **M1** | `mechanics/{kinds,palette,base,fbd,bodies,supports,assembly}` | `test_assets_mechanics.py` | **SHIPPED** (19 pass) |
| **M1.5** | `core/{pose,refs,loads}`, `mechanics/{massprops,rigidbody}` | `test_m1_5_pose_rigidbody.py` | scaffold |
| **M1.6** | `core/{transforms,frames,state}`, `kinematics/{rigid_body,rolling,bindings}` | `test_m1_6_kinematics.py` | scaffold |
| **M2** | `mechanics/{surfaces,contact,environment}` | `test_m02_supports_contact.py` | scaffold |
| **M3** | `mechanics/{circular,motion}` | `test_m03_rolling.py` | scaffold |
| **M4** | `mechanics/{connectors,constraints}` | `test_m04_connectors.py` | scaffold |
| **M5** | `mechanics/rod` | `test_m05_rod.py` | scaffold |
| **M6** | `core/{trajectory,state}` | `test_m06_state_trajectory.py` | scaffold |
| **M7** | `core/events` | `test_m07_events.py` | scaffold |
| **M8** | `mechanics/surfaces_curved` | `test_m08_curved_surfaces.py` | scaffold |
| **M9** | `overlays/{graphs,kinematics,forces}` | `test_m09_overlays.py` | scaffold |
| **M10** | `mechanics/springs` | `test_m10_springs.py` | scaffold |
| **M11** | `mechanics/chain` | `test_m11_chain.py` | scaffold |
| **M12** | `core/impact`, `overlays/events` | `test_m12_collisions.py` | scaffold |
| **M13** | `mechanics/orbital` | `test_m13_orbital.py` | scaffold |
| **M14** | `mechanics/reference_frames` | `test_m14_frames.py` | scaffold |
| **M15** | `recipes/base` | `test_m15_recipes.py` | scaffold |
| **M16** | `mechanics3d/bodies3d` | `test_m16_threed.py` | scaffold |
| **M17** | `problems/{refs,scene_plan,adapters}` | `test_m17_problems.py` | scaffold |
| **M18** | `core/scene_data`, `overlays/views` | `test_m18_presentation.py` | scaffold |

Each scaffold module: pure-data declarations (dataclasses, `StrEnum`s, defaults)
are **implemented**; every method with real logic raises `NotImplementedError`
with a `"M.. name"` tag. Full class lists per milestone are in the plan docs; the
scaffold covers each milestone's headline surface. Where a milestone extends a
shipped M1 file (e.g. new supports → `supports.py`, `RigidBody2D` → `bodies.py`),
the scaffold uses a **new** module (`environment.py`, `rigidbody.py`, …) and notes
the merge in its docstring, so shipped M1 code is untouched.

Out of scope here: fluids **F1–F6** (sibling domain) — scaffold separately.

## How to run / test

```bash
# Whole suite — stays green (structural passes + xfail specs):
uv run pytest -q                         # -> 50 passed, 38 xfailed
uv run ruff check .                      # scaffold is lint-clean

# One milestone's specs, forced to run for real (the TDD "red"):
uv run pytest tests/test_m03_rolling.py --runxfail -q

# One acceptance criterion while implementing it:
uv run pytest tests/test_m10_springs.py::test_hooke_law_force --runxfail -q
```

## TDD workflow (per milestone, red → green)

1. Pick a milestone; open its spec file and its plan doc.
2. `uv run pytest tests/test_mNN_*.py --runxfail -q` → see the real
   `NotImplementedError`s (RED).
3. Implement the stubbed method(s) in the matching `physics/…` module.
4. Re-run with `--runxfail` until that test passes; then **delete its `@TDD`
   (xfail) marker** so it becomes a normal green test.
5. When a milestone's specs all pass, run `uv run pytest -q` + `uv run ruff
   check .` — the milestone's xfails have become passes and the suite is still
   green. Update the Jira story/subtasks to Done.

`--runxfail` is the key flag: without it an unimplemented spec is reported as
`xfail` (expected, build stays green); with it, pytest runs the spec for real so
you see the failure to drive against.

## Recommended implementation order

Follow the dependency graph (see [DIAGRAMS.md](DIAGRAMS.md) §2b):
`M1.5 → M1.6 → {M2, M6} → M7 → {M3, M8, M9} → {M4, M10, M11, M12, M13, M14} →
M15 → {M16, M17, M18}`. Start with `physics/core` (pose/refs/loads/transforms/
state) since almost everything depends on it.
