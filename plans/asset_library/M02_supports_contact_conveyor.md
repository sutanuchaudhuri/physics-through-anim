# M2 — Supports, Contact Semantics, Conveyor

Status: **DRAFT FOR REVIEW**
Depends on: M1. Files touched: `kinds.py` (+`ContactGeometry`,`MaterialPairing`,
`ContactPhase`), `supports.py` (unified `Wall` primitive + `Floor` preset),
`environment.py` (`Ceiling`/`Incline`/`Corner`/`Conveyor` presets), `surfaces.py`
(`LineSurface`/`FloorSurface`/`InclineSurface`), `contact.py` (NEW),
`overlays/contact.py` (glyphs), `assembly.py` (placement on any wall + the
**non-penetration** clamp), `__init__.py`.

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

Add the rest of the static environment and a **first-class `Contact`** object
with the *richer* semantics the vision calls for — separating the geometric
contact location from the material point that occupies it — while implementing
only what M2 needs and leaving the enum room for M7/M8 to grow.

**The static environment is one family of oriented boundaries, not a bag of
special cases.** A horizontal boundary is a floor (or a ceiling, facing down); a
vertical boundary is a side-wall; a boundary at angle θ is a ramp/incline; two
boundaries meeting is a corner; several make a channel, V-groove or box. They
differ only by **orientation and which way the outward normal points** — so they
share one primitive (`Wall`) with named presets (`Floor`, `Ceiling`, `Incline`,
`Conveyor`). **No wall ever gets a free-body diagram** — a wall is
`BodyDynamics.STATIC`, owns a `Surface`, and only supplies a *reaction* to the
touching body's FBD. See "New supports" for the full taxonomy.

**Walls and floors are impenetrable.** A hard geometric invariant — *no body may
be rendered on the solid side of any wall/floor* — is enforced at placement and
on every pose update (see "Non-penetration constraint"). Contact is tangency,
never overlap; a round body rolling into a wedge seats against *both* walls
instead of piercing either.

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

### A wall is one family: a static boundary at any orientation (MUST)

> **A "wall" is just a static boundary surface placed at some position and
> orientation. Floor, ceiling, side-wall, ramp and the sides of a box/corner are
> all the *same thing* at different angles — do not model them as unrelated
> classes.** And: **nobody ever draws a free-body diagram of a wall.** A wall is
> `BodyDynamics.STATIC`; it has no weight, carries no `ForceSpec`, and its
> `fbd()` is always empty. It only (a) *owns a `Surface`* (`point_at/tangent_at/
> normal_at`) and (b) contributes a **reaction** to the *body's* FBD (`N`, `f`).
> Arrows live on the body, never on the wall.

The one primitive is an oriented boundary; everything else is a named angle:

| Type | Orientation | Outward normal | Built as |
| --- | --- | --- | --- |
| **Floor** (horizontal wall, floor below) | θ = 0° | `+y` (up) | `Wall(angle_deg=0, facing="up")` |
| **Ceiling** (horizontal wall, room above) | θ = 0° | `−y` (down) | `Wall(angle_deg=0, facing="down")` |
| **Vertical wall** (left/right side) | θ = 90° | `±x` | `Wall(angle_deg=90, side="right")` |
| **Ramp / incline** (wall at angle θ) | θ = 30°… | `(−sinθ, cosθ)` | `Wall(angle_deg=θ)` / `Incline` |
| **Corner** (two walls meeting) | two angles | two normals | `Corner(a, b)` = a floor + a wall |
| **Channel / V-groove / box** | N walls | N normals | `VGroup` of walls (a composite) |
| **Conveyor** (a *moving-surface* wall) | θ = 0° | `+y` | `Conveyor(belt_speed=…)` |

`Wall` is therefore the general oriented boundary; `Floor`, `Ceiling`,
`Incline`, `Conveyor` are **thin, well-named presets** over it (kept for
readability and for the M1 `Floor` already shipped). Each exposes
`owner.surface(name)` so contact/tangent/normal come for free (review 10/11);
none of them ever declares a force on itself.

