# F6 — Fluid Recipe Gallery

Status: **DRAFT FOR REVIEW**
Depends on: F01–F05, mechanics `Recipe` contract (M15). Files:
`fluids/recipes/`, `tests/test_fluids_recipes.py`, a render gallery.

## Goal

Ship the textbook fluid setups as **recipes** (compositions of generic fluid
assets, returning the same `Recipe` type M15 defines — specs, not `VGroup`s), and
a small **regression gallery** rendering one representative per family.

## Recipe catalogue (`fluids/recipes/`)

```python
def dam_pressure(height=3, density=1000) -> Recipe        # F02: reservoir + DamWall + pressure loads
def connected_tanks(h1, h2) -> Recipe                     # F03: two tanks + Pipe + HydraulicConnection
def tank_draining(h0, orifice_area) -> Recipe             # F04: OpenTank + Orifice + Jet + DrainTrajectory
def torricelli_jet(h0) -> Recipe                          # F04: efflux + jet trajectory + v=√(2gh)
def venturi(A1, A2) -> Recipe                             # F05: Pipe + ControlVolume + head diagram
def siphon(h_high, h_low) -> Recipe                       # F03/F04: over-the-top pipe + jet
def pipe_bend_force(angle, Q) -> Recipe                   # F05: ControlVolume + momentum flux resultant
def manometer(p_gauge) -> Recipe                          # F02: U-tube + PressureField + Δh
def floating_body(body, density) -> Recipe                # F01/F02: buoyancy = displaced-fluid weight
```

Each recipe: **only generic fluid + core assets**, returns a `Recipe`
(`assembly`, `events`, `overlays: dict[str, OverlaySpec]`,
`trajectories: dict[str, Trajectory]`, `moments`, `camera_anchors: PointRef`),
names its key moments so a scene (or an AI, via M17 `ProblemScenePlan`) can drive
it without knowing internals.

## Regression gallery (one render per fluid family)

```python
FLUID_FAMILIES = {
  "hydrostatic": dam_pressure, "communicating": connected_tanks,
  "efflux": tank_draining, "torricelli": torricelli_jet,
  "bernoulli": venturi, "siphon": siphon, "momentum": pipe_bend_force,
  "manometer": manometer, "buoyancy": floating_body,
}
```

## Tests (`tests/test_fluids_recipes.py`)

```
- Each recipe() builds a valid Recipe: fluid entities present; trajectories for
  time-varying quantities; overlays carried as specs (not VGroups).
- dam_pressure: resultant at center of pressure (F02 invariant).
- tank_draining: h(t) monotonically decreasing; jet speed = √(2gh) (F04).
- venturi: A1 v1 ≈ A2 v2 (continuity) and p2 < p1 (Bernoulli) (F05).
- floating_body: buoyant force == displaced-fluid weight (Archimedes).
- Every FLUID_FAMILIES entry constructs without error (the regression sweep).
- Recipes import only fluids/ + physics/core/, never problems/ (one-way dep).
```

## Render smoke
Render the fluid-family gallery at low quality (precomputed/analytic trajectories,
so low-quality is valid per SKILL Rule 11); one frame per family; eyeball; clean up.

## Use cases unlocked
The fluid textbook: `dam_pressure()`, `tank_draining()`, `venturi()` etc. as
first-class recipes, corpus-drivable through the shared M17 problem layer, sharing
the mechanics timeline / trajectory / graph / narration infrastructure.
