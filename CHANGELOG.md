# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `.gitignore` so only source code and documentation are version-controlled
  (rendered videos under `media/` and audio under `assets/audio/` are excluded).
- `CHANGELOG.md` and this versioning convention.
- `plans/README.md` index of all planning/spec documents, with a link to the
  Jira project (**PAC — Physics Animation Creator**) that tracks the asset-library
  and fluids roadmap.
- Self-documenting `make help` that lists every target and its description.
- Promoted the physics framework to a scalable, cross-domain namespace
  `physics_through_anim.physics` (core/kinematics/shared + domain packages);
  documented in `plans/ARCHITECTURE.md` and `plans/DIAGRAMS.md`.
- Vendored a pymunk `SpaceScene` at `src/physics_through_anim/sim/` replacing the
  `manim-physics` rigid-body plugin.
- TDD scaffold for milestone **M1.5** (`physics/core/{pose,refs,loads}`,
  `physics/mechanics/{massprops,rigidbody}`) with a red/green spec suite
  (`tests/test_m1_5_pose_rigidbody.py`) and `plans/asset_library/M01_5_TESTPLAN.md`.
- TDD scaffold for milestones **M1.6–M18**: stub modules across
  `physics/{core,kinematics,mechanics,mechanics3d,overlays,recipes,problems}` plus
  a per-milestone spec file each and `plans/asset_library/SCAFFOLD_STATUS.md`
  (suite: 50 passed, 38 xfailed).
- Cumulative asset-demo lesson **asset_demo** (`render-lesson asset_demo`,
  `stitch-lesson asset_demo`) rendering the block-on-floor FBD (M1) and an
  M1.5-computed `v = omega x r` vector.
- Render-smoke scene **asset_demo s02** (`KinematicsBindings`) cycling the eight
  M1.6 acceptance cases (translation, hinge rotation, general plane motion, point
  attachment, spring redraw, rolling without drift, path-tangent following, linked
  rods) -- every pose driven by the kinematics bindings, not hand-tuned shifts.
- Deterministic render-layout framework `physics/render/layout.py` (`Region`,
  `Layout`, `standard_bands`, `avoid_overlap`): content is placed into named
  rectangular bands (header/stage/equation/caption) so the FBD/kinematics stage
  carries only vector *symbols* while formulas live in the equation band, and
  symbol-label collisions resolve deterministically. Covered by
  `tests/test_render_layout.py` (6 specs). Reusable by M9 overlays and M18 views.
- Render-smoke scene **asset_demo s03** (`SupportsAndContact`): the conveyor
  contact cases (running/stopped belt with FBD + contact glyph) and the wedge --
  a cylinder rolling into a floor+ramp corner that seats tangent to both walls
  and pierces neither.
- Render **`Mask`** (`physics/render/mask.py`): a cosmetic skin (Manim mobject,
  image, SVG or raw matrix/lamina) that follows a point-mass CM pose. Geometry is
  cosmetic (a mask may be fully transparent) and its rotation is decoration --
  the physical vectors and lever arms carry the meaning. `place()` is drift-free
  and anchors the CM (`cm_local`); `from_matrix`/`transparent` constructors.
  Design in `plans/asset_library/RENDER_MASK.md`; specs in `tests/test_render_mask.py`.
- Render **skins** (`physics/render/skins.py`): `radial_polygon(radii)` builds a
  silhouette from an input vector of per-vertex radii, and `rock_skin(...)` a
  seeded jagged rock -- a customizable/extensible *picture* passed as a body's
  `skin`. Specs in `tests/test_render_skins.py`.
- Render-smoke scene **asset_demo s04** (`RockRolling`): a rock skin rolling as a
  disk (contact `P`, CM, weight, Rule 5 velocity field) -- swap the skin, keep
  the physics.

### Implemented
- Milestone **M1.5**: `physics/core/{pose,refs,loads}` (Pose2D transforms, typed
  ref parsing, VectorScalePolicy arrow length) and
  `physics/mechanics/{massprops,rigidbody}` (parallel-axis inertia, absolute pose,
  generic point velocity/acceleration). Its 18 specs are green.
