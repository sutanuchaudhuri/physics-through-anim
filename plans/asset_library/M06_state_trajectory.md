# M6 — State Snapshot + Trajectory Adapter (solver-agnostic motion)

Status: **DRAFT FOR REVIEW**
Depends on: M1–M5. Files: `state.py` (NEW), `base.py` (+`apply_state`),
`assembly.py` (semantic queries + `apply_states`), `bodies.py` (bodies honour
`apply_state`).

## Revisions (architecture review 2026-09-05) — major rewrite

> This is the most important file for the corpus-driven goal; several shapes
> below are **replaced**. The revised contract:

- **One consistent `SystemState` per time `t`, not one `Trajectory` per body**
  (review 12). Rationale: coupled systems (two blocks + pulley, cylinder + moving
  wedge, colliding masses, rod + sliding end, chain + support) must never mix a
  body from one interpolation with a contact from another provider.
  ```python
  @dataclass(frozen=True)
  class BodyState2D:
      pose: Pose2D | None = None            # absolute (M1.5) — no cumulative rotation
      velocity: Vec2 | None = None; omega: float | None = None
      acceleration: Vec2 | None = None; alpha: float | None = None
  @dataclass(frozen=True)
  class AssetState:                         # review 24: carries optional shape (chains)
      body: BodyState2D | None = None
      shape: object | None = None           # e.g. ChainShapeState(path=...)
  @dataclass(frozen=True)
  class SystemState:
      states: Mapping[AssetRef, AssetState]
      observables: Mapping[QuantityRef, QuantityValue]   # typed, review 13 (NO extra: dict)
  class Trajectory(Protocol):
      @property
      def domain(self) -> TimeDomain: ...
      def state_at(self, t: float) -> SystemState: ...
  ```
- **No `extra: dict[str, float]`** (review 13). Observables are keyed by typed
  `QuantityRef("contact:disk.floor:N")`, `QuantityRef("rope:1:tension")`,
  `QuantityRef("body:disk:KE")`, `QuantityRef("system:energy")`;
  `QuantityValue = float | np.ndarray`. `GraphBinding` (M9) binds to these
  directly (a `Signal`), across the whole system.
- **`InterpolationPolicy` per quantity** (review 16): `LINEAR`, `ANGLE_UNWRAP`
  (avoid the 2π wrap), `STEP_LEFT`, `STEP_RIGHT`, `NONE`. An impact must not
  interpolate velocity smoothly across the collision unless intentionally
  visualising the impulse interval.
- **Analytic solutions live OUTSIDE assets** (review 15) in
  `src/physics_through_anim/motion/analytic/` (`projectile.py`, `rolling.py`,
  `kepler.py`, `shm.py`, `top.py`) as `Trajectory` providers. `OrbitPath`/`Top`
  stay geometry-only.
- **`apply_state` uses absolute pose** (M1.5 `set_pose`), never incremental
  rotation — repeated updater calls don't drift.
- **Solver-free contract (authoritative):** *A mechanics asset or relation may
  evaluate geometry, kinematics, constitutive laws, and declared constraint
  relationships, but it must never advance physical state by integrating
  equations of motion. Motion enters only through a `Trajectory` provider that
  samples a complete `SystemState` at time `t`.* Providers: `AnalyticTrajectory`,
  `SampledTrajectory`, `PiecewiseTrajectory`, `CSVTrajectory`,
  `SciPySolutionAdapter`, `ManimPhysicsAdapter`, `PrecomputedTrajectory`.
- **`StateSnapshot`** references a `SystemState` + `QuantityRef`s (not
  `State.extra`).

## Revisions (springs & fluids review 2026-09-05)

- **`SystemState` is made domain-generic so it can drive fluids too** (fluids
  review 21). A fluid has no single CM pose; it needs a free surface / fields.
  So `SystemState` carries **entities + fields + observables**, and the
  per-entity state is a **union**:
  ```python
  EntityState = BodyState2D | FluidRegionState | ...      # AssetState.body widened
  @dataclass(frozen=True)
  class SystemState:
      entities: Mapping[AssetRef, EntityState]
      fields: Mapping[FieldRef, FieldState]               # pressure(x,y), velocity(x,y)
      observables: Mapping[QuantityRef, QuantityValue]
  ```
  Rationale: one `Trajectory.state_at(t)` then drives SHM, a Krotov pulley, a
  dam-pressure lesson, and a draining-reservoir animation with the same timeline,
  signals, named moments, graph binding, and narration sync.
