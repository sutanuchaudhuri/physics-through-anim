# F3 — Pipes + Connected Containers

Status: **DRAFT FOR REVIEW**
Depends on: F01, core signals/trajectory. Files: `fluids/pipes.py`,
`fluids/connections.py`, `fluids/overlays/flow.py`, `fluids/overlays/level.py`.

## Goal

A first-class **`Pipe`** and a semantic **`HydraulicConnection`** so two
containers can exchange fluid. `h1(t)`, `h2(t)`, `Q(t)` come from a `Trajectory`
provider (algebraic/analytic or precomputed) — the framework renders, it does
not derive. Flagship: two tanks with unequal levels equalising through a pipe.

## `pipes.py`

```python
@dataclass
class Pipe(PhysicsAsset):
    name="pipe"; path: list[Vec2] = field(default_factory=default_hpath)
    diameter=0.3; dynamics=STATIC
    def build(): draw the conduit along path (two offset polylines); 
        keypoints: inlet=path[0], outlet=path[-1], mid
    def surface(self, side) -> Surface           # pipe walls (Surface reuse)
    # useful signals (resolved from SystemState.observables):
    #   QuantityRef("pipe:1:Q"), ":v", ":p_in", ":p_out"
```

## `connections.py`

```python
@dataclass
class HydraulicConnection:                       # pure semantic relation (no mobject)
    from_region: AssetRef                         # "A.water"
    to_region: AssetRef                           # "B.water"
    pipe: AssetRef                                # "pipe1"
    # state variables live in SystemState.observables: h1(t), h2(t), Q(t), v_pipe(t)
```

## `overlays/flow.py`, `overlays/level.py`

```python
def flow_arrow(pipe, Q_signal) -> VGroup:         # arrow along pipe, size/dir ∝ Q(t)
def level_marker(region) -> VGroup                # a labelled line at the free surface
def level_delta(region_a, region_b) -> VGroup     # Δh dimension between two surfaces
```

## Demo — two connected tanks

```python
class F3ConnectedTanks(Scene):
    A = OpenTank(...).shift(LEFT*3); B = OpenTank(...).shift(RIGHT*3)
    wA = FluidRegion(container="A", fill_level=2.5)
    wB = FluidRegion(container="B", fill_level=0.8)
    pipe = Pipe(path=[A.outlet, B.inlet], diameter=0.25)
    conn = HydraulicConnection(from_region="A.water", to_region="B.water", pipe="pipe")
    # trajectory supplies h1(t) falling, h2(t) rising, Q(t) -> 0 as levels equalise:
    traj = SampledTrajectory(precomputed_equalise)      # or motion/analytic
    animate_trajectory(self, {"system": traj}, 0, T, run_time=8)
    add(flow_arrow(pipe, QuantitySignal("pipe:Q")), level_delta(wA, wB))
    # graph: Δh vs t, Q vs t via GraphBinding (M9)
    finish_with_narration()
```

## Tests (`tests/test_fluids_pipes.py`)

```
- Pipe keypoints inlet/outlet/mid on the path ends/middle.
- HydraulicConnection stores from/to/pipe refs (pure semantic; no mobject).
- flow_arrow direction flips with sign of Q; length ∝ |Q|.
- Applying a SystemState with h1<h2 moves both free surfaces to the sampled heights.
- level_delta magnitude == |hA - hB|.
- GraphBinding on QuantityRef("pipe:Q") plots Q(t) -> 0 at equalisation.
```

## Render smoke
`F3ConnectedTanks`: A drops, B rises, flow arrow shrinks toward zero as Δh → 0.

## Use cases unlocked
Communicating vessels, U-tubes, siphons (with F04 jet/efflux), and any
level-vs-time / flow-vs-time teaching — all driven by a supplied trajectory.
