# F4 — Tank Draining / Efflux

Status: **DRAFT FOR REVIEW**
Depends on: F01, F03, `motion/analytic`. Files: `fluids/boundaries.py`
(`Orifice`), `fluids/regions.py` (`Jet`), `motion/analytic/torricelli.py`.

## Goal

Draining through a small hole. **`Orifice`** is a boundary opening (separate from
`Pipe`, which is a conduit), and a **`Jet`** shows the efflux. `h(t)`,
`v_exit(t)`, `Q(t)` come from a `DrainTrajectory` provider (Torricelli as an
algebraic relation — not integrated inside the asset). Flagship: a tank draining
through a small hole.

## `boundaries.py` — `Orifice` (distinct from `Pipe`, review 20)

```python
@dataclass
class Orifice(PhysicsAsset):
    name="orifice"; boundary: SurfaceRef = ""   # "tank.right_wall"
    height: float = 0.0                          # y of the hole
    width: float = 0.15; cd: float = 0.62        # discharge coefficient (display/label)
    dynamics=STATIC
    def build(): small gap glyph on the boundary; keypoint "O" at the hole
```

## `regions.py` — `Jet`

```python
@dataclass
class Jet(PhysicsAsset):
    name="jet"; origin: PointRef = ""; speed: float = 0.0; g: float = 9.81
    def build(): parabolic streamline from the orifice (projectile arc of the efflux)
    def apply_state(state):    # speed from v_exit(t); redraw the arc + length
```

## Motion provider (`motion/analytic/torricelli.py`)

```python
@dataclass
class DrainTrajectory(Trajectory):     # solver-free provider (algebraic + optional ODE sample)
    area_tank: float; area_orifice: float; h0: float; g=9.81
    def state_at(t) -> SystemState:
        h = h(t)                        # ½ from Torricelli/continuity (algebraic or precomputed)
        v = sqrt(2*g*h)                 # Torricelli: constitutive relation, not integration
        Q = cd*area_orifice*v
        return SystemState(entities={"water": FluidRegionState(free_surface_height=h)},
                           fields={}, observables={QuantityRef("orifice:v"):v,
                                                   QuantityRef("orifice:Q"):Q,
                                                   QuantityRef("tank:h"):h})
```

## Demo — draining tank

```python
class F4Draining(Scene):
    tank = OpenTank(...); water = FluidRegion(container="container", fill_level=H0)
    orifice = Orifice(boundary="container.right_wall", height=0.2)
    jet = Jet(origin="orifice.O")
    traj = DrainTrajectory(area_tank=A, area_orifice=a, h0=H0)
    animate_trajectory(self, {"system": traj}, 0, T, run_time=8)
    # water level drops; jet speed/length shrink; v arrow at outlet (overlays/velocity)
    graph = GraphBinding(x=TimeSignal(), y=QuantitySignal("tank:h")).build(traj,0,T)
    # storyboard: reservoir + h(t) graph -> orifice close-up -> v arrow -> Torricelli note
    finish_with_narration()
```

## Tests (`tests/test_fluids_draining.py`)

```
- Orifice registers "O" on the boundary at the given height (distinct from Pipe).
- DrainTrajectory.state_at: v == sqrt(2 g h); Q == cd*a*v; h decreases with t.
- Jet.apply_state redraws with length increasing with speed; arc is parabolic.
- SystemState from DrainTrajectory carries water FluidRegionState + observables.
- GraphBinding("tank:h") is monotonically decreasing.
```

## Render smoke
`F4Draining`: level falls, jet shortens/slows, `h(t)` cursor descends.

## Use cases unlocked
Torricelli efflux, draining tanks, jet trajectory, siphons (with F03), and the
`Orifice` vs `Pipe` distinction. All timing supplied by a `Trajectory`.
