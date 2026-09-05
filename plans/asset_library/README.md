# Physics Asset Library — Full Framework Roadmap (Index)

Status: **DRAFT FOR REVIEW** (2026-09-05)
Scope: turn the current Manim asset catalogue into a genuinely reusable
**2-D mechanics animation framework** — declarative entities → contact regimes
→ events → trajectories → overlays — while keeping the visual asset layer
**solver-free** (assets *consume* motion, they never integrate it).

Parent plan (signed off, M1 shipped): [`../physics_asset_library.md`](../physics_asset_library.md)

> This folder holds one **tech doc per milestone** (M01–M16). Each is heavy on
> pseudocode so the API can be reviewed *before* implementation. Nothing here is
> "kept for future" — every capability in the expanded vision has a milestone.

---

## Architectural layers (revised — architecture review 2026-09-05)

The original "7 layers" mixed physics semantics, geometry, state, rendering and
playback in a few classes. The review (point 1) replaces it with these strict
ownership boundaries — each layer **owns** one thing and must **not** own the
next column:

| Layer | Owns | Must NOT own | Milestone(s) |
| --- | --- | --- | --- |
| **Entity geometry** | `Block`, `Rod`, `Disk`, `Pulley`, `Rope` geometry, `Table` | solving, events | M1, M3 |
| **Mechanical model** | mass, inertia, CM, body surfaces, attachment points | Manim animation timing | M1.5 |
| **Kinematics & transforms** | `Pose2D`/SE(2) `Transform2D`, `Frame2D`, point kinematics, bindings (pose/attachment/path/rolling/look-at), scene graph | dynamics / solving | M1.6 |
| **Relations** | `Contact`, `PinConstraint`, `RopeConstraint`, `RollingConstraint` (pure semantic) | `VGroup` / rendering | M2, M4, M7 |
| **Motion data** | `BodyState2D`, `SystemState`, `Trajectory`, signals | ODE integration | M6 |
| **Timeline** | events, constraint activation/deactivation, named moments | rendering | M7 |
| **Rendering binding** | model/state → Manim mobjects | physics decisions | M1.5, M9 |
| **Teaching overlays** | FBD, vectors, graphs, energy, contact microscope | model mutation | M9, M13, M14 |
| **Lesson composition / presentation** | `ScenePhysicsData`/`NamedState`/`ViewSpec`/`LessonSpec`: supplied physics values → named states, transitions, views, narration beats | solving the physics | M18 |
| **Recipes** | textbook composition of generic primitives | source-book metadata | M15 |
| **Problem orchestration** | Krotov/F=ma/Holics `ProblemRef` → recipe/scene plan | low-level Manim | M17 |

**Two load-bearing rules from the review:**

- **`PhysicsAsset` means *renderable entity* only** (review point 2). It owns
  `mobject`/`keypoints`/`forces`. A **`Contact`, `Constraint`, or `Event` is a
  relationship, not a drawable** — they are plain semantic dataclasses with **no
  `mobject`**; their optional visuals live in `overlays/`/`glyphs`
  (`ContactMarkerOverlay`, `ConstraintGlyph`, `EventHighlightOverlay`). This
  reverses M2's original `class Contact(PhysicsAsset)`.
- **Problem IDs never live in `mechanics/`** (points 30–31). The corpus knows
  *which* problem/source/concept; `mechanics/` knows *how to represent*
  mechanics. `KrotovProblem47`/`FMA2025Q18` belong in `problems/`, which passes
  only a resolved `ProblemRef` + structured metadata into the framework.

**Design rule (unchanged):** `KeplerOrbit`, `FallingChain`,
`CylinderLeavingTable`, `GalperinCollision` are **recipes assembled from generic
assets** (M15), never fundamental asset classes. Composition-first, always.

---

## The nine questions the framework must answer cleanly