- **Extract a domain-neutral `physics/core/`** shared by `mechanics/` and
  `fluids/`: `state.py`, `trajectory.py`, `timeline.py`, `signals.py`, `refs.py`,
  `events.py`, `loads.py`. `mechanics/` keeps `BodyState2D`; `fluids/` adds
  `FluidRegionState`. Rationale: SHM, a rigid-body problem, and a fluid problem
  reuse the same infrastructure while domain physics objects stay separate.
- **Spring SHM kinematics live in `motion/analytic/shm.py`** as an
  `SHMTrajectory` provider (not in `springs.py`) — reaffirms review 15. The same
  `LinearSpring` can be driven by analytic/damped SHM, SciPy, CSV, or
  manim-physics without changing the spring asset.

## Revisions (kinematics review 2026-09-05) — MUST

- **The per-entity state is `RigidKinematicState`** (from M1.6): `pose` +
  optional `velocity`/`acceleration`/`omega`/`alpha`. `BodyState2D` is kept as an
  alias. `SystemState.entities` are these kinematic states; the transform/binding
  layer (M1.6) consumes the poses, overlays consume the vectors/quantities.
- **The solver MAY supply a partial state** — just `pose` (simple animation),
  `pose + velocity` (velocity arrows), or all fields (full F=ma explanation).
- **Bindings, not `apply_state` ad-hoc, drive motion** (M1.6): a
  `FollowTrajectory`/`RigidPoseBinding` reads `SystemState.entities[ref].pose`
  each frame and applies it via absolute `set_pose` (no drift). This supersedes
  the earlier `Assembly.animate_trajectory` sketch, which now delegates to the
  binding layer.
- **Rationale:** one binding mechanism keeps keypoints, contact points, velocity
  arrows, CM markers, attachments and labels synchronised for every rigid body,
  and cleanly separates the supplied *kinematic state* from the *geometric
  transformation* that renders it.

## Revisions (presentation review 2026-09-05) — MUST

- **Add the presentation data contract to `core/scene_data.py`** (M18):
  `QuantitySpec` (symbol/value/unit/latex), `VectorSpec` (anchor/vector/role/
  `perpendicular_to`), `EquationSpec`, `BindingSpec`, and **`NamedState`** — which
  **elevates `StateSnapshot`** into a first-class teaching state (a `SystemState`
  + supplied `QuantitySpec`s/`VectorSpec`s + annotations).
- **`SystemState.observables` values MAY be `QuantitySpec`** (symbol + value +
  unit + latex), so one supplied number renders as a label, equation term, bar,
  graph point, or HUD **without recomputation**.
- **Rationale:** most teaching scenes need *correct named states + understandable
  transitions*, not a frame-by-frame simulation. The solver supplies the values;
  M6 just carries them. See [`M18_presentation_authoring.md`](M18_presentation_authoring.md).

## Goal

Let assets **consume** motion without integrating it (the vision's non-solver
contract §7). A `Trajectory` is any source of `State` at a time `t`
(analytic formula, NumPy, SciPy, CSV, manim-physics, LLM-validated values). A
`StateSnapshot` (§23) lets an AI request a freeze-frame teaching moment
declaratively.

## `state.py` (NEW)