- Milestone **M1.6** — reusable kinematics layer: `physics/core/transforms.py`
  (`Transform2D` SE(2), point vs vector), `physics/core/frames.py` (`Frame2D`
  world/local maps), `physics/core/state.py` (`RigidKinematicState`/`BodyState2D`,
  `InterpolationPolicy`), and the `physics/kinematics/` package
  (`rigid_body` point position/velocity/acceleration, `instantaneous_center`,
  `point` relative motion, `rolling` `Δθ = -Δs/R`, and pose-driven `bindings`:
  `RigidPoseBinding`, `PointAttachmentBinding`, `RelativePoseBinding`,
  `PathPoseBinding`, `RollingPoseBinding`). `RigidBody2D` now delegates its point
  kinematics here. Specs in `tests/test_kinematics.py` + `tests/test_m1_6_kinematics.py`
  (37 pass).
- Milestone **M2** — supports, contact semantics, and the non-penetration
  constraint. One oriented-boundary primitive `Wall(angle_deg, facing)` with
  `Floor`/`Ceiling`/`Incline`/`Conveyor` presets and a `Corner` composite; **no
  wall has a free-body diagram**. `surfaces.py` (`LineSurface`/`FloorSurface`/
  `InclineSurface`) gives every wall a point/tangent/normal. `contact.py` models a
  `Contact` relation (no mobject) with split enums (`ContactKinematics`/
  `FrictionModel`/`ContactLifecycle`) and `ContactLocator`s
  (`FixedWorldPoint`/`SurfaceCoordinate`/`BodyKeypoint`); glyphs live in
  `overlays/contact.py`. **Walls and floors are impenetrable**: `geometry.py`
  provides signed-distance `clearance`, the two-wall `corner_seat` solver, and a
  `no_penetration_clamp`; `Assembly` rejects any body that pierces a wall and
  seats round bodies in a corner, and `RollingPoseBinding` takes a `clamp` hook.
  Specs in `tests/test_m02_supports_contact.py` + `tests/test_m02_non_penetration.py`.
- Milestone **M3** — rolling/rotation bodies. `mechanics/circular.py`
  (`CircularBody` + `Disk`/`Ring`/`Hoop`/`Sphere2D`/`Cylinder` presets with
  per-shape inertia factors, and a spinnable `Pulley` with named rim points):
  drawable round bodies with rim geometry, contact `P`, auto weight at CM, and
  the Rule 5 rolling velocity field (`v = ω × (point − P)`). Each accepts a `skin`
  mobject so the *picture* (a rock/wheel/image) is decoupled from the disk
  *physics*. `mechanics/motion.py::roll_group` rolls a body at `Δθ = -Δs/R` with
  no drift. Specs in `tests/test_m03_rolling.py`.
- **Round-body seating on any wall is the non-penetration constraint, not manual
  placement.** `Assembly.add(body, place_on=incline)` seats a round body tangent
  to the slope (`clearance == 0`, centre one radius out along the normal) via
  `geometry.seat_circle_on_surface`; `motion.roll_along_surface` rolls it along
  the surface tangent at that fixed offset, so it is **always in contact** and
  never pierces. Flagship scene **asset_demo s05** (`CylinderOnIncline`) seats a
  cylinder with `place_on=ramp` (no coordinates) and rolls it down in contact.
- **Rotated block-on-incline seating.** `place_on=ramp` now also seats a polygon
  body: `PhysicsAsset.rotate` turns the block's base parallel to the slope and it
  is seated flush (min-corner `clearance == 0`). `geometry.body_shape` builds
  polygon corners from edge-midpoint keypoints so clearance is correct for a
  rotated block.
- Milestone **M4** — connectors & assemblies. `mechanics/connectors.py`
  (`Rope`/`Cable`/`MasslessLink` flexible links + `Hinge`/`PinJoint` pin glyphs):
  a rope draws a line/slack arc between two points, `tension_on(body, at, toward)`
  declares a `TENSION` force along it, `slips=True` adds hash marks; a hinge marks
  a pinned point and `reaction_on(body)` declares a `REACTION`. Typed
  `constraints.py` (`Pin`/`FixedPoint`/`Distance`/`RopeLength`/`Rolling`/`Path`/
  `Slot`/`FixedAxle`/`ContactLock`) stay inspectable dataclasses. `Assembly` gains
  `resolve(ref)`, `connect(rope)` (resolves `from_ref`/`to_ref` to world points),
  and `hang(pulley, from_ceiling)`. Flagship scene **asset_demo s06**
  (`PulleyTwoRopes`): a ceiling-hung pulley with two name-resolved ropes and their
  `T_A`/`T_B` tensions vs `mg`. Specs in `tests/test_m04_connectors.py`.