```
WHAT objects exist?                      -> Bodies (L1)
WHERE are their meaningful points?       -> keypoints dict (world coords)
WHAT connects / constrains them?         -> Connectors (L3) + Constraints (L4)
WHAT contacts what?                      -> Contact (L4)
WHAT is the current contact regime?      -> ContactRegime / ContactState (L4)
WHAT event changes that regime?          -> Event / EventSequence (L5)
WHAT state should each object have now?  -> State / Trajectory adapter (M6)
WHAT physical quantities to visualize?   -> Overlays (L6)
WHAT explanatory view should show?       -> Snapshot / Recipe (M6, M15)
```

Manim becomes an implementation detail: a human writes a recipe, an AI builds
the same semantic graph, both produce the same
`Assembly + State/Trajectory + Events + Overlays`.

---

## Milestone roadmap

Revised sequence (review point 33): a new **M1.5** hardens the model layer
(`Pose2D` + local keypoints, `RigidBody2D`, typed refs, `loads.py`) *before*
M2–M4 build on it, and a new **M17** adds the problem/corpus layer. This avoids
shipping APIs in M2/M3 and then replacing their foundations in M6/M8.

| M | Title | Doc | Status |
| --- | --- | --- | --- |
| M1 | Core + block-on-floor slice | [`M01_core_block_floor.md`](M01_core_block_floor.md) | ✅ shipped (API preserved) |
| **M1.5** | **Pose2D + local keypoints, RigidBody2D, typed refs, loads** | [`M01_5_pose_rigidbody.md`](M01_5_pose_rigidbody.md) | draft (NEW) |
| **M1.6** | **Kinematics layer: transforms, frames, bindings, point kinematics (MUST)** | [`M01_6_kinematics_bindings.md`](M01_6_kinematics_bindings.md) | draft (NEW) |
| M2 | Surface protocol + Contact semantic model + supports/conveyor | [`M02_supports_contact_conveyor.md`](M02_supports_contact_conveyor.md) | draft (revised) |
| M3 | Rolling / rotation / pulley bodies | [`M03_rolling_rotation.md`](M03_rolling_rotation.md) | draft |
| M4 | Connectors & assemblies (rope/hinge/pin) | [`M04_connectors_assemblies.md`](M04_connectors_assemblies.md) | draft |
| M5 | SKILL Rule 19 + docs + first gallery | [`M05_skill_gallery.md`](M05_skill_gallery.md) | draft |
| M6 | State snapshot + trajectory adapter | [`M06_state_trajectory.md`](M06_state_trajectory.md) | draft |
| M7 | Constraints + event model + contact switching | [`M07_constraints_events.md`](M07_constraints_events.md) | draft |
| M8 | Curved surfaces / table / edge / track / peg / slot | [`M08_curved_surfaces.md`](M08_curved_surfaces.md) | draft |
| M9 | Explanatory overlays + graph binding | [`M09_overlays_graphbinding.md`](M09_overlays_graphbinding.md) | draft |
| M10 | Springs / dampers / richer connectors | [`M10_springs_dampers.md`](M10_springs_dampers.md) | draft |
| M11 | Chains / distributed-mass bodies | [`M11_chains.md`](M11_chains.md) | draft |
| M12 | Collisions / impulse / event sequences | [`M12_collisions.md`](M12_collisions.md) | draft |
| M13 | Orbital / central-force assets | [`M13_orbital.md`](M13_orbital.md) | draft |
| M14 | Reference frames / non-inertial overlays | [`M14_reference_frames.md`](M14_reference_frames.md) | draft |
| M15 | Recipe catalogue + regression gallery | [`M15_recipes_gallery.md`](M15_recipes_gallery.md) | draft (revised) |
| M16 | 3-D rigid-body / top / gyroscope | [`M16_three_d.md`](M16_three_d.md) | draft (revised) |
| **M17** | **Problem/corpus orchestration layer** | [`M17_problem_orchestration.md`](M17_problem_orchestration.md) | draft (NEW) |
| **M18** | **Presentation contract + declarative lesson authoring (MUST)** | [`M18_presentation_authoring.md`](M18_presentation_authoring.md) | draft (NEW) |

---

## Cross-cutting design principles (apply to every milestone)

