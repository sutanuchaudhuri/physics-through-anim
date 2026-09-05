# M2 — Supports, Contact Semantics, Conveyor

Status: **DRAFT FOR REVIEW**
Depends on: M1. Files touched: `kinds.py` (+`ContactGeometry`,`MaterialPairing`,
`ContactPhase`), `supports.py` (+`Wall`,`Ceiling`,`Incline`,`Conveyor`),
`contact.py` (NEW), `assembly.py` (placement on wall/ceiling/incline), `__init__.py`.

## Revisions (architecture review 2026-09-05)

> The sections below are **superseded where they conflict** with this block.

- **`Contact` is NOT a `PhysicsAsset`** (review 2). A contact is a *relationship*,
  not a drawable. It becomes a pure semantic dataclass with **no `mobject`**;
  the dot/tangent/normal visuals move to `overlays/contact.py`
  (`contact_marker`, `contact_frame`). Rationale: keeps entity vs relation
  boundaries clean and prevents the trouble the review flags for M7 edges.
  ```python
  @dataclass
  class Contact:                      # pure semantic — no VGroup
      body: AssetRef; surface: SurfaceRef
      locator: ContactLocator                    # review 9
      kinematics: ContactKinematics = STICKING   # review 8
      friction: FrictionModel = COULOMB          # review 8
      lifecycle: ContactLifecycle = ACTIVE       # review 8
      def frame_at(self, system_state) -> ContactFrame:   # point/tangent/normal
          return self.locator.locate(system_state)
  ```
- **`ContactRegime` is split** (review 8) into three orthogonal enums:
  `ContactKinematics {STICKING, SLIDING, ROLLING_NO_SLIP, ROLLING_WITH_SLIP}`,
  `FrictionModel {FRICTIONLESS, COULOMB, CUSTOM}`, and
  `ContactLifecycle {ESTABLISHING, ACTIVE, SEPARATING}`. Rationale: `SMOOTH`
  (a friction law), `SLIDING` (kinematics), and `ROLLING_NO_SLIP` (a relative-
  velocity condition) were three different concepts in one enum.
- **`ContactPersistence.FIXED/MOVING` → `ContactLocator` protocol** (review 9),
  because "fixed" was ambiguous (world vs body-A vs body-B vs surface coord):
  ```python
  class ContactLocator(Protocol):
      def locate(self, system_state) -> ContactFrame: ...
  FixedWorldPoint(p) | BodyKeypoint(PointRef) | SurfaceCoordinate(SurfaceRef, s_of_t)
      | ClosestPoint(a, b) | EdgePoint(SurfaceRef)
  # cylinder on an edge: geometric location = FixedWorldPoint(edge.E),
  #                      material point = CHANGING (kinematics), naturally expressed.
  # rolling on an incline: SurfaceCoordinate(incline.surface, s(t)).
  ```
- **`Surface` protocol is introduced HERE, not M8** (review 10): create
  `surfaces.py` now with `LineSurface`, `FloorSurface`, `InclineSurface`
  exposing `point_at/tangent_at/normal_at/curvature_at/length`. Rationale: M2
  contact already needs tangents/normals; otherwise M2 ships `Incline.normal()`,
  `Wall.contact_at()`, `Floor.contact_under()` only for M8 to replace them.
- **A surface is geometry attached to an entity, not a `Support`** (review 11):
  a support/body *owns* a surface (`floor.surface("top")`, `wedge.surface(
  "incline")`), so moving walls/wedges/belts work later. The `Incline.normal()`/
  `surface_at()`/`Wall.contact_at()`/`Floor.contact_under()` helpers below are
  **replaced** by `owner.surface(name).<method>`.
- **`MotionState` trimmed to `AT_REST | MOVING`** (review 7); `CONSTRAINED` and
  `ABOUT_TO_MOVE` are not motion states — that information moves to relations
  (a `Constraint`, or a friction-threshold condition on a `Contact`). M1's
  values remain as **deprecated aliases** for compatibility.

## Goal

Add the rest of the static environment (wall, ceiling, incline, conveyor) and a
**first-class `Contact`** object with the *richer* semantics the vision calls
for — separating the geometric contact location from the material point that
occupies it — while implementing only what M2 needs and leaving the enum room
for M7/M8 to grow.

## New enums (extend `kinds.py`)

```python
class ContactGeometry(StrEnum):     # shape of the contact
    POINT = "point"                 # disk on plane, ball on ball
    PATCH = "patch"                 # block foot on floor
    LINE  = "line"                  # rod lying flat, cylinder side on plane

class MaterialPairing(StrEnum):     # does the touching material change?
    SAME     = "same"               # resting block: same atoms in contact
    CHANGING = "changing"           # rolling/sliding: contact atoms change

class ContactPhase(StrEnum):        # lifecycle of a contact (M7 uses fully)
    ESTABLISHING = "establishing"
    ACTIVE       = "active"
    SEPARATING   = "separating"
```

> The vision's target model is
> `Contact{geometry, regime, location_motion, material_pairing, phase}`.
> M2 ships `geometry + regime + location_motion(ContactPersistence) +
> material_pairing`; `phase` defaults to `ACTIVE` and becomes meaningful in M7.

## `contact.py` (NEW)

