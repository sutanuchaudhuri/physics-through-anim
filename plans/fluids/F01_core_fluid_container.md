# F1 — Fluid Region + Containers

Status: **DRAFT FOR REVIEW**
Depends on: `physics/core/` (state/refs), M6 `SystemState` (entities + fields).
Files: `fluids/regions.py`, `fluids/containers.py`.

## Goal

The primitive fluid asset is a **`FluidRegion`** (density + fill), separate from
the **container geometry** it occupies. A **`FreeSurface`** (not a keypoint hacked
into a reservoir) represents the water level. Flagship: static water in an open
rectangular tank.

## `regions.py`

```python
class FluidType(StrEnum):
    WATER = "water"; OIL = "oil"; MERCURY = "mercury"; CUSTOM = "custom"

@dataclass(frozen=True)
class FluidRegionState:                 # an EntityState variant (M6 union)
    free_surface_height: float
    volume: float | None = None
@dataclass
class FreeSurface:                      # owned by a FluidRegion; a level or a curve
    height: float = 0.0
    curve: Callable[[float], float] | None = None   # x -> y for non-flat surfaces
    def y_at(self, x): return curve(x) if curve else height

@dataclass
class FluidRegion(PhysicsAsset):        # renderable entity (fills its container)
    name="water"; density=1000.0; fluid=FluidType.WATER
    container: AssetRef | None = None   # geometry it fills
    fill_level: float = 1.0             # initial free-surface height
    color=None; fill_opacity=0.4
    def build():
        poly = fill the container profile up to free_surface.y_at(x)
        keypoints: surface_left, surface_right, bottom_mid
        return VGroup(poly)
    free_surface: FreeSurface = FreeSurface()
    def apply_state(state: FluidRegionState):   # move the surface; refill polygon (absolute)
        free_surface = replace(free_surface, height=state.free_surface_height); rebuild()
```

> Rationale (review 12/13): separates *fluid* from *container geometry*, so the
> same water fills a rectangular tank, a tapered tank, or a reservoir.

## `containers.py`

```python
@dataclass
class Container2D(PhysicsAsset):
    name="container"; dynamics=STATIC
    profile: list[Vec2] = field(default_factory=default_rect)   # open-top polyline
    def build():
        draw walls/bottom from profile; keypoints:
            bottom, left_wall, right_wall, free_surface_region, outlet, inlet
    def surface(self, name) -> Surface   # reuse the mechanics Surface protocol for walls
    def fill_polygon(self, level) -> list[Vec2]   # profile clipped at y=level (for FluidRegion)

# Convenience specialisations (mostly recipes / preset profiles):
class Tank(Container2D): ...
class OpenTank(Tank): ...            # no top
class ClosedTank(Tank): ...         # sealed (atmospheric vs gauge pressure later)
class Reservoir(Container2D): ...   # a large open body, one vertical wall = a dam face
```

## Demo — static water in an open tank

```python
class F1StaticTank(Scene):
    tank = OpenTank(profile=rect(w=4, h=3))
    water = FluidRegion(container="container", fill_level=2.0, density=1000)
    add(tank.mobject); add(water.mobject)          # water fills bottom 2 units
    # free-surface line + a level label via overlays/fluids/level.py (F-overlays)
    finish_with_narration()
```

## Tests (`tests/test_fluids_regions.py`)

```
- FreeSurface.y_at flat == height; curved uses the curve.
- FluidRegion.build fills up to fill_level; surface keypoints at that height.
- Container2D.fill_polygon clips the profile at a level (area increases with level).
- Container2D.surface("left_wall") returns a Surface (mechanics protocol reuse).
- apply_state(FluidRegionState(height=h)) moves the surface absolutely (no drift).
- FluidRegionState is a valid EntityState in a SystemState (M6 union).
```

## Render smoke
`F1StaticTank`: water fills the lower part of the tank; free-surface line at the
right height.

## Use cases unlocked
Any container + fluid split; the free-surface object every later fluid milestone
drives (draining, connected tanks, dam). Reuses the mechanics `Surface` protocol
for walls, and `SystemState` for the fluid entity/field.