1. **Assets are builders, not `Mobject` subclasses.** Each owns
   `asset.mobject: VGroup` + `asset.keypoints: dict[str, np.ndarray]` (world
   coords) + `asset.forces: list[ForceSpec]`. Established in M1.
2. **stdlib `@dataclass`, no pydantic.** Every field has a default (YAML loader
   is a later, non-blocking concern — keep fields plain/serializable).
3. **`StrEnum`** for every enum (ruff UP042). No `str, Enum`.
4. **Solver-free.** Assets consume `State`/`Trajectory` (M6); they never
   integrate ODEs. Real dynamics stay in `manim-physics` (SKILL Rule 10) or a
   scene-supplied trajectory.
5. **Obey the SKILL.** FBD/overlay colours via `palette.py` (Rule 2), layout
   bands (Rule 8), tangential `(r_y, -r_x)` vectors (Rule 5), real rolling
   (Rule 7), symbols-only labels (Rule 9), logging (Rule 14), sub-scenes
   (Rule 16), narration sync (Rule 18), 3-D base (Rule 17).
6. **`shift()` moves mobject *and* keypoints together.** Any new geometry must
   register its keypoints so placement, FBD anchoring, and overlays stay exact.
7. **Semantic queries** on `Assembly` (`body("disk")`, `contact("disk.floor")`,
   `resolve("pulley.A")`) — added in M6/M7, foundation already in M1
   namespacing.
8. **Local geometry + absolute pose, never cumulative transforms** (review 3).
   Entities store `local_keypoints` + a `Pose2D`; `keypoint()` still returns
   world coords but computes them as `pose.world_point(local)`. No updater ever
   mutates points incrementally — every frame applies an *absolute* pose, so
   translation + rotation + rolling + trajectories + parent assemblies compose
   without drift.
9. **Typed references, never string-keyed dicts for physics** (reviews 13, 19).
   `AssetRef`, `PointRef`, `QuantityRef`, typed `Constraint`/`Load` dataclasses —
   so an AI can inspect a constructor contract instead of guessing dict keys.
10. **Assets evaluate laws; they never integrate.** Local constitutive laws
    (`F=-kx`, `N` from a contact model, Kepler *geometry*) are allowed; advancing
    state by integrating equations of motion is not — that enters only through a
    `Trajectory` provider (see the solver-free contract below).
11. **`Assembly` is a facade, not a god object** (review 28). Internally it
    delegates to `MechanicsModel` (entities/contacts/constraints),
    `MechanicsRenderer` (state→mobjects), and `Timeline` (trajectory/events/
    moments); the public `add/connect/play_*` surface stays pleasant.

---

## The four architecture probes (acceptance gate)

If the design represents these four elegantly, it is on the right track. Each is
a **recipe** (M15) that must reuse only generic assets:

- **A. Cylinder reaches a table edge** — `Disk + Table + Edge` + moving contact
  + contact-switch + separation + free-flight rotation. Exercises M3, M7, M8.
- **B. Kepler elliptical orbit** — `Particle + CentralBody + Trajectory` +
  target-directed force + radius vector + swept area + apsis markers + graph.
  Exercises M6, M9, M13.
- **C. Chain falling over an edge** — distributed body + moving material
  coordinates + table + edge + changing supported/free portions + COM.
  Exercises M8, M11.
- **D. Infinite block collisions (Galperin)** — multiple bodies + wall +
  BEFORE/DURING/AFTER + repeated events + snapshots + event counter +
  phase-space overlay. Exercises M6, M12.

---

## Directory layout when complete (revised)

> Namespace: paths below drop the `assets/` prefix — read `assets/physics/...`
> as `physics/...`. Canonical layout: [../ARCHITECTURE.md](../ARCHITECTURE.md).