```python
@dataclass(frozen=True)
class State:
    position: tuple[float,float] | None = None     # CM position
    angle:    float | None = None                  # body orientation (rad)
    velocity: tuple[float,float] | None = None
    omega:    float | None = None
    acceleration: tuple[float,float] | None = None
    alpha:    float | None = None
    extra:    dict[str, float] = field(default_factory=dict)   # N, T, energy...

class Trajectory(Protocol):
    def state_at(self, t: float) -> State: ...

# Concrete adapters (all solver-free from the asset's view):
@dataclass
class AnalyticTrajectory(Trajectory):
    fn: Callable[[float], State]              # state_at = fn
@dataclass
class SampledTrajectory(Trajectory):
    times: np.ndarray; states: list[State]    # linear interp between samples
    def state_at(t): interpolate position/angle/velocity... between bracketing samples
@dataclass
class CSVTrajectory(SampledTrajectory):
    @classmethod from_csv(path, cols={...}) -> builds times+states
# manim-physics bodies already move themselves (Rule 10) -> no adapter needed;
# a scene can still SAMPLE a pymunk body into a SampledTrajectory for overlays.

@dataclass(frozen=True)
class StateSnapshot:              # a declarative freeze-frame request (§23)
    t: float
    phase: Phase = Phase.BEFORE
    show: tuple[str,...] = ("body",)   # {"body","fbd","velocity","omega","contact","energy"}
    label: str | None = None
```

## Asset integration (`base.py`, `bodies.py`)

```python
PhysicsAsset.apply_state(state: State):
    if state.position: shift so CM -> position   (moves keypoints too)
    if state.angle is not None: rotate mobject about CM to `angle`, update keypoints
    stash state on self._state (for overlays to read velocity/omega)
# Bodies override to also move their spoke/rim keypoints consistently.

Assembly.apply_states(mapping: dict[str, State]):   # {"disk": s1, "block": s2}
    for name, s in mapping: self.body(name).apply_state(s)

Assembly.animate_trajectory(scene, traj_map: dict[str,Trajectory], t0, t1, run_time):
    tracker = ValueTracker(t0)
    updater: for name,traj: body(name).apply_state(traj.state_at(tracker.value))
    play(tracker.animate.set_value(t1), run_time)     # bodies follow the trajectory
```

## Semantic queries (Assembly) — the AI-friendly surface (§25)

```python
Assembly.body(name)        -> PhysicsAsset          # "disk"
Assembly.assets(kind=Body) -> list                  # filter by class
Assembly.resolve(ref)      -> np.ndarray            # "pulley.A", "rope.from"
Assembly.forces_on(name)   -> list[ForceSpec]
Assembly.snapshot(snap: StateSnapshot, traj_map) -> VGroup   # build the freeze frame:
    apply states at snap.t; assemble requested overlays into one VGroup
```

## Demo — a projectile from a formula (no solver in the asset)

```python
def parabola(t) -> State:
    x = x0 + vx*t; y = y0 + vy*t - 0.5*g*t^2
    vy_t = vy - g*t
    return State(position=(x,y), velocity=(vx, vy_t))
ball = Particle(...)                     # Particle = point-like body (added here or M13)
a.add(ball)
a.animate_trajectory(self, {"ball": AnalyticTrajectory(parabola)}, 0, T, run_time=5)
# then a StateSnapshot at apex:
snap = StateSnapshot(t=T/2, show=("body","velocity"))
self.play(FadeIn(a.snapshot(snap, {"ball": AnalyticTrajectory(parabola)})))
```

## `Particle` body (point-like; belongs here or M13 — declared here)

```python
@dataclass
class Particle(PhysicsAsset):
    name="particle"; mass=1.0; position=(0,0); radius=0.08; color=None
    show_weight=False; label="m"
    build(): Dot(position, r=radius); keypoint CM; optional weight
```

## Tests (`tests/test_assets_state.py`)

```
- AnalyticTrajectory.state_at returns the fn's State.
- SampledTrajectory interpolates midway between two samples (linear).
- apply_state(position) moves CM and all keypoints by the right delta.
- apply_state(angle) rotates keypoints about CM (a top keypoint ends where expected).
- Assembly.body/resolve/forces_on return the right objects.
- StateSnapshot with show=("body","velocity") produces a VGroup containing a
  velocity overlay (needs M9 overlays; until then assert body present).
- animate_trajectory math: at t1 the body CM == traj.state_at(t1).position.
```

## Render smoke
Projectile follows the parabola; apex snapshot shows the velocity vector
horizontal (vy≈0). Confirm by frame.

## Use cases unlocked
Any solver (analytic/NumPy/SciPy/CSV/pymunk-sampled/LLM) drives the same assets;
freeze-frame teaching moments become declarative. Foundation for probe **B**
(Kepler trajectory) and probe **D** (collision snapshots).