```python
@dataclass
class Wall(Support):                 # THE oriented static boundary (no FBD, ever)
    name="wall"; angle_deg=90.0      # 0 => horizontal, 90 => vertical, θ => ramp
    center=(-5.0, 0.0); length=5.6   # midpoint + extent along the surface
    facing="auto"; side="right"      # which way the outward normal / hatch points
    hatch=True; color=GRAY
    dynamics = STATIC                 # <- walls are never dynamic; fbd() is empty
    build(): Line along the θ direction through `center`; hatch on the solid side;
             keypoints surface(mid)/start/end
    surface(name="face") -> LineSurface(start, end)   # point/tangent/normal
    normal() -> (-sin θ, cos θ) flipped by `facing`   # outward unit normal
    contact_at(s in [0,1]) -> point on the surface    # for seating a body
    # NOTE: no weight, no ForceSpec, no self-arrows. A wall only *reacts*.

@dataclass
class Floor(Wall):     name="floor";   angle_deg=0.0; facing="up"     # M1 preset
@dataclass
class Ceiling(Wall):   name="ceiling"; angle_deg=0.0; facing="down"
    def anchor(x) -> [x, y, 0]                          # hang ropes/hinges (M4)

@dataclass
class Incline(Wall):                 # a wall at angle θ, seated on the floor
    name="incline"; angle_deg=30.0; length=5.0; mu=0.0
    on_floor=True; base=(-2.0, GROUND_Y); hatch=True
    build(): foot=base; apex=base+length*(cosθ,sinθ);
             draw surface foot->apex (+ optional filled wedge to the floor);
             keypoints foot/apex/surface_mid
    surface_at(s in [0,1]) -> foot + s*length*(cosθ,sinθ)   # place a body
    normal() -> (-sin θ, cos θ)                              # out of the slope
    slope_down() -> (cos θ, -sin θ)                          # for force directions

@dataclass
class Corner:                        # two walls meeting (e.g. floor + right wall)
    a: Wall; b: Wall                 # a composite RELATION, not a new primitive
    # renders both; a body in the corner has TWO reactions (one per wall) in ITS
    # FBD. The corner itself still has no FBD.

@dataclass
class Conveyor(Floor):               # a Floor (horizontal wall) whose surface moves
    name="conveyor"; belt_speed=0.0; direction=+1; mu=0.4
    # belt_speed 0 => MotionState.AT_REST (frozen); >0 => MOVING (animate)
    motion_state property = MOVING if belt_speed>0 else AT_REST
    build(): Floor line + chevron/hatch marks that scroll under animate()
    animate(scene, run_time):
        if AT_REST: no-op (frozen)          # "conveyor not moving" case
        else: scroll chevrons via ValueTracker+updater at belt_speed*direction
```

**Why this matters for the FBD layer:** because a wall never owns forces, the
FBD renderer iterates only over *dynamic* bodies. A wall's contribution appears
exclusively as the body's `N`/`f` reaction (declared via
`contact.apply_reaction(body, ...)`), so horizontal, vertical, angled and
corner walls all "just work" without any per-wall force bookkeeping. Adding a
new wall angle never touches the FBD code.

## Assembly placement (extend `_place_on`)

```python
_place_on(body, support):
    # One rule for every oriented boundary: seat the body's touching side onto the
    # wall's surface and align the body to the wall's tangent; the wall's outward
    # normal gives the reaction direction. Presets are just angles of this rule.
    match support:
      Floor|Conveyor (θ=0, up):   drop bottom to surface; contact FIXED (PATCH)
      Ceiling (θ=0, down):        raise top to surface; anchor point for M4
      Wall (θ=90):               push body's side onto the wall; contact along face
      Incline / Wall(θ):         rotate body by θ; seat CM on surface_at(s);
                                 register body "contact" at seat; MOVING if it rolls
      Corner(a, b):              seat against both walls; body gets TWO reactions
    # No branch ever adds a force to the support; reactions are declared on the body.
```

## Non-penetration constraint (MUST) — walls and floors cannot be pierced

> **Invariant (geometric, enforced by the renderer/assembly, not by dynamics):
> no dynamic body's geometry may cross to the *solid* (inward) side of any wall
> or floor. Contact is *tangency*, never overlap.** Walls and floors are
> impenetrable boundaries; "touching" means the signed distance from the body's
> surface to the wall is exactly zero, and "free" means it is positive on the
> wall's outward-normal side. A negative signed distance (penetration) is an
> invalid configuration that placement MUST correct and updates MUST never
> produce.

This is a **rendering/placement constraint**, not a force: it is pure geometry,
so it holds identically for a resting block, a seated cylinder, or a body driven
by an externally supplied `Trajectory` (M6). It complements — never replaces —
the contact reaction on the body's FBD.

### Signed distance (the one primitive)

For a wall with outward unit normal `n` and any surface point `q`, the signed
distance of a world point `p` is `d(p) = (p − q) · n`. For a body:

```
clearance(body, wall) = min over the body's extreme point(s) of d(p)
  • circle/cylinder (centre c, radius R):  clearance = (c − q)·n − R
  • block / polygon:                       clearance = min over vertices of d(vertex)
penetrates  ⇔  clearance < −ε          # ε a small tolerance
touches     ⇔  |clearance| ≤ ε
free        ⇔  clearance >  +ε
```