```
src/physics_through_anim/physics/mechanics/
   kinds.py            # StrEnums (trimmed: MotionState AT_REST|MOVING; split contact enums)
   refs.py             # AssetRef, PointRef, QuantityRef, SurfaceRef (M1.5)
   pose.py             # Pose2D: local->world (M1.5)
   palette.py          # colours (force + kinematic + orbit + momentum + pseudo families)
   base.py             # PhysicsAsset (renderable entity ONLY), keypoint machinery
   loads.py            # LoadSpec: ForceSpec / TorqueSpec / ImpulseSpec (M1.5, review 20-21)
   massprops.py        # MassProperties, inertia_about (M1.5)
   bodies.py           # RigidBody2D + Block/Rod/Disk/Ring/Cylinder/Spool/Pulley/Particle (M1.5,M3)
   supports.py         # Floor, Wall, Ceiling, Incline, Conveyor (thin owners of a Surface)
   surfaces.py         # Surface protocol + LineSurface/FloorSurface/InclineSurface (M2; extended M8)
   connectors.py       # Rope, MasslessLink, Cable (flexible physical links) (M4)
   constraints.py      # typed Pin/FixedPoint/Distance/RopeLength/Rolling/Path/Slot (M4,M7)
   contact.py          # Contact (pure semantic) + ContactLocator impls (M2, enriched M7)
   events.py           # Event, EventKind (core), EventSequence, Phase (M7)
   state.py            # BodyState2D, SystemState, Trajectory[SystemState], InterpolationPolicy (M6)
   signals.py          # Signal + QuantitySignal/TimeSignal (M6/M9)
   springs.py          # SpringGeometry + HookeLaw + SpringConstraint; Damper; TorsionSpring (M10)
   chain.py            # Chain geometry + ChainShapeState (shape carried in SystemState) (M11)
   fbd.py              # LoadSpec -> arrows, VectorScalePolicy (M1, review 20)
   glyphs.py           # HingeMarker, PinMarker (relation visuals, not overlays) (M4)
   overlays/           # explanatory assets, render-independent OverlaySpec (M9,M12,M13,M14)
      forces.py kinematics.py rotation.py energy.py momentum.py
      orbit.py contact.py constraints.py events.py graphs.py frames.py
   frames.py           # ReferenceFrame (consumes FrameState/FrameTrajectory) (M14)
   orbital.py          # CentralBody, OrbitPath, apsis (GEOMETRY only) (M13)
   model.py            # MechanicsModel (entities/contacts/constraints)  \
   render.py           # MechanicsRenderer (state -> mobjects)           |  facade split
   timeline.py         # Timeline (trajectory/events/moments)           /   (review 28)
   assembly.py         # Assembly: pleasant facade over the three above
   recipes/            # textbook compositions returning Recipe(specs, not VGroups) (M15)
      atwood.py rolling_spool.py table_edge.py kepler.py chain.py collisions.py ...
src/physics_through_anim/motion/analytic/     # analytic Trajectory providers (review 15)
   projectile.py rolling.py kepler.py shm.py top.py
src/physics_through_anim/problems/            # corpus/problem orchestration (M17, reviews 30-31)
   refs.py registry.py scene_plan.py adapters.py
```

## Cross-domain evolution (springs & fluids review 2026-09-05)

Springs stay inside mechanics but split across milestones (physical spring →
M10, SHM kinematics → M6, FBD/graphs → M9, events → M7, *massive* spring → M11
`DistributedBody`). Fluid mechanics is large enough to be a **sibling domain**,
not part of `mechanics/`. Both reuse a domain-neutral core:

```
src/physics_through_anim/physics/
├─ core/                     # domain-neutral, shared by mechanics AND fluids
│   refs.py pose.py transforms.py frames.py state.py trajectory.py timeline.py signals.py events.py loads.py
│   # transforms.py = SE(2) Transform2D (point vs vector); pose.py = Pose2D; frames.py = Frame2D
│   # SystemState carries entities (RigidKinematicState) + FIELDS + observables
├─ kinematics/               # reusable transform/kinematics/binding layer (M1.6, MUST)
│   rigid_body.py point.py relative_motion.py instantaneous_center.py rolling.py linkage.py bindings.py
├─ mechanics/                # rigid bodies, surfaces, constraints, springs, ...
├─ fluids/                   # regions, containers, pipes, boundaries, orifices, ...
└─ overlays/
    common/                   # FBD, vectors, graphs, energy (domain-neutral)
    mechanics/                # rolling field, contact microscope, ...
    fluids/                   # pressure, level, flow, streamlines, ...
```

