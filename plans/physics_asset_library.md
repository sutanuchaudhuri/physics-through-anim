# Plan — Composable Physics Asset Library for `physics_through_anim`

Status: **SIGNED OFF — implementing** (2026-09-05)
Owner: (developer)
Target package: `src/physics_through_anim/physics/mechanics/`
Related reference: `physics-visualizer-engine/src/physicsviz` (declarative spec engine)

> **Namespace update (2026-09-05):** the framework root is now
> `physics_through_anim.physics` (not `...assets.physics`). Read every
> `assets/physics/...` path in this document as `physics/...`. The canonical,
> multi-domain layout is [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 0. Sign-off decisions (2026-09-05)

1. **Config mechanism**: stdlib `@dataclass` now (zero new deps). Design with a
   **future YAML config loader** in mind (keep fields plain/serializable), but
   do not build the loader yet.
2. **Spec/loader**: **not needed now** (deferred).
3. **`COLOR_TENSION`**: add a **new palette colour** for rope/string tension.
4. **Location**: assets live in **`assets/physics/mechanics/`**.
5. **2D first**, extend to 3D later (Rule 17 path).
6. **Naming**: use **`Block` / `RectangularMass`** (not `PointMass`) for the
   default rectangular body — `RectangularMass` is an alias of `Block`.
7. **Motion state**: include explicit **`CONSTRAINED`** and **`ABOUT_TO_MOVE`**
   (on the verge of slipping) in `MotionState`.
8. **Temporal phases**: add a **`Phase` (BEFORE / DURING / AFTER)** concept so an
   asset/assembly can render *before*, *during*, and *after* an event (e.g. a
   collision) — before-impact, impulse-transfer, post-impact.

---

## 1. Motivation

Today every scene hand-builds its shapes (`rough_ground()`, `thin_block()`,
`wheel_setup()`, ad-hoc `Arrow`s). That is fine for one lesson but it does not
scale, and it forces each scene author to re-decide the same things: where the
CM is, which way `mg` points, whether the body is static or moving, where the
contact point is and whether it moves, what the free-body diagram looks like.

We want a **hierarchical, composable library of physics "assets"** so a
developer can *assemble* a scene from semantically-rich, granular building
blocks and then, for free, get:

- named **keypoints** (CM, contact point `P`, rope attach points `A`/`B`, hinge `H`),
- a **free-body diagram (FBD)** decomposition (force vectors drawn at the right
  keypoints, in the right colors),
- correct **animation** for the moving parts (a conveyor belt, a rolling
  cylinder, a rotating pulley) — or a deliberately **frozen frame**,
- consistent styling that already obeys the `physics-animation-standards` skill
  (Rule 2 colors, Rule 8 layout bands, Rule 5 tangential vectors, Rule 7 real
  rolling, Rule 9 symbols-only labels).

This mirrors the *intent* of `physicsviz` (declarative entities → contact
regimes → FBD) but stays **manim-native and dependency-light** (no pydantic,
no SVG engine) because `physics_through_anim`'s only job is to render teaching
animations.

## 2. Goals / Non-goals

**Goals**
- A base class hierarchy separating **geometry**, **dynamic state**,
  **contact**, **support/environment**, and **forces/FBD** into orthogonal,
  granular pieces.
- Distinguish, *through the class/config structure*:
  - **static vs dynamic** bodies, and for dynamic bodies whether they are
    **moving now or at rest now** (e.g. a body on a stopped conveyor vs a
    moving one);
  - whether a **contact point is fixed or moves with time** (conveyor contact
    stays put; a cylinder's contact `P` on an incline is a *moving* point).
- **Separable sub-assets**: hinge is separate from the wall it hangs on;
  incline is separate from the floor it sits on; a pulley, its ceiling mount,
  and each rope segment are separate, individually-addressable assets that can
  be shown/animated/faded independently.
- **Assembly**: combine multiple assets into one scene with automatic relative
  placement (body-on-floor, cylinder-on-incline-on-floor, pulley-from-ceiling)
  and a single combined FBD.
- **Named attachment points** supplied by the developer at construction (e.g.
  "the thread attaches to the pulley at `A` and to the hanging mass at `B`",
  "the hinge attaches to the ceiling at `H`"). Forces are drawn *at* these
  named points.
- **Granular properties with defaults** — the developer supplies only what
  matters; everything else defaults sensibly.
- FBD **decomposition** + the ability to **freeze a frame** and show the force
  vectors at key points.

**Non-goals (for this effort)**
- No physics *solver* (no ODE integration inside the assets). Assets are
  visual + semantic; if a scene needs real dynamics it still uses
  `simulation.py`-style modules or `manim-physics` (Rule 10). Assets can
  *consume* a trajectory but don't compute one.
- No pydantic/spec-file loader like `physicsviz` (can be a later phase — see
  Open Questions).
- No change to `render.py` / `lessons.toml` / the CLI. Assets are a library
  scenes import; lessons still register normally.

## 3. Design principles

1. **An asset is a builder, not a Mobject subclass.** Each asset owns a manim
   `VGroup` (`asset.mobject`) plus semantic metadata and a
   `keypoints: dict[str, np.ndarray]` map in *world* coordinates. This mirrors
   the existing repo convention where `wheel_setup()` returns a `VGroup` with a
   `.wheel_center` attribute — we generalize that to every asset.
2. **Config is a stdlib `@dataclass`** (frozen where possible) with defaults and
   `__post_init__` validation. No new dependency. (Pydantic is available in the
   *reference* repo but not here; see Open Questions if we want it.)
3. **Orthogonal concerns via composition/mixins**, not a deep single tree:
   - *Geometry* (shape + size) — how it's drawn.
   - *Dynamics* (`BodyDynamics.STATIC | DYNAMIC`) and *motion state*
     (`MotionState.AT_REST | MOVING`) — separate axis.
   - *Contact* (`ContactRegime` + `ContactPersistence.FIXED | MOVING`).
   - *Forces* (a list of `ForceSpec` attached at named keypoints) → FBD.
4. **Everything obeys the skill.** The FBD/vector layer calls the existing
   `force_arrow` / `velocity_arrow` helpers and the `COLOR_*` constants; assets
   place themselves within the Rule 8 layout bands; rolling uses the Rule 7
   `animate_rolling` pattern; captions stay symbol-only (Rule 9).

## 4. Enumerations (proposed `assets/physics/kinds.py`)

```python
class BodyDynamics(str, Enum):
    STATIC = "static"      # never moves (walls, ceiling, fixed incline)
    DYNAMIC = "dynamic"    # can move (a block, a cylinder, a hanging mass)

class MotionState(str, Enum):
    AT_REST = "at_rest"          # dynamic but currently v = 0 (block on stopped belt)
    MOVING = "moving"            # currently translating/rotating (belt running)
    CONSTRAINED = "constrained"  # held by a constraint (pinned/roped), not free to move
    ABOUT_TO_MOVE = "about_to_move"  # on the verge of slipping (f_s = mu_s N)

class ContactRegime(str, Enum):        # mirrors physicsviz.core.enums
    NO_CONTACT = "no_contact"
    RESTING = "resting"
    SLIDING = "sliding"
    ROLLING_NO_SLIP = "rolling_no_slip"
    SMOOTH = "smooth_contact"

class ContactPersistence(str, Enum):
    FIXED = "fixed"        # the material contact point does not change (conveyor patch)
    MOVING = "moving"      # contact point P sweeps along the surface (cylinder on incline)

class Phase(str, Enum):    # temporal phase for event scenes (e.g. a collision)
    BEFORE = "before"      # pre-event state (pre-impact)
    DURING = "during"      # the event itself (impulse transfer / contact)
    AFTER = "after"        # post-event state (post-impact)

class ForceKind(str, Enum):            # drives color via Rule 2
    WEIGHT = "weight"        # mg   -> COLOR_WEIGHT
    NORMAL = "normal"        # N    -> COLOR_NORMAL
    FRICTION = "friction"    # f    -> COLOR_FRICTION
    APPLIED = "applied"      # F    -> COLOR_APPLIED
    TENSION = "tension"      # T    -> COLOR_TENSION (new palette colour)
    REACTION = "reaction"    # hinge/pin reaction
```

## 5. Class hierarchy (proposed)

```
PhysicsAsset (ABC)                         assets/physics/base.py
├─ .mobject: VGroup                        # the drawable
├─ .keypoints: dict[str, np.ndarray]       # named world points (CM, P, A, B, H, axle...)
├─ .dynamics: BodyDynamics
├─ .forces: list[ForceSpec]                # declared force vectors (for FBD)
├─ build() -> VGroup                        # subclass builds geometry + fills keypoints
├─ add_force(at: str, kind, magnitude|auto, label, direction) 
├─ fbd(scene=None, include=None) -> VGroup  # force_arrow at each keypoint (Rule 2 colors)
├─ shift_to(anchor)/place_on(support, at)   # placement helpers -> updates keypoints
└─ animate(scene, ...)                      # default no-op (static); overridden by movers

Body(PhysicsAsset)                         assets/physics/bodies.py
├─ mass, motion_state, velocity, show_cm, show_weight
├─ keypoint "CM"; auto weight force at CM when show_weight
├─ PointMass(Body)        # DEFAULT rectangular per requirement; CM + mg
├─ Block(Body)            # rectangle|square, angle
├─ CircularBody(Body)     # radius, inertia_factor; keypoint "contact" when placed
│    └─ Cylinder(CircularBody)  # cross-section hatch + weight at CM; rolls
└─ Rod(Body)              # endpoints "A","B"; massless flag (no weight if massless)

Support(PhysicsAsset)                      assets/physics/supports.py   (STATIC by default)
├─ Floor          # horizontal ground, y level, hatch
├─ Wall           # vertical wall (a Floor rotated 90°), hatch side
├─ Ceiling        # top boundary, hatch downward
├─ Incline        # angle_deg (default 30), sits ON a Floor (composable), length, mu
├─ Conveyor(Floor)   # belt_speed (default 0 => AT_REST), direction; belt anim
└─ Pulley(CircularBody as support)   # axle keypoint, hangs from a Ceiling/Hinge; rotates flag

Connector(PhysicsAsset)                    assets/physics/connectors.py
├─ Rope           # from_point -> to_point, angle_deg, tension label, slips flag
├─ Hinge          # pin marker (keypoint "H"); SEPARATE from the wall/ceiling it pins to
└─ PinJoint       # semantic "A is pinned to B at point" (reaction force pair)

Contact                                    assets/physics/contact.py
├─ regime: ContactRegime, persistence: ContactPersistence
├─ point ("auto"|keypoint), tangent, normal, mu
└─ marker() -> Dot at P; frame() -> tangent/normal indicator

Assembly                                   assets/physics/assembly.py
├─ add(asset, place_on=None, at=None)
├─ .mobject: VGroup (all sub-asset mobjects)
├─ .keypoints: merged, namespaced ("pulley.A", "rope1.top")
├─ fbd() -> combined FBD across members
└─ animate(scene) -> plays each mover's animation (belt + rolling + rotation) in sync
```

### 5.1 `ForceSpec` (the FBD atom)

```python
@dataclass(frozen=True)
class ForceSpec:
    kind: ForceKind
    at: str                 # keypoint name on the owning asset ("CM","P","A"...)
    label: str              # symbolic only, e.g. "mg", "N", "f_s", "T_A"  (Rule 9)
    direction: tuple | str  # explicit unit dir, or "down"/"along_normal"/"up_slope"/"auto"
    magnitude: float | None = None   # for relative arrow lengths; None => default length
```

`fbd()` turns each `ForceSpec` into a `force_arrow(...)` anchored at
`keypoints[at]`, colored by `kind` per Rule 2. This is exactly the
"decompose each body into an FBD and show the force vector at key points"
requirement, and because forces are declared with a named `at`, a pulley can
say *"tension `T_A` acts at keypoint `A`, tension `T_B` at keypoint `B`"* and
the arrows land in the right places automatically.

## 6. Granular properties + defaults (illustrative)

Every asset takes a small dataclass config; unset fields default. Examples:

```python
PointMass(mass=1.0, size=(0.9, 0.6), motion_state=AT_REST,
          show_cm=True, show_weight=True, color=None, label="m")
Incline(angle_deg=30, length=5.0, mu=0.0, on_floor=True, thickness=0.0)
Conveyor(y=GROUND_Y, length=8.0, belt_speed=0.0,   # 0 => AT_REST, >0 => MOVING
         direction=+1, mu=0.4)
Cylinder(mass=1.0, radius=0.6, inertia_factor=0.5, show_cross_section=True)
Pulley(radius=0.5, rotates=True, hangs_from="ceiling",
       ropes={"A": 30, "B": 60}, thread_slips=False)   # rope angles default 30/60
Rope(from_point="pulley.A", to_point="mass1.top", angle_deg=30,
     tension_label="T_1", slips=False)
Hinge(at=(x, y), pins="rod.A", to="wall")              # hinge separate from wall
```

Defaults chosen so the three "same body, different environment" cases the
requirement calls out differ **only** in the fields that matter:

| Scene | Assets | Distinguishing fields |
| --- | --- | --- |
| Point mass on a floor, `mg` at CM | `PointMass` + `Floor` | body `motion_state=AT_REST`, contact `FIXED` |
| Point mass on a **moving** conveyor | `PointMass` + `Conveyor(belt_speed>0)` | `Conveyor.motion_state=MOVING`, belt animates |
| Point mass on a **stopped** conveyor | `PointMass` + `Conveyor(belt_speed=0)` | `Conveyor.motion_state=AT_REST`, belt frozen |

## 7. The requested catalog → hierarchy mapping

- **Point mass (default rectangular) with CM keypoint + `mg` down, on a floor** →
  `Assembly[Floor, PointMass(show_cm, show_weight)]`; `PointMass` auto-declares
  a `WEIGHT` force at `CM`.
- **Point mass on a conveyor moving at `v` (animated)** →
  `Assembly[Conveyor(belt_speed=v), PointMass]`; `Conveyor.animate()` scrolls
  the belt hatching; contact `FIXED` (patch stays under the body) but belt
  surface `MOVING`.
- **Body on a conveyor currently not moving** → same, `belt_speed=0`,
  `MotionState.AT_REST`; `animate()` is a no-op (frozen).
- **Hinge hanging from a wall, hinge + wall separate** →
  `Assembly[Wall, Hinge(pins=..., to="wall")]`; each is its own asset, can be
  faded in/out independently.
- **Hinge on a vertical wall, separable** → `Wall(angle=90)` + `Hinge`.
- **Cylinder rolling down an incline** → `Assembly[Floor, Incline(angle=30,
  on_floor=True), Cylinder(show_cross_section, weight_at_CM)]`; contact `P` is
  `ContactPersistence.MOVING`; rolling via the Rule 7 `animate_rolling` pattern;
  contact dot at the (moving) keypoint `P`.
- **Pulley hung from ceiling, ropes at 30° and 60°, rotates or not, thread slips
  or not, all shown separately** → `Assembly[Ceiling, Pulley(rotates=...,
  ropes={"A":30,"B":60}), Rope(from="pulley.A",...), Rope(from="pulley.B",...)]`;
  tensions `T_A`,`T_B` declared at pulley keypoints `A`,`B`; `Pulley.animate()`
  rotates it (or not); `Rope(slips=True)` shows slip markers.

## 8. FBD, freeze-frame, and animation integration

- **FBD**: `asset.fbd()` / `assembly.fbd()` returns a `VGroup` of colored
  `force_arrow`s at the declared keypoints. A scene shows it with
  `self.play(FadeIn(assembly.fbd()))` and can hold on it (freeze frame).
- **Freeze a frame**: assets are static by default; a scene simply *doesn't*
  call `animate()` and holds — the FBD stays put. For manim-physics-driven
  freezes see Rule 10.7.
- **Show vectors at key points**: guaranteed by the `ForceSpec.at` keypoint
  anchoring; e.g. normal + friction at `P`, weight at `CM`, tension at `A`/`B`.
- **Animation**: `Conveyor.animate()` (belt scroll), `Cylinder.animate_roll()`
  (Rule 7), `Pulley.animate_spin()`; `Assembly.animate()` runs the movers
  together on one `ValueTracker` so they stay in sync, and any scene using this
  ends with `self.finish_with_narration()` per Rule 18.
- Kinematic vectors (velocity of the contact patch, `ω×r`) reuse the exact
  Rule 5 `(r_y, -r_x)` tangential construction.

## 9. Proposed file layout

```
src/physics_through_anim/assets/
├─ visuals.py                 # EXISTING (generic helpers) — unchanged
├─ narration.py               # EXISTING — unchanged
└─ physics/                   # NEW namespace package
   └─ mechanics/              # NEW package (2D mechanics assets)
      ├─ __init__.py          # curated exports (Block/RectangularMass, Incline, Conveyor, Pulley, Rope, Hinge, Assembly, ...)
      ├─ kinds.py             # enums (Section 4): BodyDynamics, MotionState, ContactRegime, ContactPersistence, Phase, ForceKind
      ├─ palette.py           # canonical force/kinematic colours incl. COLOR_TENSION
      ├─ base.py              # PhysicsAsset, ForceSpec, keypoint/placement machinery
      ├─ bodies.py            # Block/RectangularMass, CircularBody, Cylinder, Rod
      ├─ supports.py          # Floor, Wall, Ceiling, Incline, Conveyor, Pulley
      ├─ connectors.py        # Rope, Hinge, PinJoint
      ├─ contact.py           # Contact (regime + persistence), markers/frames
      ├─ fbd.py               # ForceSpec -> arrow rendering, combined FBD, Rule 2 colours
      ├─ phases.py            # BEFORE/DURING/AFTER helpers for event (collision) scenes
      └─ assembly.py          # Assembly (compose + place + combined FBD + synced animate)
tests/
├─ test_assets_geometry.py    # keypoints resolve correctly; placement math
├─ test_assets_fbd.py         # forces land at the right keypoints, correct colours/kinds
└─ test_assets_catalog.py     # each requested example builds without error
```

## 10. Reuse of existing framework standards

- **Colors (Rule 2)**: `fbd.py` maps `ForceKind → COLOR_*`. `TENSION` needs a
  color — proposal: add `COLOR_TENSION` (a blue/cyan distinct from velocity's
  blue) to the lessons' `common.py` and the skill table (Open Question).
- **`force_arrow`/`velocity_arrow`**: assets call these, not raw `Arrow`.
- **Layout bands (Rule 8)**: `Floor` defaults to `GROUND_Y`; assets expose a
  `place_within_bands()` helper.
- **Rolling (Rule 7)**: `Cylinder.animate_roll` wraps `animate_rolling`.
- **Symbols-only labels (Rule 9)**, **logging (Rule 14)**, **sub-scenes
  (Rule 16)**, **narration sync (Rule 18)**, **3D (Rule 17)** all continue to
  apply; assets are 2D first, with a noted 3D extension path.

## 11. SKILL.md update (Rule 19, to be written when code lands)

Add a new rule so scaffolding reuses the library **when the user asks**:

> **Rule 19 — Build scenes from the physics asset library when asked.** When a
> user asks (during scaffolding per Rule 11, or a scene edit) to *reuse the
> asset library / build from assets*, construct the scene from
> `physics_through_anim.assets.physics` (PointMass, Block, Cylinder, Incline,
> Conveyor, Pulley, Rope, Hinge, Assembly) instead of ad-hoc shapes. Supply the
> granular properties the problem states (mass, angle, belt speed, rope angles,
> which contact is fixed vs moving, named attachment points) and rely on
> defaults for the rest. Get the FBD from `assembly.fbd()` rather than placing
> arrows by hand — it already obeys Rules 2/5/8/9. Do **not** force this on
> lessons that didn't ask for it.

Also update Rule 11's scaffold checklist ("if the plan is asset-based, base
scenes on the asset library") and the frontmatter `description`.

## 12. Phased milestones (each independently reviewable/renderable)

> **Expanded roadmap (2026-09-05).** This 5-milestone plan has been extended
> into a full **7-layer 2-D mechanics framework** (M1–M16). Each milestone now
> has its own pseudocode-heavy tech doc under [`asset_library/`](asset_library/)
> — start at [`asset_library/README.md`](asset_library/README.md) for the layer
> model, roadmap table, and the four architecture probes. M1 below is shipped;
> M2–M5 are unchanged in intent and documented in full there; M6–M16 add state/
> trajectory, events/constraints, curved surfaces, overlays/graphs, springs,
> chains, collisions, orbital, non-inertial frames, recipes, and 3-D.

- **M1 — Core + one vertical slice**: `kinds.py`, `base.py`, `fbd.py`,
  `PointMass`, `Floor`, `Assembly`; a demo scene "point mass on floor with mg";
  tests. → proves the keypoint + FBD model end-to-end.
- **M2 — Supports & contact**: `Wall`, `Ceiling`, `Incline`, `Conveyor`
  (moving/stopped), `Contact` (fixed vs moving). Demo: the three conveyor cases.
- **M3 — Rolling & rotation**: `CircularBody`, `Cylinder` rolling down incline
  (moving `P`), `Pulley` spin. Demo: cylinder-on-incline FBD + roll.
- **M4 — Connectors & assemblies**: `Rope`, `Hinge`, `PinJoint`; pulley +
  ceiling + two ropes (30°/60°) with tensions at `A`/`B`; slip vs no-slip.
- **M5 — Skill + docs**: write Rule 19, update Rule 11 + frontmatter; a short
  gallery scene rendering every catalog asset for visual QA.
- **M6–M16** — see [`asset_library/`](asset_library/): state/trajectory (M6),
  constraints/events (M7), curved surfaces/edges (M8), overlays/graph binding
  (M9), springs/dampers (M10), chains (M11), collisions (M12), orbital (M13),
  reference frames (M14), recipes + regression gallery (M15), 3-D (M16).

## 13. Testing strategy

- **Unit (no render)**: keypoint coordinates after placement; `fbd()` produces
  the expected number of arrows with correct `ForceKind`/color/anchor; defaults
  resolve as specified. (Same style as `tests/test_subscenes.py` with a fake
  scene where needed.)
- **Render smoke**: one throwaway scene per milestone rendered at low quality,
  a frame extracted and eyeballed (per the skill's verify-by-frame practice),
  then cleaned up.

## 14. Open questions for review — RESOLVED (see Section 0 sign-off)

All resolved on 2026-09-05:
1. Config → **dataclass now**, YAML loader later.
2. Spec/loader → **deferred**.
3. `COLOR_TENSION` → **add new palette colour**.
4. Location → **`assets/physics/mechanics/`**.
5. 2D first, 3D later → **yes**.
6. Naming → **`Block` / `RectangularMass`** (alias).
7. Motion state → **add `CONSTRAINED` and `ABOUT_TO_MOVE`**.
8. Extra requirement captured: **`Phase` BEFORE/DURING/AFTER** for event
   (collision) scenes.

---

*Implementation started at Milestone 1 (core + Block-on-floor slice) on the
sign-off date.*
