# M1.6 — Kinematics Layer: Transforms, Frames, Bindings, Point Kinematics

Status: **DRAFT FOR REVIEW** (NEW — kinematics review 2026-09-05, **all MUST**)
Depends on: M1.5. Comes **before M6** and before advanced rolling/contact (M2/M3).
Files: `physics/core/transforms.py`, `physics/core/pose.py` (moved here from
mechanics), `physics/core/frames.py`, `physics/kinematics/` (NEW package),
`overlays/kinematics.py`.

## Governing rule (MUST)

> **Reuse the transformation mathematics aggressively; never reuse the physics
> solution implicitly.**

The pipeline is fixed:

```
Physics solution  ->  Kinematic state  ->  Geometric transformation  ->  Manim
(human/AI/solver)     (RigidKinematicState)  (Transform2D / bindings)     (VGroup)
```

**The framework MUST be able to compute** (pure kinematics/geometry): world
position from local point + supplied pose; velocity/acceleration of any point
from supplied `v_O, ω, α`; vector decomposition; frame transforms; relative
velocity; tangent/normal vectors; matrix transforms; and the *declared* rolling
relation `Δθ = -Δs/R`.

**The framework MUST NOT decide** (dynamics): what `ω(t)`/`α(t)` are; acceleration
from forces/torques; when a collision occurs; friction; whether energy is
conserved. Those are supplied as a `Trajectory` (M6).

## `core/transforms.py` (MUST) — SE(2) homogeneous transform

```python
@dataclass(frozen=True)
class Transform2D:
    m: np.ndarray                       # 3x3 SE(2) matrix
    @classmethod
    def identity(cls) -> "Transform2D"
    @classmethod
    def rotation(cls, theta) -> "Transform2D"          # R(θ) about origin
    @classmethod
    def translation(cls, x, y) -> "Transform2D"
    @classmethod
    def from_pose(cls, pose: "Pose2D") -> "Transform2D" # [[R, t],[0,1]]
    def compose(self, other) -> "Transform2D"          # self ∘ other (matrix @)
    def inverse(self) -> "Transform2D"
    def transform_point(self, p: Vec2) -> np.ndarray   # translation + rotation
    def transform_vector(self, v: Vec2) -> np.ndarray  # ROTATION ONLY (no translate)
```

> The point-vs-vector distinction is mandatory: a **point** gets `T+R`, a
> **vector** (velocity, force direction) gets `R` only. Lesson writers MUST never
> hand-build `R = [[cosθ,-sinθ],[sinθ,cosθ]]`; they use `Transform2D` / the body
> API.

## `core/pose.py` (MUST — moved here from mechanics)

```python
@dataclass(frozen=True)
class Pose2D:
    position: Vec2 = (0.0, 0.0)
    angle: float = 0.0
    def to_transform(self) -> Transform2D: return Transform2D.from_pose(self)
    def world_point(self, local: Vec2) -> np.ndarray
    def world_vector(self, local_vec: Vec2) -> np.ndarray
    def compose(self, child: "Pose2D") -> "Pose2D"     # parent ∘ child (scene graph)
```

## `core/frames.py` (MUST) — reference-frame transforms

```python
@dataclass
class Frame2D:                          # a.k.a. ReferenceFrame2D
    pose: Pose2D = Pose2D()             # frame origin/orientation (may vary via FrameState, M14)
    def to_world_point(self, p_local) -> np.ndarray
    def to_local_point(self, p_world) -> np.ndarray
    def to_world_vector(self, v_local) -> np.ndarray
    def to_local_vector(self, v_world) -> np.ndarray
# Pure kinematic map (MUST NOT integrate) — M14 supplies frame motion as FrameState.
```

## `RigidKinematicState` (MUST — in `core/state.py`) — the solver's output shape

```python
@dataclass(frozen=True)
class RigidKinematicState:              # canonical per-entity EntityState (M6)
    pose: Pose2D
    velocity: Vec2 | None = None
    acceleration: Vec2 | None = None
    omega: float | None = None
    alpha: float | None = None
# BodyState2D is kept as an alias of RigidKinematicState. The solver MAY supply
# only `pose` (simple animation), pose+velocity (velocity arrows), or all fields.
```

## `kinematics/` package (NEW, MUST)

```python
# kinematics/rigid_body.py  — generic point kinematics (NOT a CircularBody feature)
def point_position(body, ref, state) -> np.ndarray          # pose.world_point(local[ref])
def point_velocity(body, ref, state) -> np.ndarray          # v_O + ω × r_{P/O}
def point_acceleration(body, ref, state) -> np.ndarray      # a_O + α×r + ω×(ω×r)
# RigidBody2D (M1.5) delegates its point_* methods to these.

# kinematics/point.py — relative position/velocity between points/bodies
def relative_position(a_ref, b_ref, state); def relative_velocity(a_ref, b_ref, state)

# kinematics/relative_motion.py — motion measured in a Frame2D
def velocity_in_frame(point, state, frame); def acceleration_in_frame(...)

# kinematics/instantaneous_center.py
@dataclass(frozen=True)
class InstantaneousCenterState: body: AssetRef; point: Vec2; omega: float
def velocity_at(icr: InstantaneousCenterState, P) -> np.ndarray   # ω×(P-I): ⟂ IP, |v|=ω·IP

# kinematics/rolling.py — a DECLARED kinematic constraint (allowed), not dynamics
@dataclass(frozen=True)
class RollingKinematicRelation: radius: float; direction: int = +1
    def pose_from_arc(self, s) -> Pose2D    # Δθ = -Δs/R about the contact

# kinematics/linkage.py — propagate poses through a chain given generalized coords
def propagate_linkage(links, thetas, anchor) -> dict[AssetRef, Pose2D]

# kinematics/bindings.py — the reusable animation bindings (see below)
```