The fluid domain has its **own plan series** (mirroring this one) at
[`../fluids/`](../fluids/) — `F01`–`F06`. It reuses the same `Trajectory`,
`Timeline`, signals, named moments, `GraphBinding`, and narration sync, so SHM,
a Krotov pulley problem, a dam-pressure lesson, and a draining reservoir all
share one rendering + teaching pipeline.

## Solver-free contract (authoritative — mirrored in M06)

> A mechanics asset or relation may evaluate **geometry, kinematics,
> constitutive laws, and declared constraint relationships**, but it must never
> advance physical state by **integrating equations of motion**. Motion enters
> the rendering framework through a `Trajectory` provider whose only required
> operation is sampling a complete `SystemState` at time `t`.

```python
class Trajectory(Protocol):
    @property
    def domain(self) -> TimeDomain: ...
    def state_at(self, t: float) -> SystemState: ...
```

Providers: `AnalyticTrajectory`, `SampledTrajectory`, `PiecewiseTrajectory`,
`CSVTrajectory`, `SciPySolutionAdapter`, `ManimPhysicsAdapter`,
`PrecomputedTrajectory`. Assets do not care where the solution came from — so an
F=ma problem, a Krotov linkage, a Holics rolling problem, and an externally
integrated system all reuse the same rendering + teaching infrastructure.

---

## Revisions ledger (architecture review 2026-09-05)

This roadmap was revised against a 33-point architecture review. Per-milestone
"Revisions" sections record the detail; the structural decisions are:

1. **Layers redrawn** into strict ownership boundaries (above); added a
   **Problem orchestration** layer (M17).
2. **`PhysicsAsset` = renderable entity only**; `Contact`/`Constraint`/`Event`
   are pure semantics, visuals moved to `overlays/`/`glyphs`.
3. **`Pose2D` + local keypoints** (new M1.5) replace mutate-every-point-on-shift
   with canonical geometry + absolute pose (no drift under rotation/rolling).
4. **`RigidBody2D`** (new M1.5) owns generic `point_position/velocity/
   acceleration` + `MassProperties`; `point_velocity` is no longer a
   `CircularBody` feature. Rolling becomes a *constraint*, not the mechanism.
5. **`Pulley` → `RigidBody2D`** (not `Support`) + `FixedAxleConstraint`; enables
   movable/massive/released pulleys with no new class.
6. **Split connectors vs constraints**: `connectors.py` (Rope/MasslessLink/
   Cable) vs typed `constraints.py`; `hinge()` = marker + `PinConstraint`.
7. **Enums trimmed**: `MotionState` → `AT_REST|MOVING`; `ContactRegime` split
   into `ContactKinematics` + `FrictionModel` + `ContactLifecycle`;
   `ContactPersistence` → `ContactLocator` protocol; `EventKind`/`ConstraintKind`
   shrunk to a core + string tags / typed classes.
8. **`Surface` protocol pulled forward to M2** (needed by contact/rolling/rope),
   and expressed as *geometry attached to an entity*, not a `Support` subclass.
9. **M6 rebuilt around `SystemState`** (all bodies consistent at one `t`) with
   **typed `QuantityRef` observables** (no `extra: dict`), `InterpolationPolicy`,
   and `AssetState.shape` (so chains need no special trajectory pathway).
10. **Analytic solutions moved out of assets** into `motion/analytic/`;
    `OrbitPath`/`Top` are geometry-only.
11. **`ForceSpec` → `loads.py`** with a physical `value` (`QuantityRef|float`)
    separated from arrow length (`VectorScalePolicy`); added `TorqueSpec`/
    `ImpulseSpec`.
12. **Overlays own all UI** (`EventCounter`, contact markers, glyphs);
    `Recipe` stores **specs**, not `VGroup`s.
13. **`Assembly` is a facade** over `MechanicsModel`/`MechanicsRenderer`/
    `Timeline`.
