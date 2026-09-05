# F2 — Hydrostatics + Pressure

Status: **DRAFT FOR REVIEW**
Depends on: F01, `loads.py` `DistributedLoadSpec` (M1.5 revision), M9 overlays +
`isolate`. Files: `fluids/fields.py`, `fluids/boundaries.py` (`DamWall`),
`fluids/overlays/pressure.py`.

## Goal

The important visualisation for a dam is the **hydrostatic pressure
distribution**, not the water polygon. Draw pressure growing with depth, then
collapse the distributed load into a **resultant** at the **centre of pressure**.
Flagship: a reservoir pushing against a vertical dam.

## `fields.py`

```python
@dataclass(frozen=True)
class FieldState:                       # goes in SystemState.fields (M6)
    fn: Callable[[float, float], float] # (x,y) -> scalar (pressure) or vector (velocity)
@dataclass
class PressureField:
    surface_y: float; density=1000.0; g=9.81; p_atm=0.0
    def pressure_at(self, x, y): return p_atm + density*g*max(0.0, surface_y - y)
    def as_field_state(self) -> FieldState
```

## `boundaries.py`

```python
@dataclass
class DamWall(PhysicsAsset):
    name="dam"; base=(0,GROUND_Y); height=3.0; thickness=0.6; batter=0.0
    dynamics=STATIC
    def build(): trapezoid wall; keypoints: heel, toe, top, water_face(s)
    def face(self) -> Surface           # the wetted face (mechanics Surface reuse)
```

## `overlays/pressure.py`

```python
def pressure_arrows_on_boundary(field, surface, n=8) -> VGroup:
    # arrows normal to the face, length ∝ pressure(depth) -> grows toward the bottom
    for s in linspace(0,1,n): arrow at surface.point_at(s), len ∝ field.pressure_at(P)
def distributed_pressure_load(field, surface) -> DistributedLoadSpec:
    # w(s) = pressure(depth(s)); direction = surface normal (into the wall)
def resultant_pressure_force(field, surface) -> ForceSpec:      # collapse the strip
    # F = ½ ρ g H^2 * width (for a flat vertical face), at the center of pressure
def center_of_pressure_marker(field, surface) -> VGroup:        # y_cp = 2/3 H below surface
```

## FBD choices (reuse M9 `isolate`)

```python
isolate(["dam"]):    hydrostatic resultant + dam weight + ground normal/friction/reactions
isolate(["water"]):  fluid weight + wall pressure force + bottom pressure force + p_atm
# fluid pressure is a DISTRIBUTED load -> DistributedLoadSpec (M1.5), then collapsed.
```

## Demo — reservoir against a dam

```python
class F2DamPressure(Scene):
    res = Reservoir(...); water = FluidRegion(container="container", fill_level=H)
    dam = DamWall(height=H+0.5)
    field = PressureField(surface_y=H, density=1000)
    add(res, water, dam)
    arrows = pressure_arrows_on_boundary(field, dam.face())      # grow with depth
    play(FadeIn(arrows))
    R = resultant_pressure_force(field, dam.face())              # collapse to one arrow
    cp = center_of_pressure_marker(field, dam.face())            # at 2/3 depth
    play(Transform(arrows, render(R)), FadeIn(cp))
    # then isolate(["dam"]) FBD
    finish_with_narration()
```

## Tests (`tests/test_fluids_hydrostatics.py`)

```
- PressureField.pressure_at: 0 at/above surface; ρg·depth below; linear in depth.
- distributed_pressure_load intensity ∝ depth; direction == face normal.
- resultant magnitude == ½ρg H² (per width) within tol; located at y_cp = surface - 2H/3.
- pressure arrows increase monotonically toward the bottom.
- isolate(["water"]) shows fluid weight + boundary pressure forces; isolate(["dam"])
  shows the resultant + support reactions.
```

## Render smoke
`F2DamPressure`: triangular pressure arrows on the dam face, then one resultant
at the centre of pressure.

## Use cases unlocked
Dam pressure, submerged gates, hydrostatic force on any wetted face, centre of
pressure, and the `DistributedLoadSpec` → resultant workflow reused by pipe-bend
forces (F05). Manometers later reuse `PressureField`.
