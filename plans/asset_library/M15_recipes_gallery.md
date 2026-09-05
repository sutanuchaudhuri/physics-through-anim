# M15 — Recipe Catalogue + Large Regression Gallery

Status: **DRAFT FOR REVIEW**
Depends on: M1–M14. Files: `recipes/` package (NEW), `tests/test_recipes.py`,
a regression-gallery scene per family.

## Revisions (architecture review 2026-09-05)

- **`Recipe` stores specs, not `VGroup`s** (review 29). A recipe must stay
  semantic/declarative until rendering:
  ```python
  @dataclass
  class Recipe:
      assembly: Assembly
      events: EventSequence
      overlays: dict[str, OverlaySpec]        # was dict[str, VGroup]
      trajectories: dict[str, Trajectory]     # SystemState providers (M6)
      moments: dict[str, float]
      camera_anchors: dict[str, PointRef]     # was dict[str, np.ndarray]
  ```
  Rationale: enables AI reuse and eventual serialisation; the renderer builds the
  `VGroup`s from the specs.
- **The problem/corpus layer sits ABOVE recipes** (review 30), in M17. Recipes
  stay source-agnostic — no `KrotovProblem47` metadata inside `recipes/`; a
  `ProblemScenePlan` (M17) is what *selects and parameterises* a recipe.

## Revisions (presentation review 2026-09-05) — MUST

- **`Recipe` becomes a *presentation* recipe (MUST):** it carries named states,
  transitions, views, equations, and narration beats — not just assembly +
  overlays:
  ```python
  @dataclass
  class Recipe:
      assembly: Assembly
      states: dict[str, NamedState]           # M18
      transitions: list[TransitionSpec]
      views: dict[str, ViewSpec]
      equations: dict[str, EquationSpec]
      narration: dict[str, NarrationBeat]
      moments: dict[str, MomentSpec]
      trajectory: Trajectory | None = None    # optional continuous motion
  ```
  Most generated videos are built from **named states + transitions + views**.
- **Add the `spring_incline_collision` recipe (MUST):** the worked example — two
  blocks on an incline, one spring-attached, sliding into a collision that either
  sticks (activate `ContactLockConstraint`, DOF drops) or rebounds. Phases:
  pre-impact → impact → post-impact; solution (trajectories + `ImpactData`)
  supplied by the caller. Exercises M7 (phase constraints/gap), M10 (spring),
  M12 (impact), M18 (named states/views).

## Goal

Ship the **textbook compositions as recipes** (compositions, not inheritance —
vision §24) and a **broad regression gallery** (one small render per family,
§27) that tests framework health far better than isolated constructor tests.

## Recipe contract (compositions, never new physical subclasses)

```python
@dataclass
class Recipe:
    assembly: Assembly
    events: EventSequence
    overlays: dict[str, VGroup]        # named overlays ready to FadeIn
    trajectories: dict[str, Trajectory]
    moments: dict[str, float]          # named times ("slip_onset","apoapsis","impact_1")
    camera_anchors: dict[str, np.ndarray]
    def named(self, key) -> object     # resolve a named body/point/overlay/moment

# A recipe FUNCTION returns a Recipe assembled from generic assets:
def kepler_orbit(a=3, e=0.5, period=8, **kw) -> Recipe:
    sun=CentralBody(...); orbit=OrbitPath(a,e,focus=sun.CM); planet=Particle(...)
    asm=Assembly(); asm.add(sun); asm.add(orbit); asm.add(planet)
    return Recipe(assembly=asm, events=apsis_events(orbit,period),
                  overlays={"radius":..., "swept":..., "graph":...},
                  trajectories={"m": orbit.as_trajectory(period)},
                  moments={"periapsis":0,"apoapsis":period/2},
                  camera_anchors={"sun":sun.CM})
```

## Recipe catalogue (`recipes/`)

```
recipes/
  atwood.py        # atwood(m1,m2) -> Recipe  (M4 pulley+ropes+two blocks)
  rolling_spool.py # spool_pulled(angle) -> friction-direction family (M3+M4)
  rod_edge.py      # rod_falling_at_edge() -> phase transitions (M7+M8) [falling-rod doc]
  table_edge.py    # cylinder_at_table_edge() -> PROBE A (M3+M7+M8)
  kepler.py        # kepler_orbit(), hohmann_transfer(), hyperbolic_flyby() -> PROBE B
  chain.py         # chain_over_edge() -> PROBE C (M8+M11)
  collisions.py    # galperin(M,m), newtons_cradle(n), ballistic_pendulum() -> PROBE D
  pendulum.py      # physical_pendulum(), pendulum_with_peg() (M4 Hinge/Peg + M7 switch)
  oscillators.py   # mass_spring(), coupled_oscillators(), driven_damped() (M10)
  ladder.py        # ladder_two_contacts(), ladder_slipping() (M2 wall+floor, M7)
  noninertial.py   # block_in_truck(), puck_on_turntable() (M14)
```

Each recipe: **only generic assets**, returns a `Recipe`, names its key
moments/points so a scene (or an AI) can drive it without knowing internals.

## Regression gallery (the real health check — §27)

```python
# tests/test_recipes.py + a render gallery: ONE representative per family.
FAMILIES = {
  "translation": block_on_floor, "friction": impending_slide,
  "rolling": disk_on_incline, "moving_surface": block_on_conveyor,
  "pulley": massive_pulley, "hinge": physical_pendulum, "multi_contact": ladder,
  "curved_contact": bead_on_circular_track, "separation": body_leaving_convex,
  "edge": cylinder_table_edge, "distributed": chain_over_edge, "spring": mass_spring,
  "collision": block_block_impact, "repeated_collision": galperin,
  "topology": bullet_embeds_in_rod, "orbit": kepler_orbit, "central_force": gravity_to_focus,
  "noninertial": block_in_truck, "variable_mass": falling_chain_onto_scale, "com": person_on_boat,
}
```

## Tests (`tests/test_recipes.py`)

```
- Each recipe() builds a valid Recipe: assembly has expected bodies; events sorted;
  named moments resolve to floats; trajectories present for moving bodies.
- kepler_orbit: PROBE B invariants (from M13).
- cylinder_at_table_edge: PROBE A (contact-switch then separation events present).
- chain_over_edge: PROBE C (COM defined; supported/free portions).
- galperin: PROBE D (impact count grows; phase-space points).
- Recipe.named resolves bodies/points/overlays/moments.
- Every FAMILIES entry constructs without error (the regression sweep).
```

## Render smoke
Render the 20-family gallery at low quality (precomputed trajectories, so Rule 11
low-quality is valid); extract a frame per family; eyeball; clean up. This is the
single best signal of framework health.

## Use cases unlocked
The whole textbook: a human writes `kepler_orbit(e=0.6)`; an AI builds the same
semantic graph; both yield `Assembly + Trajectory + Events + Overlays`. All four
architecture probes pass here as first-class recipes.
```
