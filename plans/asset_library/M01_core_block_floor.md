# M1 — Core + Block-on-Floor Slice  ✅ SHIPPED

Status: **DONE** (2026-09-05). This doc records the shipped API the rest of the
milestones build on. Code: `assets/physics/mechanics/{kinds,palette,base,fbd,bodies,supports,assembly}.py`.

## What exists

### `kinds.py` — StrEnums
```
BodyDynamics        = STATIC | DYNAMIC
MotionState         = AT_REST | MOVING | CONSTRAINED | ABOUT_TO_MOVE
ContactRegime       = NO_CONTACT | RESTING | SLIDING | ROLLING_NO_SLIP | SMOOTH
ContactPersistence  = FIXED | MOVING
Phase               = BEFORE | DURING | AFTER
ForceKind           = WEIGHT | NORMAL | FRICTION | APPLIED | TENSION | REACTION
```

### `palette.py`
```
COLOR_WEIGHT=PURPLE  COLOR_NORMAL=GREEN  COLOR_FRICTION=ORANGE
COLOR_APPLIED=YELLOW COLOR_TENSION="#0CA678" COLOR_REACTION="#868E96"
COLOR_VELOCITY=BLUE  COLOR_ANGULAR="#20C997" COLOR_ACCEL="#FF2D95"
FORCE_COLORS: dict[ForceKind, colour]
```

### `base.py` — the two foundations
```python
@dataclass(frozen=True)
class ForceSpec:
    kind: ForceKind
    at: str                       # keypoint name on the owning asset
    label: str                    # symbolic only (Rule 9)
    direction: tuple|str = "auto" # unit vector or keyword {up,down,left,right}
    magnitude: float|None = None  # relative arrow length; None -> default

@dataclass
class PhysicsAsset:
    name: str = "asset"
    label: str|None = None
    dynamics: BodyDynamics = DYNAMIC
    keypoints: dict[str,np.ndarray] = field(init=False)   # WORLD coords, 3D
    forces:    list[ForceSpec]      = field(init=False)
    mobject:   VGroup               = field(init=False)
    __post_init__:      self.mobject = self.build()
    build() -> VGroup:  # subclass builds geometry + fills keypoints (raise if base)
    set_keypoint(key, pt) / keypoint(key) -> np.ndarray
    add_force(kind, at, label, direction="auto", magnitude=None) -> ForceSpec
    shift(delta) -> self            # moves mobject AND every keypoint
    fbd(include=None) -> VGroup     # delegates to fbd.render_forces
```

### `fbd.py`
```
render_forces(asset, include=None) -> VGroup:
    for spec in asset.forces (filtered by include):
        anchor = asset.keypoint(spec.at)
        dir    = resolve_direction(spec.direction)   # keyword or explicit unit
        end    = anchor + dir * arrow_length(spec.magnitude)
        Arrow(anchor->end, colour=FORCE_COLORS[kind], stroke_width=6) + MathTex(label)
```

### `bodies.py`
```
Block(PhysicsAsset)  (alias RectangularMass):
    mass=1, position=(0,0), width=0.9, height=None, shape="rectangle"|"square",
    color=None, fill_opacity=0.3, motion_state=AT_REST, velocity=(0,0),
    show_cm=True, show_weight=True, label="m", dynamics=DYNAMIC
    display_height = height or (width if square else 0.6*width)
    build(): Rectangle at CM; keypoints CM/top/bottom/left/right;
             YELLOW CM dot if show_cm; auto WEIGHT ForceSpec at CM if show_weight
    validates mass>0 and shape in {rectangle,square}
```

### `supports.py`
```
GROUND_Y = -2.0    # SKILL Rule 8
Support(PhysicsAsset): dynamics=STATIC
Floor(Support): y=GROUND_Y, half_width=5.5, hatch=True, color=GRAY
    build(): ground Line + hatch ticks; keypoints surface/left/right
    contact_under(x) -> [x, y, 0]
```

### `assembly.py`
```
Assembly:
    members: list; mobject: VGroup; keypoints: dict (namespaced "name.key")
    add(asset, place_on=None):
        if place_on: _place_on(asset, place_on)
        register mobject + namespaced keypoints
    _place_on(body, floor):     # Floor-only in M1
        shift body so keypoint("bottom").y == floor.y
        set body "contact" keypoint at floor.contact_under(CM.x)
    keypoint(key); fbd(include) = union of members' FBDs
```

## Tests shipped (`tests/test_assets_mechanics.py`, 8)
Block defaults/keypoints; RectangularMass alias; square shape; auto-weight;
shift moves mobject+keypoints; place-on-floor rests bottom + contact keypoint;
assembly namespacing; weight colour == COLOR_WEIGHT.

## Verified
ruff clean; 8/8 pass (full suite 19); rendered demo frame shows block resting on
floor with `mg` (down, purple) at CM and `N` (up, green) at contact.

## Carried forward (constraints later milestones must honour)
- keypoints are world-coord 3D np arrays; every new asset registers them.
- every field defaults; StrEnum only; colours only via palette.
- assets never import lesson `common.py` (framework-level; use palette).

## Revisions (architecture review 2026-09-05)

**M1's shipped public API is preserved** — the review makes no breaking change
here. The following are *forward-looking* deprecations implemented in later
milestones without breaking M1:

- **Internals refactor deferred to M1.5**: world-coord keypoints + mutate-on-
  `shift` are replaced internally by `Pose2D` + **local** keypoints (canonical
  geometry + absolute pose). `keypoint()` still returns world coords (review 3).
- **`ForceSpec` \u2192 `loads.py`** in M1.5: gains a physical `value:
  QuantityRef|float` separated from arrow length (`VectorScalePolicy`); the M1
  `magnitude=` field stays as a back-compat shim (reviews 20, 21).
- **`MotionState.CONSTRAINED`/`ABOUT_TO_MOVE` become deprecated aliases**
  (review 7) \u2014 they are not motion states; that info moves to relations. M1
  keeps `AT_REST`/`MOVING` as the live values.
- **`ContactRegime`/`ContactPersistence` are superseded** by M2's split
  (`ContactKinematics` + `FrictionModel` + `ContactLifecycle`) and the
  `ContactLocator` protocol (reviews 8, 9). M1 does not use them yet, so nothing
  breaks.
- **`ForceKind.WEIGHT` \u2192 alias of `InteractionKind.GRAVITY`** (review 22); the
  palette colour is unchanged.
- **Rationale:** keep the one shipped, tested slice stable while every
  foundational decision that affects M2\u2013M17 lands in M1.5/M2 before more code is
  written on top of it.
