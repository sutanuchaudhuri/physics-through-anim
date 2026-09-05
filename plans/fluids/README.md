# Fluid Mechanics Domain — Plan Series (Index)

Status: **DRAFT FOR REVIEW** (2026-09-05)
Scope: a **sibling** physics domain to mechanics, sharing the domain-neutral
`physics/core/` (state, trajectory, timeline, signals, refs, events, loads).
Fluid physics objects stay cleanly separated from rigid-body mechanics.

Parent framework index: [`../asset_library/README.md`](../asset_library/README.md)

> Fluids is **not** placed inside `mechanics/`. It is
> `src/physics_through_anim/physics/fluids/`, reusing `physics/core/`.
> Milestones use an **F-prefix** (F01–F06), not the mechanics M-numbers.
> Canonical namespace: [../ARCHITECTURE.md](../ARCHITECTURE.md) (read any
> `assets/physics/...` path as `physics/...`).

## Why a sibling domain

The mechanics roadmap explicitly describes itself as a mechanics framework;
`Reservoir`/`Dam`/`Pipe`/`Water` do not belong there. But fluids can reuse the
same `Trajectory`, `Timeline`, signals, named moments, `GraphBinding`, and
narration sync — so SHM, a Krotov pulley problem, a dam-pressure lesson, and a
draining reservoir share one rendering + teaching pipeline. The enabler is the
**domain-generic `SystemState`** (entities + fields + observables) from the M6
springs & fluids revision.

## Shared core reused (no new motion engine)

```
physics/core/     state.py trajectory.py timeline.py signals.py refs.py events.py loads.py
# SystemState.entities[fluid_ref] = FluidRegionState(free_surface=..., volume=...)
# SystemState.fields[pressure] = FieldState(p(x,y));  fields[velocity] = FieldState(v(x,y))
# Trajectory.state_at(t) -> SystemState drives h(t), Q(t), v_exit(t) — solver-free.
```

## Package layout (`physics/fluids/`)

```
fluids/
   regions.py         # FluidRegion, FluidRegionState, FreeSurface
   containers.py      # Container2D, Reservoir, Tank, OpenTank, ClosedTank
   boundaries.py      # DamWall, Orifice, Inlet, Outlet
   pipes.py           # Pipe
   connections.py     # HydraulicConnection
   fields.py          # PressureField, VelocityField, FieldState
   control_volume.py  # ControlVolume, Section
   overlays/          # (registered under physics overlays/fluids)
      pressure.py velocity.py level.py flow.py graphs.py
   recipes/           # dam_pressure, connected_tanks, tank_draining, venturi, ...
```

## Milestone series

| F | Title | Doc | Flagship |
| --- | --- | --- | --- |
| F01 | Fluid region + containers | [`F01_core_fluid_container.md`](F01_core_fluid_container.md) | static water in an open tank |
| F02 | Hydrostatics + pressure | [`F02_hydrostatics_pressure.md`](F02_hydrostatics_pressure.md) | reservoir against a vertical dam |
| F03 | Pipes + connected tanks | [`F03_pipes_connected_tanks.md`](F03_pipes_connected_tanks.md) | two tanks equalising through a pipe |
| F04 | Tank draining / efflux | [`F04_draining_efflux.md`](F04_draining_efflux.md) | tank draining through a small hole |
| F05 | Control volume / Bernoulli | [`F05_control_volume_bernoulli.md`](F05_control_volume_bernoulli.md) | Venturi / continuity |
| F06 | Fluid recipe gallery | [`F06_recipes_gallery.md`](F06_recipes_gallery.md) | one render per fluid family |

## The simplest mapping (from the review)

| What you want | Where it belongs |
| --- | --- |
| Water | `FluidRegion` (F01) |
| Water level | `FreeSurface` + `FluidRegionState` (F01) |
| Reservoir / tank | container geometry (F01) |
| Two tanks + pipe | `HydraulicConnection` recipe (F03) |
| Pipe | `Pipe` (F03) |
| Dam | `DamWall` + distributed pressure loads (F02) |
| Hydrostatic pressure | pressure-field overlay (F02) |
| Draining tank | trajectory + `Orifice` + `Jet` (F04) |
| `h(t)`, `Q(t)`, `v(t)` graphs | shared `GraphBinding` |
| Force on dam / pipe | shared loads/FBD + `DistributedLoadSpec` / control volume |

## Solver-free contract (same as mechanics)

Fluid assets evaluate geometry and local relations (hydrostatic `p = ρgh`,
Torricelli `v = √(2gh)` as a *constitutive/algebraic* relation) but never
integrate the governing equations. `h(t)`, `Q(t)`, `v_exit(t)` enter through a
`Trajectory` provider (`motion/analytic/` or precomputed/CFD data).