```python
@dataclass
class Contact(PhysicsAsset):
    """A relationship asset: body-touches-surface at a (possibly moving) point."""
    name: str = "contact"
    dynamics = STATIC
    body_ref: str = ""              # "block"          (assembly-namespaced)
    surface_ref: str = ""           # "floor"
    at: tuple[float,float]|str = "auto"   # world point, or a keypoint name
    regime: ContactRegime = RESTING
    geometry: ContactGeometry = POINT
    location: ContactPersistence = FIXED  # FIXED patch vs MOVING sweep
    pairing: MaterialPairing = SAME
    phase: ContactPhase = ACTIVE
    mu: float = 0.0
    show_marker: bool = True        # a Dot at the contact point
    show_frame: bool = False        # tangent/normal indicator
    tangent: tuple|None = None      # unit tangent; None => infer from surface
    normal:  tuple|None = None

    def build():
        p = resolve_point()                       # world coords
        set_keypoint("P", p)
        g = VGroup()
        if show_marker: g.add(Dot(p, colour=WHITE, r=0.05))
        if show_frame:  g.add(_tangent_normal_glyph(p, tangent, normal))
        return g

    # helper: an arrow-pair glyph showing t (along surface) and n (out of surface)
```

Rendering the normal/friction forces stays in the FBD layer: a `Contact`
*declares* them on the body via `add_force` when a scene asks, e.g.
`contact.apply_reaction(body, normal_label="N", friction_label="f")`.

Contact truth table (documented, drives defaults):

| Situation | geometry | location | pairing |
| --- | --- | --- | --- |
| block resting on floor | PATCH | FIXED | SAME |
| block sliding on floor | PATCH | MOVING | CHANGING |
| wheel pure rolling | POINT | MOVING | CHANGING |
| rod pinned at hinge | POINT | FIXED | SAME |
| rod foot sliding | POINT | MOVING | CHANGING |
| cylinder on sharp edge | POINT | FIXED (edge) | CHANGING (body) |
| bead on wire | POINT | MOVING | — |
| projectile | (no Contact asset) | — | — |

## New supports (`supports.py`)

```python
@dataclass
class Wall(Support):
    name="wall"; x=-5.0; half_height=2.8; side="right"  # hatch faces +x
    hatch=True; color=GRAY
    build(): vertical Line at x; hatch ticks on `side`;
             keypoints surface/top/bottom; contact_at(y) -> [x,y,0]

@dataclass
class Ceiling(Support):
    name="ceiling"; y=3.0; half_width=5.5; hatch=True   # ticks point down
    build(): horizontal Line at y; keypoints surface/left/right;
             anchor(x) -> [x,y,0]              # for hanging ropes/hinges (M4)

@dataclass
class Incline(Support):
    name="incline"; angle_deg=30.0; length=5.0; mu=0.0
    on_floor=True; base=(-2.0, GROUND_Y); thickness=0.0; hatch=True
    build():
        theta=radians(angle_deg); dir=(cos,sin)
        foot=base; apex=base+length*dir
        draw incline Line foot->apex (+ optional filled wedge to floor)
        keypoints: foot, apex, surface_mid,
                   surface_at(s) registered lazily via method
        normal_dir = (-sin, cos)     # out of the slope
    surface_at(s in [0,1]) -> foot + s*length*dir      # for placing a body
    normal() -> (-sin(theta), cos(theta))
    slope_down() -> (cos(theta), -sin(theta)) ... etc  # for force directions

@dataclass
class Conveyor(Floor):               # a Floor whose surface moves
    name="conveyor"; belt_speed=0.0; direction=+1; mu=0.4
    # belt_speed 0 => MotionState.AT_REST (frozen); >0 => MOVING (animate)
    motion_state property = MOVING if belt_speed>0 else AT_REST
    build(): Floor line + chevron/hatch marks that scroll under animate()
    animate(scene, run_time): 
        if AT_REST: no-op (frozen)          # "conveyor not moving" case
        else: scroll chevrons via ValueTracker+updater at belt_speed*direction
```

## Assembly placement (extend `_place_on`)

```python
_place_on(body, support):
    match support:
      Floor|Conveyor: drop bottom to y; contact FIXED (PATCH)
      Incline:        rotate body by angle; seat CM on surface_at(s);
                      register body "contact" at seat; contact MOVING if body rolls
      Wall:           push body's side to wall.x; contact at that side
      Ceiling:        (M4) attach point for rope/hinge
```

## Demo scene (pseudocode) — the three conveyor cases (Rule 16 `together`)

```python
class M2ConveyorCases(RollingLessonScene-like plain Scene):
    def build_case(belt):
        a = Assembly()
        conv = Conveyor(belt_speed=belt)
        blk  = Block(width=1.0, label="m")
        a.add(conv); a.add(blk, place_on=conv)
        c = Contact(body_ref="block", surface_ref="conveyor",
                    at="block.contact", regime=RESTING if belt==0 else SLIDING,
                    location=FIXED, pairing=SAME if belt==0 else CHANGING, show_frame=True)
        a.add_relation(c)               # (assembly stores contacts alongside members)
        return a
    segments = [floor-like belt=0, moving belt=2, stopped belt=0-after-moving]
    play_subscenes(together) + each case shows FBD (mg, N) + contact glyph
```

## Tests (`tests/test_assets_supports.py`)

```
- Incline.surface_at(0)==foot, surface_at(1)==apex; normal is unit & perp to slope.
- Wall/Ceiling keypoints at expected coords; contact_at/anchor return right points.
- Conveyor(belt_speed=0).motion_state == AT_REST; >0 => MOVING.
- Contact.build registers "P"; marker present iff show_marker.
- Contact truth-table defaults: block-on-floor => PATCH/FIXED/SAME.
- placement on incline rotates block and seats CM on surface (CM above line by h/2).
```

## Render smoke
`M2ConveyorCases` at low quality; extract a frame; confirm belt chevrons, block
resting, contact glyph + FBD; delete temp artifacts.

## Use cases unlocked
Body on floor / moving conveyor / stopped conveyor; block on incline (static FBD);
wall- and ceiling-mounted setups for M4; the contact vocabulary that M3 (rolling
`P`), M7 (contact switch/separation) and M8 (edges) all extend.
