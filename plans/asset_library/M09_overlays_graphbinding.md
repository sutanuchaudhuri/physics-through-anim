# M9 — Explanatory Overlays + Graph Binding

Status: **DRAFT FOR REVIEW**
Depends on: M1–M8. Files: `overlays/` package (NEW), `palette.py` (kinematic +
energy + momentum colours already present; add any missing), `assembly.py`
(`overlay(...)` convenience), reuse SKILL Rules 2/5/6.

## Revisions (architecture review 2026-09-05)

- **`GraphBinding` consumes a `Signal`, not `State.extra`** (review 14). A
  `Signal = Callable[[float, SystemState], float]` (or a `QuantityRef` resolved
  against `SystemState.observables`). Rationale: graphs must work across the
  whole system (N vs θ, friction vs applied force, T₁ vs t, relative slip vs t,
  COM-x vs t, total energy vs t) without stuffing everything into one body.
  ```python
  graph = GraphBinding(x=TimeSignal(),
                       y=QuantitySignal(QuantityRef("contact:cyl.track:N")))
  ```
- **Overlays are render-independent `OverlaySpec`** (review 29 spirit): an
  overlay factory returns a *spec* that the `MechanicsRenderer` turns into a
  `VGroup`, so recipes/plans stay declarative and serialisable. The `-> VGroup`
  signatures below are the renderer's output, not what a recipe stores.
- **All UI lives in `overlays/`** (review 25), including event counters/glyphs
  that earlier drafts placed next to semantic models.

## Revisions (springs & fluids review 2026-09-05)

- **Component / system FBD + `isolate`** land in `overlays/forces.py` (springs
  review 7): the key teaching operations for multi-body spring systems and F=ma/
  Krotov problems.
  ```python
  component_fbd(model, ref)                 # FBD of one component ("m1", "spring1")
  system_fbd(model, members)                # FBD of a chosen subsystem
  isolate(model, members)                   # fade everything else; suppress INTERNAL
                                            # forces between members, show only external
  # massless-spring FBD (springs review 8) = an equal/opposite endpoint force pair:
  #   T <- /\/\/\ -> T
  ```
- **`overlays/deformation.py`** (springs review 4) holds the spring
  *visualisation* (kept OUT of `LinearSpring.build`): `spring_deformation_marker`,
  `spring_length_dimension` (the `<--L0-->` / `<---L--->` dimension lines),
  `spring_force_pair`. Rationale: educational annotations are overlays, not part
  of the physical asset.
