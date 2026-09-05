# M1.5 — Pose2D + Local Keypoints, RigidBody2D, Typed Refs, Loads

Status: **DRAFT FOR REVIEW** (NEW — architecture review 2026-09-05)
Depends on: M1 (preserved). Files: `pose.py` (NEW), `refs.py` (NEW),
`massprops.py` (NEW), `loads.py` (NEW), `base.py` (refactor internals only),
`bodies.py` (introduce `RigidBody2D`). **M1's public API is kept** — this
milestone changes *internals* and adds new foundations before M2–M4 build on
them.

## Why this milestone exists (review points 3, 4, 20, 21, 33)

M1's model — world-coord keypoints mutated on every `shift()` — is perfect for a
static block but becomes fragile once translation + absolute rotation + rolling +
trajectories + parent assemblies + moving wedges + rotating frames coexist
(review 3). And `point_velocity` is a general rigid-body fact
(`v_P = v_G + ω × r_{P/G}`), not a circular-body feature (review 4). Fixing both
now is far cheaper than after M8–M15.

## `pose.py` (NEW) — canonical geometry + absolute pose

```python
Vec2 = tuple[float, float]

@dataclass(frozen=True)
class Pose2D:
    position: Vec2 = (0.0, 0.0)
    angle: float = 0.0                      # absolute orientation (rad)
    def world_point(self, local: Vec2) -> np.ndarray:
        c, s = cos(angle), sin(angle)
        x = position[0] + c*local[0] - s*local[1]
        y = position[1] + s*local[0] + c*local[1]
        return np.array([x, y, 0.0])
    def world_vector(self, local_vec: Vec2) -> np.ndarray:   # direction only (no translate)
        ...
    def compose(self, other: "Pose2D") -> "Pose2D":          # parent ∘ child (assemblies)
```

## `base.py` refactor (internals only — public contract unchanged)

```python
@dataclass
class PhysicsAsset:                         # RENDERABLE ENTITY ONLY (review 2)
    ...
    local_keypoints: dict[str, Vec2] = field(init=False)     # canonical, body frame
    pose: Pose2D = field(default=Pose2D())
    # PUBLIC contract preserved:
    def keypoint(self, key) -> np.ndarray:  # world coords, computed on demand
        return self.pose.world_point(self.local_keypoints[key])
    def set_local_keypoint(self, key, local): self.local_keypoints[key] = local
    def set_pose(self, pose: Pose2D):        # ABSOLUTE — rebuild mobject transform from canonical
        self.pose = pose; self._reapply_pose()
    def shift(self, delta):                  # now sugar over set_pose (absolute), not mutate-all
        self.set_pose(replace(self.pose, position=add(self.pose.position, delta)))
    def rotate_to(self, angle):              # absolute rotation, no accumulation
        self.set_pose(replace(self.pose, angle=angle))
    # BACK-COMPAT: set_keypoint(key, world_pt) still works -> stored as local via inverse pose.
```

> Key property (review 3): every transform is **absolute** — `set_pose` rebuilds
> from canonical geometry, so repeated updater calls (rolling, trajectories)
> never accumulate numerical/transform error.

## `refs.py` (NEW) — typed references (reviews 13, 19, 25)

```python
@dataclass(frozen=True)
class AssetRef:    name: str                      # "disk"
@dataclass(frozen=True)
class PointRef:    asset: str; key: str           # "disk.P"  (parse "a.k")
@dataclass(frozen=True)
class SurfaceRef:  asset: str; name: str          # "wedge.incline"
@dataclass(frozen=True)
class QuantityRef: path: str                      # "contact:disk.floor:N", "rope:1:tension"
# helpers: parse("disk.P") -> PointRef; str() round-trips (YAML-friendly).
```

## `massprops.py` (NEW) — review 4

```python
@dataclass(frozen=True)
class MassProperties:
    mass: float = 1.0
    inertia_cm: float = 0.0        # I about the CM (0 for a particle)
    def inertia_about(self, r_from_cm: Vec2) -> float:      # parallel axis
        return inertia_cm + mass * (r_from_cm[0]**2 + r_from_cm[1]**2)
```

## `loads.py` (NEW) — reviews 20, 21 (separate physics from arrow length)

```python
class VectorScalePolicy(StrEnum):
    FIXED = "fixed"; PROPORTIONAL = "proportional"; NORMALIZED = "normalized"; CLIPPED = "clipped"

@dataclass(frozen=True)
class LoadSpec:                     # base for anything the FBD/torque diagram draws
    at: PointRef | str
    label: str                     # symbolic only (Rule 9)
    source: str | None = None      # e.g. "contact:disk.floor" (provenance)

@dataclass(frozen=True)
class ForceSpec(LoadSpec):          # M1's ForceSpec, upgraded
    kind: InteractionKind = InteractionKind.APPLIED
    direction: Vec2 | str = "auto"
    value: QuantityRef | float | None = None   # PHYSICAL magnitude (N), NOT arrow length
    # arrow length is decided by the renderer's VectorScalePolicy, not this field.

@dataclass(frozen=True)
class TorqueSpec(LoadSpec):
    kind = InteractionKind.APPLIED; sense: int = +1     # +ccw / -cw
    value: QuantityRef | float | None = None
@dataclass(frozen=True)
class ImpulseSpec(LoadSpec):
    direction: Vec2 | str = "auto"; value: QuantityRef | float | None = None

@dataclass(frozen=True)
class DistributedLoadSpec(LoadSpec):        # springs & fluids review: hydrostatic/pressure loads
    over: SurfaceRef | str                  # boundary the load is distributed along
    intensity: QuantityRef | Callable       # w(s) per unit length (e.g. rho*g*depth(s))
    direction: Vec2 | str = "normal"        # usually the surface normal (pressure)
    # renderer draws a growing arrow strip + can collapse to a ResultantForce (M9)
```

