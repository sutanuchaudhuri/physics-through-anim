# M8 — Curved Surfaces / Table / Edge / Track / Peg / Slot / Rail

Status: **DRAFT FOR REVIEW**
Depends on: M1–M7. Files: `surfaces.py` (NEW — the unifying `Surface` protocol),
`supports.py` (Floor/Incline re-expressed as surfaces), `contact.py`
(contact point from `Surface.point_at`), `constraints.py` (SLOT/RAIL guides).

## Revisions (architecture review 2026-09-05)

- **The `Surface` protocol is introduced in M2, not here** (review 10). M8 now
  **extends** it with the curved/edge/track/peg/slot specialisations; the
  `point_at/tangent_at/normal_at/curvature_at` interface below is already live
  from M2 (`LineSurface/FloorSurface/InclineSurface`).
- **`ParametricSurface` must NOT subclass `Support`** (review 11). A surface is
  **geometry owned by an entity**, and that entity may be *moving* (wedge, belt,
  cylinder rim, wall). So `CircularTrack`/`ConvexSurface`/`ConcaveSurface`/
  `Table` own a surface (or expose `.surface(name)`) rather than *being* a
  static support. World contact geometry = `surface local geometry` ∘
  `owner pose/state`. Rationale: Krotov has moving walls/wedges/guides/belts;
  binding surfaces to static supports would not scale.
  ```python
  # geometry attached to any entity, static OR moving:
  wedge.surface("incline") -> Surface        # frame follows wedge.pose/state
  disk.surface("rim")      -> Surface        # for tangent/rolling contact
  table.surface("top")     -> Surface
  ```
- Contact points come from a `SurfaceCoordinate` / `EdgePoint` **`ContactLocator`**
  (M2, review 9), so normal/friction directions are always the surface frame —
  no hardcoded `UP` (consistent with Rule 5).

## Revisions (kinematics review 2026-09-05) — MUST

- **Body-on-track / bead-on-wire MUST use `PathPoseBinding`** (M1.6): the AI
  supplies `s(t)`; the binding sets `position = path.point_at(s)` and
  `orientation = tangent` automatically. Seating a body on a surface MUST use
  `SurfacePoseBinding`. No scene hand-computes position/orientation along a curve.
- **Rationale:** bead-on-wire, car-on-road, block-on-circular-track, roller
  coaster, particle-on-parabola, and cylinder-leaving-a-curved-table are all the
  same path-following kinematics — one binding, supplied `s(t)`.

## Goal

Environment geometry is where textbook mechanics gets its mileage. Introduce one
**surface interface** so `Floor`, `Incline`, `CircularTrack`, `RoundedEdge`,
`Table`+`SharpEdge` are all specialisations, and contact mechanics (normal,
tangent, curvature, separation) come "for free" from that interface (vision §4).

## The unifying interface (`surfaces.py`)

```python
class Surface(Protocol):
    def point_at(self, s: float) -> np.ndarray:      # s in [0,1] along the surface
    def tangent_at(self, s: float) -> np.ndarray:    # unit tangent
    def normal_at(self, s: float) -> np.ndarray:     # unit outward normal
    def curvature_at(self, s: float) -> float:       # 1/R (0 for flat)
    def length(self) -> float

# Mixin that gives any curve-based support these four for free:
@dataclass
class ParametricSurface(Support):
    curve: Callable[[float], np.ndarray]   # s->world point
    def point_at(s):   return curve(s)
    def tangent_at(s): finite-difference curve, normalise
    def normal_at(s):  rotate tangent 90° (outward convention), normalise
    def curvature_at(s): second-difference / |r'|^3
```

Re-express existing supports on top of it (no behaviour change for callers):
```
Floor:   point_at(s)=lerp(left,right,s); tangent=+x; normal=+y; curvature=0
Incline: point_at(s)=foot + s*L*dir;    tangent=dir; normal=(-sin,cos); curvature=0
```

## New surfaces

