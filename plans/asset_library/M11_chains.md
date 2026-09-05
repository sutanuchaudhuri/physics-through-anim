# M11 — Chains / Distributed-Mass Bodies

Status: **DRAFT FOR REVIEW**
Depends on: M1–M10 (esp. M6 state, M8 edges, M9 COM overlays). Files:
`chain.py` (NEW), `overlays/momentum.py` (COM of a distributed body).

## Revisions (architecture review 2026-09-05)

- **Drop the special `ChainTrajectory` pathway** (review 24). The need for a
  separate `path_at(t)` was a warning that the generic trajectory contract was
  too narrow. Instead, the generic `SystemState` carries an entity-specific
  **`shape`** via `AssetState.shape` (M6 revision):
  ```python
  @dataclass(frozen=True)
  class ChainShapeState:
      path: Callable[[float], np.ndarray]     # material coord s in [0,1] -> world
  # rigid body: AssetState(shape=None); chain: AssetState(shape=ChainShapeState(...))
  # ONE Trajectory.state_at(t) -> SystemState feeds both; no animate_chain special case.
  ```
  Rationale: keeps a single `Trajectory.state_at(t) -> SystemState` contract for
  rigid bodies and distributed bodies alike; no bespoke animation path.
- `Chain` stays a **geometry** asset (renders `CONTINUOUS`/`LINKED` from the
  current shape); the shape's time evolution comes from the trajectory provider
  (`motion/analytic/` or a precomputed sample), not from inside the asset.

## Revisions (springs & fluids review 2026-09-05)

- **Generalise `Chain` to a `DistributedBody` base** (springs review 8). Any body
  with a material coordinate + evolving shape shares one abstraction:
  ```python
  class DistributedBody(PhysicsAsset):        # material coord s in [0,1] + shape
      render: DistributedRender = CONTINUOUS   # CONTINUOUS | LINKED
      def shape_state(self) -> object          # carried in AssetState.shape (M6)
  Chain(DistributedBody)         # links / continuous chain
  ElasticString(DistributedBody) # rubber string / cable with give
  MassiveSpring(DistributedBody) # the massive spring M10's LinearSpring is NOT
  FlexibleRod(DistributedBody)   # bendable rod
  ```
  Rationale: massive springs, elastic strings, chains and flexible rods are the
  same distributed-mass architecture; only the constitutive/visual details differ.
- Shape still travels in the generic `SystemState` via `AssetState.shape`
  (no special trajectory pathway — architecture-review revision above).

## Goal

Distributed-mass mechanics — a `Chain` with a material coordinate, two render
modes, and end keypoints. It opens a rich problem class (chain over a table
edge, chain falling, chain over a pulley). Solver-free: shape/positions come
from a scene-supplied trajectory of the material coordinate.

## `chain.py` (NEW)

```python
class ChainRender(StrEnum):
    CONTINUOUS = "continuous"    # smooth polyline / curve
    LINKED     = "linked"        # discrete visible links

@dataclass
class Chain(PhysicsAsset):
    name="chain"; mass=1.0; length=3.0; linear_density=None   # density=mass/length
    render=ChainRender.CONTINUOUS; n_links=20
    path: Callable[[float], np.ndarray] | None = None  # material-coord s in [0,1] -> world
    material_markers: tuple[float,...] = ()            # s values to tag (which piece is which)
    label="chain"
    def build():
        if path is None: default straight horizontal layout
        pts = [ path(s) for s in linspace(0,1,n) ]
        if CONTINUOUS: VMobject through pts
        else:          VGroup of `n_links` short capsules along pts
        keypoints: A=path(0), B=path(1), CM=mass-weighted mean of pts
        for s in material_markers: set_keypoint(f"mark@{s}", path(s))
        return group
    def set_path(new_path): rebuild (used each frame for motion)
    def com(): return keypoints["CM"]
    def portion(s0, s1) -> VMobject:      # highlight a sub-length (supported vs free)
    def material_marker(s) -> Dot         # a visible tag on one piece (vision §10)
```

## Distributed motion (via a path trajectory)

```python
# A ChainTrajectory maps time -> a path function (the whole shape evolves).
@dataclass
class ChainTrajectory:
    path_at: Callable[[float], Callable[[float], np.ndarray]]   # t -> (s -> world)
    def state_at(t)->State: return State(extra={})              # shape carried via path
Assembly.animate_chain(scene, chain, chain_traj, t0,t1, run_time):
    tracker=ValueTracker(t0)
    updater: chain.set_path(chain_traj.path_at(tracker.value))
    play(tracker -> t1)          # chain shape evolves; CM/markers tracked
```

## Flagship demo — chain falling over a table edge (PROBE C)

```python
class M11ChainOverEdge(Scene):
    a=Assembly(); table=Table(top_y=0.5, right=1.0); edge=table.edge()
    # path_at(t): part on the table (horizontal) + part hanging (vertical) past the edge,
    #             with the split point moving as the chain slides (supplied analytically).
    chain=Chain(length=3.0, render=CONTINUOUS, material_markers=(0.0,0.5,1.0))
    a.add(table); a.add(edge); a.add(chain)
    a.animate_chain(self, chain, ChainTrajectory(chain_over_edge_path), 0, T, run_time=6)
    # overlays: COM marker (M9) drifts; portion(0, s_split) highlighted as "supported",
    #           portion(s_split,1) as "free"; edge is the moving split (M8 SharpEdge).
    # material markers show which piece of chain is which as it pours over.
    finish_with_narration()
```

## Tests (`tests/test_assets_chain.py`)

```
- Chain.build: A=path(0), B=path(1); CM at mass-weighted mean of sampled points.
- CONTINUOUS => one VMobject; LINKED => n_links submobjects.
- material_markers register keypoints "mark@s" at path(s).
- set_path moves A/B/CM consistently (CM recomputed).
- portion(s0,s1) returns a sub-curve whose ends are path(s0),path(s1).
- linear_density defaults to mass/length.
```

## Render smoke
`M11ChainOverEdge`: three frames — mostly on table; half over the edge; mostly
hanging — with the COM marker and the two coloured portions visibly changing.

## Use cases unlocked
Chain over table edge / starting to slide, chain falling through a hole, chain
onto a scale (variable momentum flux — pairs with M12), chain picked up from
floor (variable-mass subsystem), chain over a pulley, folded chain, rope wrapping
a peg. Material markers make "which piece is which" legible. Completes PROBE C.