> **Back-compat:** M1 code that passed `magnitude=` keeps working via a shim
> (`magnitude` → interpreted as a `FIXED`/`PROPORTIONAL` hint) with a deprecation
> note; new code uses `value` + the renderer's `VectorScalePolicy`.

## `InteractionKind` (replaces the physics half of `ForceKind`, review 22)

```python
class InteractionKind(StrEnum):
    GRAVITY = "gravity"    # label "mg" (uniform field) or "GMm/r^2" (orbital) — SAME interaction
    NORMAL = "normal"; FRICTION = "friction"; APPLIED = "applied"
    TENSION = "tension"; REACTION = "reaction"; SPRING = "spring"; DAMPING = "damping"
# ForceKind kept as a thin alias mapping WEIGHT->GRAVITY for M1 compatibility.
```

## `RigidBody2D` (in `bodies.py`) — review 4

```python
@dataclass
class RigidBody2D(PhysicsAsset):
    mass_props: MassProperties = MassProperties()
    def point_position(self, ref: str, state: BodyState2D | None = None) -> np.ndarray:
        pose = state.pose if state else self.pose
        return pose.world_point(self.local_keypoints[ref])
    def point_velocity(self, ref: str, state: BodyState2D) -> np.ndarray:
        # v_P = v_G + ω × r_{P/G}   (GENERIC — the Rule 5 (r_y,-r_x) cross product)
        r = self.point_position(ref, state) - state.pose.world_point(local_CM)
        return array(state.velocity) + state.omega * array([-r[1], r[0], 0.0])
    def point_acceleration(self, ref, state) -> np.ndarray:
        # a_P = a_G + α × r + ω × (ω × r)
    def inertia_about(self, ref) -> float:
        return mass_props.inertia_about(local_keypoints[ref] - local_CM)

# M1's Block is re-parented onto RigidBody2D (behaviour identical); Rod/Disk/etc. follow in M3.
class Block(RigidBody2D): ...        # keeps all M1 fields/defaults + tests
```

## Tests (`tests/test_pose_rigidbody.py`)

```
- Pose2D.world_point: rotate a local (1,0) by 90° about (2,0) -> (2,1).
- set_pose is ABSOLUTE: two successive rotate_to(θ) calls leave the body at θ,
  not 2θ (the anti-drift guarantee).
- keypoint() still returns world coords; back-compat set_keypoint(world) round-trips.
- RigidBody2D.point_velocity ⟂ (P - CM) for pure rotation (dot≈0), matches
  v_G + ω×r for combined motion (numeric check).
- MassProperties.inertia_about parallel-axis: I(r) == I_cm + m r^2.
- Block re-parented on RigidBody2D still passes all 8 M1 tests (regression).
- ForceSpec.value vs arrow length: two forces with different `value` but the same
  VectorScalePolicy.FIXED render equal-length arrows (physics ≠ length).
```

## Render smoke
Re-render the M1 block-on-floor demo unchanged (proves the refactor is
behaviour-preserving); plus a spinning `Rod` via repeated `rotate_to` to show no
drift after many frames.

## Revisions (architecture review 2026-09-05)
- **NEW milestone** inserted from review point 33 to harden the model layer
  before M2–M4. Implements review points 3 (Pose2D/local keypoints), 4
  (RigidBody2D + generic point kinematics + MassProperties), 20 (ForceSpec value
  vs arrow length + VectorScalePolicy), 21 (TorqueSpec/ImpulseSpec via loads.py),
  22 (InteractionKind.GRAVITY unifies WEIGHT/GRAVITY), and 13/19 (typed refs).
- **Rationale:** these decisions affect almost everything downstream and are far
  cheaper to fix now than after M8–M15; M1's public contract is preserved so no
  shipped code breaks.

## Revisions (kinematics review 2026-09-05) — MUST

- **`pose.py` MOVES to `physics/core/`** (shared by mechanics, fluids, and the
  new kinematics layer), joined by `core/transforms.py` (SE(2) `Transform2D`,
  with the mandatory **point (T+R) vs vector (R only)** distinction) and
  `core/frames.py` (`Frame2D`). See [`M01_6_kinematics_bindings.md`](M01_6_kinematics_bindings.md).
- **`RigidBody2D.point_velocity/position/acceleration` MUST delegate to
  `kinematics/rigid_body.py`** — point kinematics is a generic reusable primitive,
  not a body-specific method. The M1.5 methods above become thin wrappers.
- **`BodyState2D` becomes an alias of `RigidKinematicState`** (M1.6/M6) — the
  canonical solver-supplied per-entity state (pose + optional velocity/accel/ω/α).
- **Rationale:** the transform/point-kinematics math is used identically by
  rolling, falling-rod, ladder, spool, pulley, linkage, and collision scenes;
  implementing and binding it once is foundational (M1.6), so M1.5 must expose
  its geometry through that layer rather than duplicating matrix code.