- **Rope wrapping a pulley** (`connectors.RopeOverPulley`): a rope over a pulley
  is derived, not hand-placed -- two tangent **contact points**, the **arc (arch)**
  riding the rim between them, and two straight free ends, with `turns > 1` for a
  spindle/capstan wrap. `wrap_angle()` reports the subtended wrap; `set_endpoints`
  redraws it live so the pulley can spin without slipping. M4 plan doc extended
  with the arch/spindle sections. Specs in `tests/test_rope_over_pulley.py`. Demo
  scenes **asset_demo s09** (`ProjectileOnIncline`, a formula-driven projectile
  landing on a ramp) and **s10** (`RopeLiftsMass`, a rope pulled at ~120 deg over a
  pulley lifting a mass, no slip).
- **Contact threshold** (`geometry.TOUCH_TOL`, `contact_state`): a body within a
  small band of a wall reads as *touching* (contact), not *penetrating*, so
  pixel/numerical-scale overlaps no longer trip the non-penetration guard;
  `Assembly(contact_tol=...)` tunes the band. `penetrates`/`touches` now use the
  band.
- **Slack string with variable length** (`connectors.SlackString`, `Rope.rest_length`):
  a string with a natural length whose drawn shape is not fixed -- it **sags** when
  its ends are closer than `rest_length` and snaps **taut** (straight) when
  stretched; `is_taut()` reports the state and `set_endpoints` transitions it live.
  Specs in `tests/test_contact_and_slack.py`; demo scene **asset_demo s11**
  (`SlackStringDemo`) shows the sag→taut transition.