- **`GraphBinding` already serves spring graphs** (`x-t`, `v-t`, `a-t`, `F-x`,
  `KE/PE/E-t`, phase portrait `v-x`) via signals over `SystemState.observables`
  (this milestone's main revision) — no change needed beyond noting it.
- **Overlays split into `overlays/common`, `overlays/mechanics`,
  `overlays/fluids`** (fluids review 23) so pressure/level/flow overlays live
  with the fluid domain while FBD/kinematics/graphs stay shared.

## Revisions (presentation review 2026-09-05) — MUST

- **Views are spec-driven and render supplied values — they never calculate**
  (M18). Add to `overlays/views.py`:
  - `EnergyView` / `EnergyComparisonView` — bars/curves from supplied
    `EnergyState` values; assert `E_A=E_B` only if the caller says conservation
    applies.
  - `MomentumComparisonView` — before/after arrows + resultant from supplied
    `MomentumState`; highlights equal totals when told.
  - `WorkEnergyLedger` — `K_i + ΣW = K_f` from supplied work terms.
  - `AngularMomentumView` — from `AngularMomentumViewData(about, before, after,
    omega_after, conserved)`.
  - `InstantaneousCenterOverlay` (from `InstantaneousCenterSpec` +
    `PointVelocitySpec`) reusing M1.6 `RigidBodyVelocityField`.
- **`VectorSpec` rendering (MUST):** role→colour (Rule 2), optional
  components/angle/perpendicular marker (`perpendicular_to`). **`EquationStep`**
  reveals/transforms an `EquationSpec` and co-highlights the named asset.
- **`BindingSpec` (MUST):** bind a supplied quantity to a visual property
  (`state.spring.extension → spring.geometry.length`); one state update refreshes
  all bound visuals — no hand-synchronised updaters.
- **Rationale:** the productivity win is a small supplied payload → a rich,
  synchronized visual, with zero physics inside the view.

## Goal

Make explanation assets **first-class** (vision §21). These are drawn from the
same keypoints/state the bodies already expose, so no scene rebuilds an FBD,
velocity field, or graph by hand. Includes the powerful generic `GraphBinding`
(§22) that syncs a moving body to a live plotted cursor.

## `overlays/` package layout

```
overlays/
  forces.py      # FBD (delegates to fbd.py), force-sum, reaction pair
  kinematics.py  # velocity, acceleration, trajectory trail, ghost positions,
                 # tangential-normal frame, polar basis, time markers
  rotation.py    # omega arc, alpha arc, instantaneous-centre, rolling velocity field
  energy.py      # EnergyPanel (KE/PE/total bars or curves)
  momentum.py    # momentum vector, system momentum sum, COM marker/trail, boundary
  contact.py     # contact magnifier, static-friction meter, relative-velocity indicator
  graphs.py      # GraphBinding (§22)
  frames.py      # (thin) reference-frame glyph re-export for overlays (M14 owns physics)
```

## Kinematics overlays (`overlays/kinematics.py`)

```python
def velocity_vector(body, scale=1.0, frame_label=None) -> VGroup:
    v = body._state.velocity; anchor = body.keypoint("CM")
    Arrow(anchor -> anchor + scale*v, colour=COLOR_VELOCITY, stroke_width=4)
    + MathTex("v") + optional frame label (Rule 6)
def acceleration_vector(body, scale=1.0) -> VGroup:  # COLOR_ACCEL, "a"
def trajectory_trail(body, traj, t0, t1, n=60) -> VMobject:   # sampled path polyline
def ghost_positions(body, traj, times) -> VGroup:   # faded copies at each time
def tangential_normal_frame(surface, s) -> VGroup:  # t,n arrows on a curve (n-t coords)
def polar_basis(origin, point) -> VGroup:           # r-hat, theta-hat at a point
def time_markers(trail, traj, times) -> VGroup:     # dots + t labels on a trail
```

## Rotation overlays (`overlays/rotation.py`)

```python
def rolling_velocity_field(disk, v_cm, points=("top","3","9")) -> VGroup:
    # EXACT Rule 5: for each rim point, v = perp-to-(point - contactP), (r_y,-r_x).
    # contact point marked v=0. Reuses disk.point_velocity from M3.
def instantaneous_center(disk) -> VGroup:           # mark the contact P as ICR + label
def omega_arc(body) -> VGroup:                      # COLOR_ANGULAR curved arrow
def alpha_arc(body) -> VGroup:                      # COLOR_ANGULAR_ACCEL
```

## `GraphBinding` (`overlays/graphs.py`) — the generic sync tool (§22)

```python
@dataclass
class GraphBinding:
    x: str | Callable[[State], float]   # "time" or lambda s: s.theta
    y: str | Callable[[State], float]   # lambda s: s.extra["N"]
    x_range=(0,1); y_range=(0,1); x_label="t"; y_label="y"; cursor=True
    def build(traj, t0, t1, n=100) -> VGroup:
        axes = Axes(x_range,y_range, labels)
        curve = plot [ (val(x,s), val(y,s)) for s at sampled t ]
        cursor_dot = Dot at first point (if cursor)
        return VGroup(axes, curve, cursor_dot)
    def bind(scene, tracker):           # move cursor_dot as tracker.value advances
        updater: s = traj.state_at(tracker.value); cursor.move_to(axes.c2p(x(s),y(s)))
# One component serves: f-vs-F, N-vs-θ, ω-vs-t, α-vs-t, energy-vs-t, orbit V_eff,
# spring x-v phase portrait, collision velocity-space, chain-length-over-edge.
```

## Energy / momentum overlays

```python
# energy.py
def energy_panel(get_ke, get_pe, t0, t1) -> VGroup:   # stacked bars or curves vs t
# momentum.py
def momentum_vector(body, scale) -> VGroup            # p = m v arrow
def system_com_marker(bodies) -> VGroup               # COM Dot (mass-weighted)
def com_trail(bodies, traj_map, t0,t1) -> VMobject
def momentum_sum(bodies) -> VGroup                    # resultant p arrow
def system_boundary(bodies, pad=0.3) -> VMobject      # dashed boundary (§18)
```

## Assembly convenience

```python
Assembly.overlay(kind, **kw) -> VGroup:   # "velocity"/"omega"/"fbd"/"com"/"graph"...
    dispatch to the right overlay factory using this assembly's bodies/state
```

## Demo — Kepler equal-areas teaser (feeds probe B / M13)

```python
orbit = OrbitPath(...); planet = Particle(...)          # OrbitPath lands in M13
radius = polar_basis(sun.CM, planet.CM)
graph  = GraphBinding(x="time", y=lambda s: s.extra["r"], ...).build(traj,0,T)
# animate planet along traj; radius vector + graph cursor track it automatically
```

## Tests (`tests/test_assets_overlays.py`)

```
- velocity_vector length ∝ |v|, colour COLOR_VELOCITY, anchored at CM.
- rolling_velocity_field: each arrow ⟂ (point - contactP) (dot≈0), contact v=0.
- trajectory_trail has n points on the analytic path.
- GraphBinding.build plots the curve; cursor starts at (x(s0),y(s0));
  after bind+advance, cursor is at (x(s1),y(s1)) (assert via axes.c2p inverse).
- system_com_marker at mass-weighted mean of body CMs.
- momentum_vector length ∝ m|v|.
```

## Render smoke
A rolling disk with the Rule-5 velocity field + a synced ω-vs-t GraphBinding;
frame confirms right angles at the rim and the cursor on the curve.

## Use cases unlocked
Every teaching overlay (FBD/velocity/accel/omega/energy/momentum/COM/graph) is
reusable and state-driven. `GraphBinding` synced to any body powers N-vs-θ,
energy-vs-t, phase portraits — used heavily by M12/M13/M14.