## Bindings (MUST) — one mechanism drives every rigid body

Each binding resolves refs against the `Assembly` + `SystemState`, computes a
target `Pose2D` (or point), and applies it via `asset.set_pose(...)` (M1.5
absolute pose → no drift). Each exposes `apply(assembly, state)` and an
`as_updater(tracker, trajectory)` form for animation.

```python
RigidPoseBinding(body, pose_source)          # SystemState entity pose -> body pose
PointAttachmentBinding(child_point, parent_point)   # child keypoint follows parent keypoint
RelativePoseBinding(child, parent, relative_pose)   # weld: fixed relative pose
SurfacePoseBinding(body, surface, s, orientation="normal")  # seat on a surface at param s
PathPoseBinding(body, path, parameter="s", orientation="tangent")  # follow a curve
RollingPoseBinding(body, surface)            # translate+rotate at v=ωR (uses RollingKinematicRelation)
LookAtBinding(mobject, target)               # orient toward a target (radius vector, force along spring)
```

### Parent–child scene graph (MUST)

`Assembly` MUST maintain parent→child transform links so a parent pose change
propagates automatically:

```
Block1 pose changes -> spring_hook world point changes -> spring endpoint moves ->
spring geometry redraws
```

`AttachmentBinding`/`RelativePoseBinding` register these edges; the renderer
resolves children after parents each frame. No scene recomputes attachment
geometry by hand.

## Animation helpers (MUST — replace ad-hoc `.animate.shift().rotate()`)

```python
ApplyPoseTransition(body, from_pose, to_pose, run_time)   # absolute pose interpolation
FollowTrajectory(body, source, t0, t1, run_time)          # body follows SystemState pose
# All keypoints, contact point, velocity arrows, CM marker, attachments, labels stay synced.
```

## `overlays/kinematics.py` (MUST — teaching views, not transform implementation)

```python
TranslationView(body, v)                     # pure translation: every point same v
RotationView(body, omega)                    # pure rotation: v = ω r
RigidTransformView(body, state)              # general plane motion = translation + rotation
RigidBodyVelocityField(body, points, instantaneous_center)  # arrows ∝ IP, ⟂ IP (Rule 5)
VelocityAtPointView(body, point, reference="instantaneous_center")  # arrow + 90° marker + IP line
TransformExplanationView(source_frame, target_frame, transform)     # r_local →R(θ)→ +r_CM → world (+matrix)
```

## Acceptance examples (MUST all pass — demo + tests)

```
1. translating block                      (RigidPoseBinding, pose = translation only)
2. rod rotating about a fixed hinge        (RigidPoseBinding, pose = rotation about A)
3. rod with translation + rotation         (general plane motion)
4. point attached to a moving body         (PointAttachmentBinding)
5. spring attached to a moving block        (PointAttachmentBinding + geometry redraw)
6. wheel translating + rotating             (RollingPoseBinding, Δθ=-Δs/R)
7. object following a curved path           (PathPoseBinding, orientation=tangent)
8. two linked rods                          (propagate_linkage -> RigidPoseBinding per link)
```

## Tests (`tests/test_kinematics.py`)

```
- Transform2D.transform_point translates+rotates; transform_vector rotates ONLY.
- Transform2D.rotation(θ).compose(translation) == from_pose(Pose2D(t,θ)); inverse round-trips.
- point_velocity == v_O + ω×r; ⟂ (P-O) for pure rotation (dot≈0); point_acceleration matches formula.
- InstantaneousCenter velocity_at: |v| = ω·IP and v ⟂ IP.
- RollingKinematicRelation.pose_from_arc: Δθ == -Δs/R.
- Frame2D round-trips to_world/to_local for points and vectors; vector ignores origin translation.
- Bindings: PointAttachmentBinding moves child when parent pose changes; RelativePoseBinding
  keeps a constant relative pose; PathPoseBinding places body at path.point_at(s) with tangent angle.
- Parent-child: moving a parent updates a bound child's world keypoint (scene-graph propagation).
- The 8 acceptance examples each build + apply a state without error.
```

## Render smoke
One clip cycling the 8 acceptance cases (Rule 16 `together`/`sequential`); a frame
per case confirms correct pose, attachment tracking, rolling (no drift), and path
tangent orientation.

## Revisions (kinematics review 2026-09-05)
- **NEW milestone (all MUST)** inserted from the kinematics review. Establishes the
  reusable transform/kinematics/binding layer as foundational, **before M6** and
  before advanced rolling/contact — so later Krotov/F=ma scenes become
  *configuration + externally supplied states*, not custom Manim transform code.
- **Moves `pose.py` to `core/`** and adds `transforms.py`/`frames.py` there
  (shared by mechanics, fluids, kinematics). `RigidBody2D` (M1.5) delegates its
  point kinematics to `kinematics/rigid_body.py`.
- **Rationale:** the point-velocity relation `v_P = v_O + ω×r` and pose transforms
  are used by rolling, falling-rod, ladder, spool, pulley, linkage, and collision
  scenes alike; implementing them once (and binding them once) is as important to
  productivity as `Block`/`Spring`/`Incline`/`FBD`.
