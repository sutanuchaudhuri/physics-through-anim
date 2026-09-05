# M16 — 3-D Rigid-Body / Top / Gyroscope

Status: **DRAFT FOR REVIEW**
Depends on: M1–M15 + SKILL Rule 17 (`ThreeDLessonScene`, `lift_to_3d`). Files:
`assets/physics/mechanics3d/` (NEW parallel package), reuse the 2-D semantic
model (keypoints, forces, state, events) with 3-D geometry.

## Revisions (architecture review 2026-09-05)

- **`BodyState2D`/`BodyState3D` as a common protocol** (review 27), not a scalar
  angle hacked into `extra`. 3-D orientation needs a rotation matrix or
  quaternion:
  ```python
  class BodyStateND(Protocol):
      @property
      def pose(self) -> PoseND: ...          # Pose2D (angle) | Pose3D (quaternion/matrix)
      @property
      def velocity(self): ...; angular_velocity: ...
  # SystemState.states maps AssetRef -> AssetState whose body is 2D or 3D uniformly.
  ```
- **`Top.as_trajectory()` moves out of the body** into
  `motion/analytic/top.py` (review 15) — the precession is an analytic
  `Trajectory` provider; `Top` stays geometry-only.
- The semantic layer (typed refs, loads, contacts, constraints, events, recipes)
  is reused unchanged; only geometry + camera differ (Rule 17).

## Goal

Extend the framework to genuinely 3-D mechanics (a spinning top's precession, a
gyroscope, 3-D rigid-body motion) — the vision's explicit "and then we will
extend to 3D" endpoint. The **semantic layer is unchanged**; only geometry and
the camera differ (Rule 17). 2-D assets stay 2-D (a flat FBD must not tilt).

## Package strategy

```
mechanics3d/                      # parallel to mechanics/, shares kinds/state/events
   base3d.py     # PhysicsAsset3D: keypoints are 3D (already are!), mobject is 3D
   bodies3d.py   # Sphere, Cylinder3D, Box(Prism), Rod3D, Top, Gyroscope, Disk3D
   supports3d.py # Ground(Surface z=0), Incline3D, Table3D
   overlays3d.py # Arrow3D force/velocity/omega; angular-momentum L vector; precession trail
   frames3d.py   # body vs space frame; Euler-angle glyph
   assembly3d.py # Assembly3D: compose + place + combined 3D FBD + synced animate
```

Because M1 keypoints are **already 3-D np arrays** and `State` already carries
`angle`/`omega` (extendable to 3-vectors via `extra`), most of the semantic
machinery ports directly; the work is 3-D mobjects + `ThreeDLessonScene` camera.

## Key classes (pseudocode)

```python
@dataclass
class Top(PhysicsAsset3D):
    name="top"; mass=1.0; height=1.2; radius=0.4; tilt_deg=20.0
    spin_omega=20.0; precession_omega=1.5; pivot=(0,0,0)
    build(): Cone/again body via Surface of revolution; keypoints CM, tip=pivot, axis_end
    def as_trajectory(period) -> Trajectory3D:      # analytic precession (solver-free):
        # axis sweeps a cone about vertical at precession_omega; body spins at spin_omega
def angular_momentum_vector(body) -> VGroup:        # Arrow3D along spin axis (L)
def torque_vector(body, about) -> VGroup            # gravity torque -> precession explanation
def precession_trail(body, traj, t0,t1) -> VMobject # path of the axis tip (a circle)

@dataclass
class Gyroscope(PhysicsAsset3D):
    name="gyro"; wheel=Disk3D(...); gimbal=True; spin_omega=30.0
    build(): spinning wheel + gimbal rings; keypoints axle ends, CM
```

## 2-D → 3-D lift for a body (reuse Rule 17 `lift_to_3d`)

```python
# Start with the flat 2-D asset, then lift into a solid for a "gain depth" reveal:
flat = Disk(radius=0.6)                      # 2-D asset (M3)
solid = lift_to_3d(scene, flat.mobject, Cylinder3D(radius=0.6, height=0.3).mobject)
# camera tilts to isometric while the circle becomes a cylinder (Rule 17).
```

## Flagship demo — precessing top

```python
class M16Top(ThreeDLessonScene):
    LESSON_NAME="mechanics3d_demo"
    def construct():
        add_narration(); self.standard_view()
        add(physics_axes_3d())
        top=Top(tilt_deg=20, spin_omega=20, precession_omega=1.5)
        add(top.mobject)
        self.hud(Text("Gyroscopic precession"))                  # pinned (Rule 17)
        L = angular_momentum_vector(top); tau = torque_vector(top, about=top.keypoint("tip"))
        add(L, tau)
        traj = top.as_trajectory(period=8)
        # animate: axis precesses; L sweeps the cone; trail drawn by precession_trail
        animate_trajectory3d(self, {"top": traj}, 0, 8, run_time=10)
        finish_with_narration()
```

## Tests (`tests/test_assets_3d.py`)

```
- Top keypoints CM/tip/axis_end are 3-vectors; tip == pivot.
- as_trajectory: axis tip traces a circle of constant polar angle (precession);
  |axis| constant; spin phase advances at spin_omega.
- angular_momentum_vector is an Arrow3D along the spin axis.
- lift_to_3d contract (already in tests/test_threed.py) reused for a disk->cylinder.
- Assembly3D places a body on Ground(z=0); combined 3D FBD builds.
```

## Render smoke
`M16Top` at high quality (3-D + ambient orbit reads better; Rule 17), extract a
frame mid-precession: tilted spinning top, L along the axis, axis tip on its
circular precession trail.

## Use cases unlocked
Precessing top, gyroscope, 3-D rigid-body rotation, inclined-axis spin, and the
2-D→3-D "gain depth" reveal for any round body — the full extension of the 2-D
framework into three dimensions, with the semantic layer (keypoints, forces,
state, events, recipes) reused unchanged.
```