`Wall.normal()`/`Wall.surface()` already provide `n` and `q`, so every wall
angle (floor, ceiling, side-wall, ramp) uses the *same* test — nothing is
special-cased per orientation.

### Enforcement at assembly time (seating)

`_place_on` MUST leave every body with `clearance ≥ 0` against **every** wall in
the assembly, and `= 0` against the wall(s) it is declared to rest on:

```python
add(body, place_on=support|[supports]):
    seat body so clearance(body, s) == 0 for each declared support s
    assert clearance(body, w) >= -ε for EVERY wall w in the assembly   # no piercing
    # if seating on one wall would push the body through another, seat on BOTH
    # (promote to a multi-wall / corner seat) or raise a clear placement error.
```

### Seating a round body against two walls (the corner / wedge case)

A cylinder of radius `R` that touches two walls with outward normals `n₁, n₂`
and surface points `q₁, q₂` sits with its **centre on both offset lines** (each
wall pushed out by `R` along its normal):

```
(c − q₁)·n₁ = R   and   (c − q₂)·n₂ = R
⇒ solve the 2×2 linear system for c  (unique when n₁ ∦ n₂)
contact points:  P_i = c − R·n_i           # feet of the perpendiculars
```

Example — **a floor (θ=0) and a wall at 30° forming a wedge, a cylinder rolling
into the corner:** as the cylinder rolls down the floor toward the ramp its
centre stays at height `R` (floor contact). It keeps rolling until the *second*
clearance `(c − q₂)·n₂ − R` reaches 0; at that instant the corner seat solves
both equations at once and the centre stops at the wedge apex offset. The
cylinder now touches **both** surfaces (two contacts, two reactions in its FBD)
and has **not** penetrated either — the renderer clamps the centre to the
two-line intersection, so no rolling update can drive it through a wall.

### Enforcement during updates (rolling / trajectory)

Every pose update (a `RollingPoseBinding`, a `FollowTrajectory`, M6 frames) MUST
re-assert non-penetration after computing the target pose:

```
apply(target_pose):
    p = target_pose
    for each wall w the body can contact:
        if clearance(body_at(p), w) < 0:        # would pierce w
            project p back onto clearance == 0 for w   (move along +n by |clearance|)
            activate/keep the contact with w           # picks up the extra reaction
    set_pose(p)      # absolute → still drift-free
```

Because the projection is along the wall normal and the body is re-seated to
tangency, contact is *maintained* (rolling stays glued to the surface) and a
body entering a corner naturally transitions from one contact to two — never
overlapping. The dynamics (which `ω`, which reaction magnitudes) remain
externally supplied; only the *geometry* is clamped here.

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
- Wall family is one primitive: Floor==Wall(θ=0,up), Ceiling==Wall(θ=0,down),
  vertical==Wall(θ=90); each normal() is unit and points the expected way.
- No wall has an FBD: Wall/Floor/Ceiling/Incline/Conveyor carry no ForceSpec and
  fbd() is empty for every orientation (STATIC).
- Incline.surface_at(0)==foot, surface_at(1)==apex; normal is unit & perp to slope.
- Wall/Ceiling keypoints at expected coords; contact_at/anchor return right points.
- Corner renders two walls; a body placed in it gets two reactions in ITS FBD.
- Conveyor(belt_speed=0).motion_state == AT_REST; >0 => MOVING.
- Contact.build registers "P"; marker present iff show_marker.
- Contact truth-table defaults: block-on-floor => PATCH/FIXED/SAME.
- placement on incline rotates block and seats CM on surface (CM above line by h/2).
- non-penetration: signed distance clearance(body, wall) >= 0 for every wall after
  placement; a block seated on a floor has clearance == 0 there and > 0 elsewhere.
- corner seat: a cylinder placed in a floor+ramp wedge has clearance == 0 against
  BOTH walls (centre solves the 2x2 offset-line system) and pierces neither.
- update clamp: a rolling/trajectory pose that would give clearance < 0 is projected
  back to tangency along the wall normal (centre never crosses the surface).
```

## Render smoke
`M2ConveyorCases` at low quality; extract a frame; confirm belt chevrons, block
resting, contact glyph + FBD; delete temp artifacts.

## Use cases unlocked
Body on floor / moving conveyor / stopped conveyor; block on an incline (wall at
θ); block against a vertical wall; a body seated in a corner (two reactions);
channels / V-grooves / boxes as composites of walls; wall- and ceiling-mounted
setups for M4 — all from one oriented-boundary primitive with **no per-wall FBD**.
Provides the contact vocabulary that M3 (rolling `P`), M7 (contact switch/
separation) and M8 (edges) all extend.