14. **No `WEIGHT` vs `GRAVITY` physics split** — one `InteractionKind.GRAVITY`
    with different labels (`mg` vs `GMm/r²`).
15. **Added problem/corpus layer** (M17) with registry governance mirroring the
    math corpus; `mechanics/` receives only a resolved `ProblemRef`.

### Springs & fluids review (2026-09-05, round 3)

16. **Springs split across milestones** (not all in `springs.py`): `Spring` →
    `LinearSpring` (geometry) + `constitutive.py` laws (M10); SHM kinematics →
    `motion/analytic/shm.py` (M6); FBD/`isolate`/graphs → M9; events → M7 tags;
    *massive* spring → M11 `DistributedBody`. Extension/compression are signals,
    not enums. `TorsionSpring` emits a real `TorqueSpec`.
17. **`SystemState` made domain-generic** (entities + `fields` + observables) and
    a shared **`physics/core/`** extracted, so fluids reuse the same motion/
    timeline/signals infrastructure.
18. **`DistributedLoadSpec`** added to `loads.py` (hydrostatic/pressure loads).
19. **Fluids become a sibling domain** `assets/physics/fluids/` with its own plan
    series [`../fluids/`](../fluids/) (`F01`–`F06`); `mechanics/` is unchanged.
20. **Overlays split** into `overlays/common|mechanics|fluids`.

### Kinematics review (2026-09-05, round 4) — all MUST

21. **New foundational milestone M1.6** — a reusable **kinematics/transform/
    binding layer** (`core/{pose,transforms,frames}.py` + `kinematics/` package +
    `overlays/kinematics.py`), placed **before M6** and before advanced rolling/
    contact. SE(2) `Transform2D` distinguishes **point** (T+R) from **vector**
    (R only). Bindings (`RigidPoseBinding`, `PointAttachmentBinding`,
    `RelativePoseBinding`, `SurfacePoseBinding`, `PathPoseBinding`,
    `RollingPoseBinding`, `LookAtBinding`) + a parent-child scene graph drive
    every rigid body; `ApplyPoseTransition`/`FollowTrajectory` replace ad-hoc
    `.animate.shift().rotate()`.
22. **`RigidKinematicState`** (pose + optional velocity/accel/ω/α) is the canonical
    per-entity `EntityState` the solver supplies; `BodyState2D` is an alias.
23. **`pose.py` moves to `core/`**; `RigidBody2D` delegates point kinematics to
    `kinematics/rigid_body.py`. **Rule:** reuse the transform mathematics
    aggressively; never reuse the physics solution implicitly.

### Presentation review (2026-09-05, round 5) — all MUST

24. **New capstone layer/milestone M18** — a **presentation contract** between
    the human/AI physics and the assets: `ScenePhysicsData`, `NamedState`,
    `QuantitySpec`, `VectorSpec`, `EquationSpec`, `BindingSpec`, `ViewSpec`,
    `TransitionSpec`, and a declarative `LessonSpec` + `render_lesson` authoring
    API. Most videos are built from *named states + transitions + views*, not an
    ever-growing list of `animate_*` methods.
25. **Four strict layers**: Calculation (human/AI) → Asset → Lesson composition
    → Renderer. The asset layer MAY compute rendering geometry only; it MUST NOT
    decide conservation, IC location, friction direction, `N`, `ω`, energy, or
    separation (M18).
26. **Three-way relationship taxonomy** (M7): **geometric constraint** (`n=0`,
    must hold), **constitutive law** (`F=-kx`, produces force), **event/impact
    law** (`v_rel⁺=-e·v_rel⁻`, relates before/after) — kept distinct. Constraints
    are **phase-dependent** (`PhaseSpec.active_constraints`); a stick-collision
    *activates* a `ContactLockConstraint` (DOF drops) rather than merging bodies;
    `ConstraintEquationSpec` **validates** a supplied solution (residual), it
    does not solve. Velocity is discontinuous across an impact
    (`PiecewiseTrajectory`, never interpolated).
