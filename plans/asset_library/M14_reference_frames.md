# M14 — Reference Frames / Non-Inertial Overlays

Status: **DRAFT FOR REVIEW**
Depends on: M6 (state), M9 (overlays). Files: `frames.py` (NEW),
`overlays/frames.py` (pseudo-force overlays), reuse SKILL Rule 1 observer icons
+ Rule 6 (state the frame).

## Revisions (architecture review 2026-09-05)

- **`ReferenceFrame` consumes a `FrameState`/`FrameTrajectory`; it does NOT
  integrate Ω internally** (review 26). The `-∫Ω dt` below is removed — a frame
  must not integrate anything (solver-free boundary). Transformation is purely
  kinematic:
  ```python
  @dataclass(frozen=True)
  class FrameState:
      pose: Pose2D; velocity: Vec2 = (0,0); angular_velocity: float = 0.0
      acceleration: Vec2 = (0,0); angular_acceleration: float = 0.0
  class FrameTrajectory(Protocol):
      def state_at(self, t) -> FrameState: ...
  # ReferenceFrame.to_frame(system_state, frame_state) is a pure coordinate map.
  ```
  Rationale: the frame's motion is *supplied* (like any trajectory), never solved
  — keeping the non-inertial layer consistent with the rest of the framework.
- Pseudo-force overlays stay in `overlays/frames.py` (dashed/neutral), separate
  from the semantic frame.

## Revisions (kinematics review 2026-09-05) — MUST

- **`ReferenceFrame` MUST be built on `core/frames.py::Frame2D`** (M1.6):
  `to_world_point/to_local_point/to_world_vector/to_local_vector`. Frame motion
  is supplied as `FrameState` (below); the transform is purely kinematic — the
  frame MUST NOT integrate anything. Particle-on-moving-wedge, projectile-from-
  accelerating-cart, and ball-in-rotating-hoop all reuse this one primitive.

## Goal

Support non-inertial mechanics **without hand-drawing fake forces every time**
(vision §17). A `ReferenceFrame` re-expresses body states in a moving/rotating
frame; pseudo-force overlays are a *separate semantic class* from real
interaction forces so they never get confused (Rule 2 spirit).

## `frames.py` (NEW)

```python
class FrameKind(StrEnum):
    INERTIAL="inertial"; TRANSLATING="translating"; ROTATING="rotating"

@dataclass
class ReferenceFrame:
    kind: FrameKind = FrameKind.INERTIAL
    origin: Callable[[float], np.ndarray] = lambda t: ORIGIN      # frame origin vs t
    accel:  Callable[[float], np.ndarray] = lambda t: ZERO        # frame linear accel a_f(t)
    omega:  Callable[[float], float]      = lambda t: 0.0         # rotation rate Ω(t)
    label: str = "S'"
    def to_frame(state: State, t) -> State:      # world state -> frame-relative state
        subtract origin(t) & its velocity; if ROTATING, rotate by -∫Ω and add rel terms
    def icon(scale=1.0) -> VGroup:               # Rule 1 glyph (inertial vs non-inertial)
        # non-inertial (accel≠0 or omega≠0) -> reference_frame_icon + curved accel arrow
```

## `overlays/frames.py` — pseudo-force overlays (kept SEPARATE from real forces)

```python
class PseudoForceKind(StrEnum):
    INERTIAL_PSEUDO="inertial"; CENTRIFUGAL="centrifugal"
    CORIOLIS="coriolis"; EULER="euler"

COLOR_PSEUDO = "#CED4DA"   # deliberately washed-out / dashed so it reads as "fictitious"

def pseudo_force_arrow(body, kind, frame, t, scale=1.0) -> VGroup:
    # DASHED arrow (distinct from solid real-force arrows) + symbolic label:
    #   inertial:    -m a_f
    #   centrifugal: +m Ω^2 r   (outward)
    #   coriolis:    -2 m Ω x v_rel
    #   euler:       -m dΩ/dt x r
    Arrow(..., colour=COLOR_PSEUDO, dashed=True) + MathTex(symbol)
def frame_badge(frame) -> VGroup:      # observer icon + S/S' label (Rules 1 & 6)
```

> Pseudo-forces are drawn **dashed** and in a **neutral colour** so a viewer
> never mistakes a fictitious force for a real one — this is the non-inertial
> analogue of Rule 2's FBD-vs-kinematics separation.

## Assembly integration

```python
Assembly.in_frame(frame) -> view:      # returns a lightweight wrapper whose
    # apply_states/overlays express bodies relative to `frame` (e.g. block appears
    # stationary in the truck's frame while a dashed -ma pseudo-force explains why).
```

## Demo — block in an accelerating truck (two-frame view)

```python
class M14AcceleratingTruck(Scene):
    a=Assembly(); truck_floor=Floor(); blk=Block(label="m")
    a.add(truck_floor); a.add(blk, place_on=truck_floor)
    S  = ReferenceFrame(INERTIAL, label="S")                    # ground
    Sp = ReferenceFrame(TRANSLATING, accel=lambda t: (A,0), label="S'")  # truck
    # ground frame: block accelerates, real forces only (N, mg, friction)
    # truck frame:  block at rest, add dashed pseudo-force -m a_f (frame_badge S')
    left  = snapshot in S  with frame_badge(S)  + real FBD
    right = snapshot in Sp with frame_badge(Sp) + real FBD + pseudo_force_arrow(INERTIAL)
    play_subscenes(together, [left, right])
    finish_with_narration()
```

## Tests (`tests/test_assets_frames.py`)

```
- ReferenceFrame.to_frame(TRANSLATING): a body at world x with frame origin o(t)
  reports position x - o(t); an inertial frame is identity.
- ROTATING to_frame rotates the relative position by -θ(t).
- pseudo_force_arrow is dashed and COLOR_PSEUDO; centrifugal points outward
  (away from rotation centre); coriolis ⟂ v_rel.
- frame.icon: non-inertial when accel≠0 or omega≠0 (Rule 1 correctness).
- frame_badge contains an observer icon + label.
```

## Render smoke
`M14AcceleratingTruck`: two-panel frame; ground panel shows block sliding with
real forces, truck panel shows block at rest with a dashed pseudo-force. Confirm
the pseudo-force is visually distinct (dashed/grey).

## Use cases unlocked
Block in accelerating truck, pendulum in accelerating car, effective-gravity
direction, bead on rotating rod, puck on turntable, Coriolis deflection, rotating
hoop, centrifuge, Foucault-style 2-D explanation — each a composition with a
`ReferenceFrame` + the correct dashed pseudo-force overlay.
```
