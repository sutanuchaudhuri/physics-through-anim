# F5 — Control Volume / Bernoulli / Continuity

Status: **DRAFT FOR REVIEW**
Depends on: F01–F04, `loads.py` `DistributedLoadSpec`, M9 graphs. Files:
`fluids/control_volume.py`, `fluids/fields.py` (velocity), `fluids/overlays/*`.

## Goal

A **`ControlVolume`** with labelled **`Section`s** (ports) so continuity,
Bernoulli, Venturi area changes, momentum flux, and forces on pipe bends can be
taught from the same primitives. Flagship: a Venturi (area change → velocity and
pressure change).

## `control_volume.py`

```python
@dataclass
class Section:                         # an inlet/outlet port of a control volume
    at: PointRef; area: float; normal: Vec2
    # signals: QuantityRef("section:1:v"), ":p", ":mdot"
@dataclass
class ControlVolume(PhysicsAsset):
    name="cv"; boundary: list[Vec2] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)
    dynamics=STATIC
    def build(): dashed boundary (a SystemBoundary, reuse M9); label each Section
    def continuity(self) -> QuantityRef   # sum(rho*A*v) in == out (an OBSERVABLE, supplied)
```

## `fields.py` — velocity + profiles

```python
@dataclass
class VelocityField:
    fn: Callable[[float,float], Vec2]
    def as_field_state(self) -> FieldState
def velocity_profile(section, profile="uniform"|"parabolic") -> VGroup   # arrows across a section
def streamline(field, start, n=50) -> VMobject                          # integrate a path (geometry)
```

## Overlays

```python
def head_diagram(sections, traj) -> VGroup     # pressure/velocity/elevation heads (Bernoulli)
def flow_rate_label(section) -> VGroup
def momentum_flux_arrows(cv) -> VGroup         # ρQv in/out for pipe-bend force
def bend_force_resultant(cv) -> ForceSpec      # net force on the bend from momentum flux
```

## Demo — Venturi

```python
class F5Venturi(Scene):
    pipe = Pipe(path=venturi_profile)          # wide -> narrow -> wide
    cv = ControlVolume(boundary=venturi_region,
                       sections=[Section(inlet, area=A1, normal=+x),
                                 Section(throat, area=A2, normal=+x)])
    # trajectory/observables supply v1,v2,p1,p2 (continuity A1v1=A2v2, Bernoulli):
    traj = AnalyticTrajectory(venturi_state)   # algebraic relations, solver-free
    add(velocity_profile(cv.sections[0]), velocity_profile(cv.sections[1]))  # v2>v1
    add(head_diagram(cv.sections, traj))       # p2<p1
    graph = GraphBinding(x=QuantitySignal("section:1:A"),
                         y=QuantitySignal("section:1:v")).build(traj,0,T)
    finish_with_narration()
```

## Tests (`tests/test_fluids_control_volume.py`)

```
- Section stores area/normal; ControlVolume boundary is a dashed SystemBoundary.
- continuity observable satisfies A1 v1 ≈ A2 v2 for the supplied state.
- velocity_profile draws more/longer arrows at the smaller area (higher v).
- streamline follows the velocity field (tangent to fn along the path).
- bend_force_resultant magnitude == |ρQ(v_out - v_in)| for a bend test case.
- head_diagram shows p falling where v rises (Bernoulli), from supplied observables.
```

## Render smoke
`F5Venturi`: faster/denser velocity arrows at the throat; head diagram shows the
pressure dip; `v` vs `A` cursor tracks.

## Use cases unlocked
Continuity, Bernoulli, Venturi, pipe-area changes, momentum flux, forces on pipe
bends — all as compositions of `ControlVolume` + `Section` + supplied observables.
