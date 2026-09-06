# M1.5 — Test Plan & TDD Execution

Milestone **M1.5** (Pose2D + local keypoints, RigidBody2D, typed refs, loads).
Plan: [M01_5_pose_rigidbody.md](M01_5_pose_rigidbody.md) · Jira epic **PAC-1** /
story **PAC-2**.

This milestone is built **test-first**. The acceptance criteria below are already
encoded as executable tests in
[`tests/test_m1_5_pose_rigidbody.py`](../../tests/test_m1_5_pose_rigidbody.py).
Behavioural tests are marked `xfail` so the shipped suite stays green; you make
them pass one at a time and drop the marker as each is implemented.

## Scaffolded modules (stubs to fill in)

| Module | Type | Method(s) to implement |
| --- | --- | --- |
| `physics/core/pose.py` | `Pose2D` | `world_point`, `world_vector`, `compose` |
| `physics/core/refs.py` | `AssetRef`/`PointRef`/`SurfaceRef`/`QuantityRef` | `parse` |
| `physics/core/loads.py` | `LoadSpec`/`ForceSpec`/`TorqueSpec`/`ImpulseSpec`/`DistributedLoadSpec`, enums | `arrow_length` |
| `physics/mechanics/massprops.py` | `MassProperties` | `inertia_about` |
| `physics/mechanics/rigidbody.py` | `RigidBody2D`, `BodyState2D` | `set_pose`, `keypoint`, `point_position`, `point_velocity`, `point_acceleration`, `inertia_about` |

## Acceptance criteria → tests

### Structural (green now — guard the public shape)

| # | Criterion | Test |
| --- | --- | --- |
| S1 | `VectorScalePolicy` = {fixed, proportional, normalized, clipped} | `test_vector_scale_policy_members` |
| S2 | `InteractionKind` unifies WEIGHT→GRAVITY and has the 8 kinds | `test_interaction_kind_unifies_gravity` |
| S3 | Dataclass defaults (`Pose2D`, `MassProperties`) | `test_dataclass_defaults` |
| S4 | `ForceSpec.value` is separate from arrow length; is a `LoadSpec` | `test_forcespec_value_is_separate_from_length` |
| S5 | `DistributedLoadSpec` defaults (`direction="normal"`) | `test_distributed_load_spec_fields` |

### Behavioural (RED until implemented — `xfail`)

| # | Criterion (from the plan) | Test |
| --- | --- | --- |
| B1 | `Pose2D.world_point`: local (1,0) rotated 90° about (2,0) → (2,1) | `test_pose_world_point_rotates_then_translates` |
| B2 | `world_vector` rotates only (no translation) | `test_pose_world_vector_ignores_translation` |
| B3 | `compose`: parent ∘ child places child origin in parent frame | `test_pose_compose_parent_child` |
| B4 | `set_pose` is **absolute** — two `set_pose(θ)` leave θ, not 2θ (anti-drift) | `test_set_pose_is_absolute_no_drift` |
| B5 | `keypoint()` returns world coords under the current pose | `test_keypoint_returns_world_coords` |
| B6 | `refs.parse("disk.P")` → `PointRef`; `str()` round-trips | `test_refs_parse_roundtrips` |
| B7 | `MassProperties.inertia_about` = `I_cm + m·r²` (parallel axis) | `test_massprops_parallel_axis` |
| B8 | `point_velocity` ⟂ (P−CM) for pure rotation; \|v\|=ωR | `test_point_velocity_perpendicular_for_pure_rotation` |
| B9 | `point_velocity` = `v_G + ω×r` for combined motion | `test_point_velocity_combined_motion` |
| B10 | `arrow_length(value, FIXED)` ignores `value` (physics ≠ length) | `test_arrow_length_fixed_ignores_value` |

> Not yet scaffolded (needs the `base.py` refactor): *"Block re-parented on
> `RigidBody2D` still passes all 8 M1 tests"* and the `ForceSpec` back-compat
> `magnitude=` shim. Add those tests when the M1 `PhysicsAsset` internals are
> migrated to `Pose2D` + local keypoints (kept out of this scaffold so shipped
> M1 code is untouched).

## How to execute (red → green loop)

```bash
# 1. See the real failures (force xfail specs to run as normal tests):
uv run pytest tests/test_m1_5_pose_rigidbody.py --runxfail -q

# 2. Implement one method (e.g. Pose2D.world_point), then re-run just it:
uv run pytest tests/test_m1_5_pose_rigidbody.py::test_pose_world_point_rotates_then_translates --runxfail -q

# 3. When it passes with --runxfail, delete that test's @TDD (xfail) marker so
#    it becomes a normal green test. Repeat B1..B10.

# 4. Whole suite stays green throughout (xfail specs don't fail the build):
uv run pytest -q          # 19 M1 + 5 structural pass, 10 xfail
uv run ruff check .
```

`--runxfail` is the key flag: without it, an unimplemented spec is reported as
`xfail` (expected); with it, pytest runs the spec for real so you see the actual
`NotImplementedError`/assertion — that is your TDD "red".
