# M13 — Orbital / Central-Force Assets

Status: **DRAFT FOR REVIEW**
Depends on: M6 (trajectory), M9 (overlays/graph). Files: `orbital.py` (NEW),
`overlays/orbit.py` (NEW), `palette.py` (+orbit colours), `bodies.py`
(`Particle` from M6), reuse `GraphBinding`.

## Revisions (architecture review 2026-09-05)

- **`OrbitPath` is geometry only** (review 15). `as_trajectory(kepler=True)`
  below **violates** the solver-free rule by solving Kepler timing inside a
  geometric asset. Move analytic dynamics to
  `motion/analytic/kepler.py::KeplerEllipseTrajectory`; `OrbitPath` keeps only
  `point_at(theta)` and the ellipse/foci/apsis keypoints.
  ```python
  orbit = OrbitPath(a=3, e=0.5, focus=sun.CM)         # geometry
  traj  = KeplerEllipseTrajectory(orbit, period=8)     # motion/analytic, solver-free provider
  ```
- **No separate `WEIGHT` vs `GRAVITY` interaction** (review 22). Near-surface
  `W = mg` is just gravity in the uniform-field approximation. Use one
  `InteractionKind.GRAVITY` (M1.5) with the label chosen per scene (`mg`
  terrestrial, `GMm/r²` orbital). Drop `ForceKind.GRAVITY`-as-new-interaction and
  the separate `COLOR_GRAVITY` *interaction* (a display colour is fine).
- Semantic directions (`TOWARD/AWAY_FROM/ALONG/NORMAL_TO/TANGENT_TO`) are kept —
  they resolve against `SystemState`, so orbital gravity `TOWARD(sun.CM)` and a
  spring `ALONG(axis)` are declarative.

## Goal

A major use-case family with only a few genuinely new primitives — most are
**explanation overlays**, not physical bodies (vision §8–9). Gravity is a
`ForceSpec` with a `TOWARD(target)` direction (see M-direction note below).

## `orbital.py` (NEW — the physical/geometric pieces)

```python
@dataclass
class CentralBody(PhysicsAsset):
    name="sun"; position=(0,0); radius=0.4; color=YELLOW; label="M"
    dynamics=STATIC
    build(): Circle(radius) filled; keypoint CM; (optional glow)
@dataclass
class OrbitPath(PhysicsAsset):
    name="orbit"; a=3.0; e=0.0; focus=(0,0); rotation=0.0   # semi-major a, eccentricity e
    dynamics=STATIC
    build():
        ellipse centred so one FOCUS is at `focus` (not the centre!)
        keypoints: focus, center, periapsis, apoapsis, other_focus
        return ellipse VMobject
    def point_at(theta) -> np.ndarray      # true-anomaly param on the ellipse
    def as_trajectory(period, kepler=True) -> Trajectory:
        # equal-areas timing if kepler=True (angular momentum conservation);
        # returns State(position=point_at(theta(t)), velocity=...) — analytic, solver-free.
@dataclass
class FocusMarker(PhysicsAsset):  # a small x at a focus
@dataclass
class ApsisMarker(PhysicsAsset):  # periapsis / apoapsis dots + labels
```

## `overlays/orbit.py` (NEW — explanation assets)

```python
def radius_vector(center, body) -> VGroup:          # Sun->planet arrow, updates live
def swept_area(orbit, theta0, theta1, focus) -> VMobject:  # shaded sector (Kepler II)
def central_force_arrow(body, toward) -> VGroup:    # gravity toward focus (COLOR_WEIGHT? no ->
                                                    # COLOR_GRAVITY, a new hue) 
def angular_momentum_overlay(center, body) -> VGroup:   # L = r x p indicator
def energy_panel_orbit(orbit, traj) -> VGroup:      # KE/PE/E vs r or t (reuse M9)
def apsis_velocities(orbit) -> VGroup:              # v arrows at peri/apo (vis-viva)
```

## Directions: add semantic directions (small `fbd.py` extension, used broadly)

```python
# resolve_direction gains callables so gravity/spring/normal are declarative (§26):
TOWARD(target_point)      -> unit(target - anchor)
AWAY_FROM(target_point)   -> unit(anchor - target)
ALONG(connector_axis)     -> unit(axis)
NORMAL_TO(surface, s)     -> surface.normal_at(s)
TANGENT_TO(surface, s)    -> surface.tangent_at(s)
# gravity: body.add_force(WEIGHT-like GRAVITY kind, at="CM", direction=TOWARD(sun.CM))
```
Add `ForceKind.GRAVITY="gravity"` + `COLOR_GRAVITY` so orbital gravity is distinct
from surface weight `mg` (both point-force but different pedagogy).

## Flagship demo — Kepler elliptical orbit (PROBE B)

```python
class M13Kepler(Scene):
    a=Assembly(); sun=CentralBody(position=(-1.5,0)); orbit=OrbitPath(a=3, e=0.5, focus=sun.CM)
    planet=Particle(mass=0.1, label="m")
    a.add(sun); a.add(orbit); a.add(planet)
    traj = orbit.as_trajectory(period=8, kepler=True)     # equal-areas timing
    planet.add_force(GRAVITY, at="CM", direction=TOWARD, magnitude=None)  # resolved live
    radius = radius_vector(sun.CM, planet)
    graph  = GraphBinding(x="time", y=lambda s: s.extra["r"], y_label="r").build(traj,0,8)
    # Kepler II: two equal-area sectors at peri vs apo over equal Δt
    areaP = swept_area(orbit, 0, dθ_peri, sun.CM); areaA = swept_area(orbit, π, π+dθ_apo, sun.CM)
    a.animate_trajectory(self, {"m": traj}, 0, 8, run_time=10)  # planet sweeps; radius+graph track
    # apsis markers + vis-viva velocity arrows at peri/apo
    finish_with_narration()
```

## Tests (`tests/test_assets_orbital.py`)

```
- OrbitPath: one focus at `focus`; periapsis/apoapsis keypoints at a(1∓e) from focus.
- point_at(0)==periapsis, point_at(π)==apoapsis.
- as_trajectory(kepler=True): equal areas in equal times (sector area over Δt
  near peri ≈ near apo, within tol) — the actual Kepler-II check.
- radius_vector points sun->planet.
- TOWARD(sun) direction on the planet == unit(sun.CM - planet.CM).
- swept_area sector vertices include the focus and two orbit points.
- ForceKind.GRAVITY colour == COLOR_GRAVITY (distinct from COLOR_WEIGHT).
```

## Render smoke
`M13Kepler`: frame near periapsis and near apoapsis; equal shaded areas, radius
vector + r-vs-t cursor tracking, gravity arrow always pointing at the Sun.

## Use cases unlocked
Circular/elliptical orbits, Kepler I/II/III, vis-viva, peri/apoapsis, escape
(bound→hyperbolic), orbital energy & effective potential (graph), angular-momentum
conservation, Hohmann transfer, hyperbolic flyby, binary/reduced-mass, satellite
thrust impulse (BEFORE→impulse→AFTER, via M12/M7). Completes PROBE B.
```