- Milestone **M5** — `Rod` body + catalogue gallery + SKILL Rule 19.
  `mechanics/rod.py` (`Rod`: keypoints `A`/`B`/`CM`, `point_at(s)`, `massless`
  omits the auto weight). New **SKILL Rule 19** ("build scenes from the physics
  asset library when asked") documents the catalogue, constraint-based placement,
  model-driven FBD, cosmetic skins, and binding-based motion. Gallery scene
  **asset_demo s07** (`AssetGallery`) renders one tile per family for QA. Specs in
  `tests/test_m05_rod.py` + `tests/test_assets_catalog.py` (every family builds and
  exposes its keypoints).
- Milestone **M6** — the time dimension: solver-free `Trajectory` providers.
  `core/trajectory.py` (`AnalyticTrajectory` wraps `t -> SystemState`;
  `SampledTrajectory` linearly interpolates a `SystemState` between samples).
  `PhysicsAsset.apply_state` moves an asset to a supplied `RigidKinematicState`
  via absolute pose (drift-free, rotation tracked). `Assembly` gains semantic
  queries (`body`/`assets`/`forces_on`) and `apply_states`/`animate_trajectory`
  (samples `state_at(t).entities` each frame). New point-like `Particle` body.
  Flagship scene **asset_demo s08** (`ProjectileFormula`): a particle follows an
  analytic parabola (assets consume, never integrate) with an apex freeze-frame
  showing `v` horizontal. Specs in `tests/test_m06_state_trajectory.py` +
  `tests/test_assets_state.py`.
- Milestone **M7** — constraints, events, and contact switching. `core/events.py`
  (`EventKind` small core + string `tag`s, `Phase`, `Event`, `ConstraintChange`,
  and `EventSequence` with `sort_by_time`/`at_or_before`/cursor + `phase_of`).
  `Contact` gains a lifecycle (`transition_to`, `on_separation` drops the normal
  force at N→0). `Assembly` carries **relations + a timeline**: `add_relation`
  (Contact vs typed constraint), `constraints`, and `at(t)` toggles constraints
  active/inactive per the timeline's `ConstraintChange`s. Flagship scene
  **asset_demo s12** (`ContactSwitch`): a held body (reaction R balances mg) is
  released at a `CONSTRAINT_CHANGE` event — R→0, the contact separates, and it
  free-falls from a supplied trajectory. Specs in `tests/test_m07_events.py` +
  `tests/test_assets_events.py`.
- Milestone **M8** — curved surfaces / edges / tracks. `surfaces_curved.py`
  extends the M2 `Surface` protocol: `ParametricSurface` (finite-difference
  tangent/normal/curvature for any curve), `CircularTrack`/`ConvexSurface` (hill)/
  `ConcaveSurface` (bowl)/`RoundedEdge`/`Rail` (pure geometry, owned by an
  entity), and drawable `Table` (owns a top `Surface` + a `SharpEdge`), `SharpEdge`
  (pivot/separation point `E`), `Peg`, `Slot` (yields a `SLOT` constraint).
  `separation_imminent(N)` (N→0 criterion). Flagship scene **asset_demo s13**
  (`TableEdge`): a cylinder rolls on a table top, the contact switches to the
  sharp edge, then N→0 and it separates as a spinning projectile. Specs in
  `tests/test_m08_curved_surfaces.py`.
- Milestone **M9** — explanatory overlays + graph binding, all rendered from the
  same state the bodies expose (no scene rebuilds an FBD/field/graph by hand).
  `overlays/graphs.py`: a `Signal` protocol (`TimeSignal`, `QuantitySignal`
  resolving a `QuantityRef` against `SystemState.observables`, `CallableSignal`)
  and `GraphBinding` — samples a trajectory into an axes+curve and syncs a cursor
  to a `ValueTracker`, so one clock drives both the body and the plot (N-vs-θ,
  ω-vs-t, energy-vs-t, phase portraits). `overlays/kinematics.py`: `velocity_vector`/
  `acceleration_vector` (Rule-2 colours), the exact **Rule-5 `rolling_velocity_field`**
  (each rim arrow ⟂ point−contact, contact marked v=0), `trajectory_trail`.
  `overlays/momentum.py`: `momentum_vector` (∝ m|v|), `system_com_marker`
  (mass-weighted). Flagship scene **asset_demo s14** (`RollingFieldGraph`): a
  rolling disk with the Rule-5 field and a synced ω-vs-t graph. Specs in
  `tests/test_m09_overlays.py`.
- Milestone **M10** — springs / dampers + constitutive laws. `springs.py` keeps
  geometry separate from the force law: `LinearSpring` (alias `Spring`) draws a
  zigzag coil between two points that stretches/compresses (`set_endpoints`),
  with derived `deformation()`/`extension()`/`compression()` signals (no enums)
  and `spring_force_on` declaring a `SPRING` force along the axis toward the
  natural length; `Damper` (dashpot glyph, `damping_force_on` opposes v_rel);
  `TorsionSpring` (spiral glyph + `torque_hint`). Force laws are pure locals:
  `HookeLaw` (F=-kx), `LinearDamperLaw` (F=-cv), `TorsionalHookeLaw` (τ=-κθ) —
  evaluating them is a constitutive law, not integration. New `ForceKind.SPRING`/
  `DAMPING` + `COLOR_SPRING`/`COLOR_DAMPING`. Flagship scene **asset_demo s15**
  (`MassSpringSHM`): a horizontal mass-spring in SHM — the coil deforms live, the
  restoring `F_s` reverses at the natural length, and a velocity-vs-displacement
  phase portrait traces an ellipse. Specs in `tests/test_m10_springs.py`.
- M10 (cont.) — **series & parallel spring banks**. `SpringGroup` + the
  `series_springs`/`parallel_springs` helpers wire several `LinearSpring`s between
  one pair of connectors: series draws coils end-to-end joined by junction dots
  (`1/k_eff = Σ 1/k_i`, lengths add), parallel stacks coils sharing both endpoints
  (`k_eff = Σ k_i`); both render explicit square end connectors. `LinearSpring`
  gains an optional `k`. Two scenes: **s16** (`SpringBanks`) shows each bank built
  by one helper call with its `k_eff`; **s17** (`InclineSpringPulleyMachine`) is a
  framework stress test — a fixed support → spring → block → spring → rope over a
  pulley → hanging mass on an incline, every piece a library asset wired only by
  its endpoints, the whole chain coupled by one tracker.
- **Pulley mounting on a support (two flavours).** `circular.mount_pulley` +
  `Incline.mount_pulley` fix a pulley to a point in one of two ways: flavour 1
  (`PulleyMount.ON_SUPPORT`) holds the axle off the point on an immovable
  `PulleyBracket` (hatched pad + post); flavour 2 (`AT_POINT`) puts the axle on
  the point. Both return a `MountedPulley(pulley, bracket, axle)` with a
  `FixedAxleConstraint`. Scene s17 now caps its incline with flavour 1. Specs in
  `tests/test_pulley_mount.py`.
- Milestone **M11** — chains / distributed-mass bodies. `chain.py` adds a
  `DistributedBody` base (material coord `s ∈ [0,1]` + an evolving `path(s) ->
  world` shape, solver-free) with `Chain` (`CONTINUOUS` curve or `LINKED`
  segments), `ElasticString`, `MassiveSpring` (mass-carrying, unlike M10's ideal
  spring) and `FlexibleRod`. A chain exposes end keypoints `A`/`B`, a
  mass-weighted `com()`, `material_marker(s)`/`material_markers` (which piece is
  which), `portion(s0,s1)` (supported vs free sub-curve), and `set_path` for live
  motion; `linear_density = mass/length`. Flagship scene **s18** (`ChainOverEdge`,
  probe C): a chain pours over a table's sharp edge — the split point slides, the
  COM marker drifts, and the green (supported) / orange (free) portions track the
  shape. Specs in `tests/test_m11_chain.py`.
- **Chain garment mask** (render). `render/mask.py` adds `garment_along_path` +
  `PathMask`: a transparent ribbon (offset ±width/2 along the path normal) that
  hugs a distributed body's skeleton, renders on top of the line vector, and
  fades to reveal it. `DistributedBody` gains a render-free `skin_builder`
  (`path -> Mobject`, supplied by the render layer) + `skin` + `attach_skin`, so
  the cosmetic garment tracks the skeleton through `set_path` while the line
  stays the physics. Scene **s19** (`ChainGarmentMask`) drapes the garment over
  the skeleton, then fades it out to the bare vector. Specs in
  `tests/test_render_path_mask.py`.
- Milestone **M12** — collisions / impulse / event sequences. `core/impact.py`
  adds `ImpactData` (a *supplied* impact law: before/after velocities +
  restitution + impulse, never solved) and `PiecewiseTrajectory` (pre-impact ->
  impact -> post-impact segments; velocity STEPs at each boundary while position
  stays continuous — never interpolated through an impact). `overlays/events.py`
  adds `collision(a,b,t,e)` (builds an `IMPACT` `Event`), `EventCounter`
  (symbol-only `n = k` tally), `impulse_arrow` (∝|J|), and `velocity_before_after`
  (dim pre + bright post arrows). Flagship scene **s20** (`GalperinCounter`,
  probe D): a heavy + light block bounce between a wall; a tiny in-scene elastic
  solver supplies the schedule, the library renders piecewise-constant motion, an
  `EventCounter` ticks each impact, and a phase-space overlay plots each
  post-collision state on the invariant circle (the reflections whose count
  encodes π). Specs in `tests/test_m12_collisions.py`.
- M12 (cont.) — **collision families**. `core/impact.py` gains two supplied-law
  primitives: `reflect_velocity(v, normal, e_n, e_t)` (2-D restitution off a
  surface — ball rebound on an incline/wall, elastic/inelastic) and
  `MomentumFlux(rate, v_rel)` (variable-mass reaction `F=(dm/dt)v_rel`) with
  constructors `wind` (`ρAv²`), `onto_belt` (sand on a moving belt),
  `chain_pileup` (chain falling on the floor, flux `λv²`) and `rocket`
  (`u|dm/dt|`). Spring (soft) collisions and CM-invariance-under-internal-forces
  are documented in `M12_collisions.md`. Scene **s21** (`BallReboundIncline`)
  shows a ball reflecting off an incline (incident/normal/rebound vectors,
  velocity STEP at the bounce). Specs in `tests/test_m12_collisions.py`.
- M12 (cont.) — **off-centre / angular impulse tools**. `core/impact.py` adds
  `Impulse`, `impulse_response(mass, inertia_cm, r, J)` → `(delta_v=J/m,
  delta_omega=(r×J)/I)` (a central blow only translates; an end blow spins too),
  `center_of_percussion(inertia_cm, mass, pivot_to_cm)` (the bat/rod sweet spot,
  `2L/3` for an end-pivoted rod), and `perfectly_inelastic((m,v),…)` (ballistic
  pendulum capture). `Rod` now exposes `inertia_cm` (`mL²/12`) and
  `mass_properties()`. `overlays/events.angular_impulse_markers` draws the blow
  (`J`), CM `Δv`, and spin `Δω` from the response. Scene **s22** (`RodImpulse`):
  an end impulse on a horizontal rod — CM translates while the struck end leads in
  a spin about the CM. Covers bat-and-ball, rod-on-wall, pendulum-jolt. Specs in
  `tests/test_m12_collisions.py`.
- **Point-of-interest annotations + momentum-flux scenes.** New
  `overlays/annotations.py`: `point_marker(point, "P")` (a labelled dot),
  `follow_keypoint(marker, body, key)` (bind it to a moving keypoint so it tracks
  live), and `callout(point, "Look at point P")` (text + leader line) — every
  returned group fades in/out, so a developer scripts when a static or dynamic
  point of interest appears. Scenes **s23** (`SandOnBelt`) renders the belt
  momentum-flux force `F=(dm/dt)v_belt` with a static marker P (callout) and a
  dynamic marker Q riding a grain; **s24** (`RocketThrust`) renders the thrust
  `F=u\,\dot m` with a nozzle marker N. Specs in `tests/test_annotations.py`.
- Milestone **M13** — orbital / central-force. `orbital.py` (geometry only):
  `CentralBody` (the force centre) and `OrbitPath` (an ellipse with one **focus**
  at `focus`, `point_at(theta)`, apsis/foci keypoints), plus the solver-free
  analytic provider `KeplerEllipseTrajectory` (equal-areas timing via Kepler's
  equation) and declarative directions `toward`/`away_from`. New
  `overlays/orbit.py`: `radius_vector`, `swept_area` (Kepler-II sector),
  `central_force_arrow`. New `ForceKind.GRAVITY` + `COLOR_GRAVITY`/`COLOR_ORBIT`.
  Flagship scene **s25** (`KeplerOrbit`, probe B): a planet on an ellipse with the
  Sun at a focus — gravity always points at the Sun, the radius vector sweeps, an
  r-vs-t graph tracks, and two focus sectors swept in equal time have equal area.
  Specs in `tests/test_m13_orbital.py`.
- Milestone **M14** — reference frames / non-inertial overlays. `reference_frames.py`:
  `FrameKind` (INERTIAL/TRANSLATING/ROTATING), a supplied `FrameState` (never
  integrated), and `ReferenceFrame` whose `to_frame` is a pure kinematic map on
  `core.frames.Frame2D` (+ `is_inertial`, an observer `icon`). `overlays/frames.py`:
  `pseudo_force_arrow` (dashed, neutral-grey `COLOR_PSEUDO` — inertial/centrifugal/
  coriolis/euler directions from the frame state) and `frame_badge`, kept a
  separate semantic class from real forces. Flagship scene **s26**
  (`AcceleratingTruck`): a block in an accelerating truck shown in two frames —
  the ground frame (real N/mg/f) and the truck frame (add the dashed `-m a_f`).
  Specs in `tests/test_m14_frames.py`.
- Milestone **M15** — recipe catalogue + regression gallery. `recipes/`: a
  spec-only `Recipe` (assembly + events + overlays + trajectories + named
  moments/camera anchors; `named()` resolves any of them) and a `catalogue.py` of
  textbook compositions built only from generic assets — the four probes
  (`kepler_orbit`, `cylinder_at_table_edge`, `chain_over_edge`, `galperin`) plus
  `atwood`, `mass_spring`, and a **`FAMILIES`** registry of 20 representatives
  (translation … com). The 20-family regression sweep (construct-without-error) is
  the framework's best health check. Flagship scene **s27** (`RecipeGallery`): a
  grid of recipe thumbnails, each a one-call composition. Specs in
  `tests/test_m15_recipes.py`.
- **Declarative layout anchors.** `render/layout.py` adds an `Anchor` enum
  (`CENTER`, `TOP_LEFT`, `BOTTOM`, …), `Region.anchor(where, offset=…, pad=…)`,
  `Region.columns(n, gap)`/`rows(n, gap)`, and `stage_region()` — so scenes place
  content by **named anchors and panels** (e.g. `left, right = stage_region()
  .columns(2)`; `title.move_to(left.anchor(Anchor.BOTTOM))`) instead of eyeballed
  coordinates; a numeric `offset` is the escape hatch. Scene s26 refactored to
  use it. Specs in `tests/test_layout_anchors.py`.
- **Named points + semantic value tokens** (authoring ergonomics, replace magic
  numbers). `render/layout.py` adds `NamedPoints` — a registry to define points by
  **id/enum** and read coordinates, `vector`, and translation `distance` by id
  (`pts.define(A=(-4.5,1.2), B=(1.5,1.2)); pts.distance("A","B")`; `StrEnum` keys
  work). `render/tokens.py` adds mix-in enums that **are** their value so they drop
  in wherever a number was written, with a raw number still allowed as the custom
  escape hatch: `Size` (body extent), `Span` (support half-width), `Beat` (play
  durations), `Dir` (unit-vector tangents/normals). Scenes s16/s27 use anchors +
  named points; s03 uses the tokens (`Block(width=Size.LARGE)`,
  `Floor(half_width=Span.WIDE)`, `ContactFrame(tangent=Dir.RIGHT, normal=Dir.UP)`,
  `run_time=Beat.QUICK`). Specs in `tests/test_layout_anchors.py`,
  `tests/test_tokens.py`.

### Known limitations (revisit as milestones land)

The `asset_demo` lesson shows what is renderable today; these gaps are tracked so
we revisit each when its milestone ships:

- **Animate over time** — scenes are static reveals today; time-based animation
  arrives with **M6** (`Trajectory.state_at(t)` driving frames).
- **Drive a body's pose from state each frame** — the **M1.6** bindings +
  `Transform2D` now compute the pose; `asset_demo` s02 renders eight cases driven
  by them. Stepping a binding from a time-sampled `Trajectory` arrives with **M6**.
- **Round rolling bodies** (`Disk`, `Cylinder`) arrive in **M3**; only `Block` is
  drawable today.
- **Stop hand-drawing arrows/graphs** — overlays (`velocity_vector`,
  `rolling_velocity_field`, `GraphBinding`) arrive in **M9**; the demo hand-draws
  its velocity arrow.

### Fixed
- **Resolved** the `asset_demo` s01 `v`-vs-`N` label overlap (SKILL Rules 8/9):
  the new `physics/render` layout framework keeps the FBD stage symbol-only and
  moves `v = omega x r` into the equation band, so the formula never lands on a
  force arrow.

### Changed
- Replaced the `manim-physics==0.2.4` dependency with `pymunk` and raised the
  Python cap to `>=3.11,<3.14` (3.12 and 3.13 now supported). Added an
  `audioop-lts` shim for 3.13 (pydub still imports the removed stdlib `audioop`).
  Verified: 19 tests pass and the pymunk scenes render on 3.11, 3.12, and 3.13.
- Merged `documents/plan.md` into `plans/ROADMAP.md`; removed the `documents/`
  folder so all planning lives under `plans/`.
- Rewrote `README.md`: added a Jira reference, a full table of `make` commands,
  and corrected the repository-layout section.

## [0.1.0] — 2026-09-05

### Added
- Offline-first Manim studio CLI (`main.py`) with per-scene rendering, stitching,
  named compilations, and a publish workflow.
- Flagship 28-scene "Rolling, Slipping and Friction" lesson.
- Composable physics asset-library plan (M1 shipped; M1.5–M18 + fluids F1–F6
  planned) under `plans/`.