```python
@dataclass
class CircularTrack(ParametricSurface):
    name="track"; center=(0,0); radius=2.0; arc=(0,2π); inner=False
    curve(s) = center + R*(cos(arc lerp), sin(arc lerp))
    normal outward (inner=True flips) -> loops, beads, "losing contact" scenes
@dataclass
class ConvexSurface(ParametricSurface):   # a hill: particle/cylinder can leave it
    name="hill"; ...
@dataclass
class ConcaveSurface(ParametricSurface):  # a bowl: oscillation
@dataclass
class Table(Support):
    name="table"; top_y=0.5; left=-3; right=1.0; leg=True
    build(): table top Line + legs; keypoints top_left, top_right, edge=right end
    edge() -> SharpEdge at (right, top_y)
@dataclass
class SharpEdge(Support):
    name="edge"; at=(0,0)
    build(): Dot/corner glyph; keypoint "E"
    # a body pivots about / separates at E; contact is POINT, FIXED-geometry,
    # CHANGING-material (M2 truth table row).
@dataclass
class RoundedEdge(CircularTrack):  # small-radius arc: smooth normal evolution
@dataclass
class Peg(Support):                # pendulum string catches on it (M4 rope + M7 event)
    name="peg"; at=(0,0); radius=0.06
@dataclass
class Rail(ParametricSurface):     # slider constrained to a line/curve
@dataclass
class Slot(Support):               # bead/rod slot: two parallel guide lines
    name="slot"; from=(...); to=(...); gap=0.2
    guide_constraint() -> Constraint(SLOT, ...)
```

## Contact from a surface (enrich M2 `Contact`)

```python
Contact(..., surface: Surface|None=None, s: float|None=None):
    if surface and s is not None:
        P = surface.point_at(s); tangent=surface.tangent_at(s); normal=surface.normal_at(s)
    # normal/friction ForceSpec directions taken from the surface frame -> always
    # correct even on a curve (no hardcoded UP), consistent with Rule 5.
separation_imminent(surface, s, N_value) -> bool:   # N<=0 criterion (scene supplies N)
```

## Flagship demo — cylinder reaches a table edge (PROBE A, full)

```python
class M8TableEdge(Scene):
    a=Assembly(); table=Table(top_y=0.5, right=1.0); cyl=Cylinder(radius=0.5)
    a.add(table); a.add(cyl, place_on=table.top_surface())      # rolls on the top
    edge=table.edge(); a.add(edge)
    # timeline (times supplied by a scene-side trajectory / analytic criterion):
    a.timeline.add(Event(t=2.0, kind=CONTACT_SWITCH, participants=("cyl","edge")))
    a.timeline.add(Event(t=2.6, kind=SEPARATION,     participants=("cyl","edge")))
    # phases: roll on top -> pivot about edge E (contact POINT/FIXED) -> N->0 ->
    #         free rigid-body projectile+rotation -> (ground impact if floor added)
    a.play_events(self, {"cyl": SampledTrajectory(precomputed_edge_fall)})
    # FBD updates each phase: weight at CM always; normal at P (top) then at E; gone after sep.
    finish_with_narration()
```

## Tests (`tests/test_assets_surfaces.py`)

```
- Floor/Incline via Surface: point_at endpoints, tangent/normal unit & correct,
  curvature==0.
- CircularTrack: point_at on the circle; normal points outward (inner flips);
  curvature ≈ 1/R.
- ConvexSurface normal points away from centre; ConcaveSurface toward.
- Table.edge() at (right, top_y); SharpEdge registers "E".
- Contact(surface, s): P/tangent/normal match surface frame; normal ForceSpec
  direction == surface.normal_at(s).
- separation_imminent True when N<=0.
```

## Render smoke
`M8TableEdge`: three frames — rolling on top; pivoting at the edge (N at E);
airborne (no N, still rotating). The contact-topology change is visible.

## Use cases unlocked
Ball over convex hill / particle on sphere (N=0 separation), loops & beads,
bowls, rope-over-peg, slot/rail constraints, and PROBE A in full. Curved-contact
normal/friction directions are now always geometrically exact.
