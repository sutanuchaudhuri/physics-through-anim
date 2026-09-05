# M12 — Collisions / Impulse / Event Sequences

Status: **DRAFT FOR REVIEW**
Depends on: M6 (state/snapshot), M7 (events/EventSequence/Phase). Files:
`overlays/momentum.py` (+impulse), `events.py` (collision helpers, `EventCounter`),
`overlays/graphs.py` (phase-space plot via `GraphBinding`). No new body needed —
collisions are compositions of existing bodies + wall + events (vision §11–12).

## Revisions (architecture review 2026-09-05)

- **`EventCounter` moves to `overlays/events.py`** (review 25) — semantics vs
  visualisation. `events.py` holds the event *model*; the counter, flashes, and
  phase-space dots are overlays. Rationale: the same rule that keeps `Contact`
  and `Constraint` render-free.
- **Events use `changes`/`payload`, not embedded states** (review 17, from M7):
  a collision is an `IMPACT`/`IMPULSE` event with an impulse magnitude in
  `payload`; before/after come from `trajectory.state_at(t∓ε)`.
- **Phase-space overlay is a `GraphBinding` over signals** (review 14): points
  are `(QuantityRef("body:M:v"), QuantityRef("body:m:v"))` sampled at each
  post-impact time — no `State.extra`.
- Velocity discontinuities across an impact use `InterpolationPolicy.STEP_*`
  (review 16), so the collision instant isn't smeared unless intentionally
  visualising the impulse interval.

## Revisions (presentation review 2026-09-05) — MUST

- **Velocity is discontinuous across an impact (MUST):** use a
  `PiecewiseTrajectory` — pre-impact segment → `ImpactEvent` → post-impact segment.
  **Never interpolate velocity through the impact** (`InterpolationPolicy.STEP_*`);
  position stays continuous (`s(t_c⁻)=s(t_c⁺)`).
- **The impact law is supplied, not solved (MUST):**
  ```python
  ImpactData(time=1.73, before={"m1.v":4.2,"m2.v":0.7}, after={"m1.v":1.4,"m2.v":3.1},
             restitution=e, impulse=J)
  ```
  The framework renders before/after velocity arrows + impulse; it does not
  compute `v⁺`.
- **Momentum conservation is an impact *approximation* (MUST document):** for the
  two-block-on-incline case, `m1 v1⁻ + m2 v2⁻ = m1 v1⁺ + m2 v2⁺` holds only if the
  spring/gravity/friction impulse over the (short) impact is negligible. Whether
  to include it is a **calculation-layer** decision; the caption/narration MUST
  state the assumption.
- **Stick → activate a `ContactLockConstraint`; rebound → separate (MUST):** the
  bodies are never merged. Both individual FBDs remain, plus a system FBD where
  the internal contact force cancels (M7 revision).

## Goal

Represent collisions as **event sequences over generic bodies** with
before/during/after phases, impulse overlays, an event counter, and a
phase-space overlay — including the infinite-collision (Galperin/π) family. The
assets visualise; a scene/trajectory supplies *when* and *what* each collision is.

## Overlays / helpers

```python
# overlays/momentum.py
def impulse_arrow(body, J, at="CM") -> VGroup:      # J vector (impulse) at a point
def velocity_before_after(body, v_before, v_after) -> VGroup:  # two arrows + labels
# events.py
@dataclass
class EventCounter:                 # on-screen tally of collisions so far (§11)
    seq: EventSequence; kinds=(IMPACT,)
    def glyph(t) -> VGroup:         # "n = k" symbol-only (Rule 9), k = count<=t
def collision(m_a, m_b_or_wall, t, restitution=1.0, **kw) -> Event:
    return Event(time=t, kind=IMPACT, participants=(...), note=f"e={restitution}")
```

## Collision recipe engine (reused by M15)

```python
# A scene supplies the collision schedule (times + resulting velocities), which a
# 1-D solver or the Galperin formula computes OUTSIDE the assets. The library:
#   - holds bodies + wall in an Assembly,
#   - drives them with piecewise SampledTrajectory between events,
#   - fires EventSequence highlights + EventCounter at each impact,
#   - can freeze BEFORE/DURING/AFTER snapshots (M6 StateSnapshot + M7 triptych).
def run_collision_sequence(scene, assembly, schedule: EventSequence, traj_map):
    assembly.timeline = schedule
    assembly.play_events(scene, traj_map)      # M7 machinery
```

## Phase-space overlay (for repeated collisions)

```python
phase_space = GraphBinding(                    # M9 GraphBinding, reused
    x=lambda s: s.extra["v1"], y=lambda s: s.extra["v2"],
    x_label="v_1", y_label="v_2").build(traj, 0, T)
# Galperin: successive states are reflections on a circle; the count of bounces
# relates to π. The overlay plots each post-collision (v1,v2) point.
```

## Flagship demo — infinite block collisions (PROBE D)

```python
class M12Galperin(Scene):
    a=Assembly(); wall=Wall(x=-4); big=Block(width=1.4, mass=100, label="M")
    small=Block(width=0.6, mass=1, label="m")
    a.add(wall); floor=Floor(); a.add(big, place_on=floor); a.add(small, place_on=floor)
    schedule = EventSequence(); # times + (v1,v2) after each impact from the 1-D elastic solver
    for k, (t, v1, v2) in enumerate(precomputed_bounces):
        schedule.add(collision(..., t=t)); # store v's in the SampledTrajectory states
    counter = EventCounter(schedule, kinds=(IMPACT,))
    ps = phase_space_overlay(...)
    run_collision_sequence(self, a, schedule, {"M": trajM, "m": trajm})
    # each impact: flash participants, tick counter glyph, add a phase-space point,
    #              optionally impulse_arrow on both bodies during DURING phase.
    finish_with_narration()
```

BEFORE/DURING/AFTER triptych for a single 1-D collision (M7 `triptych`):
```python
triptych(self,
    build_before=lambda: snapshot(t_before, show=("body","velocity")),
    build_during=lambda: snapshot(t_impact, show=("body","impulse")),
    build_after =lambda: snapshot(t_after,  show=("body","velocity")))
```

## Tests (`tests/test_assets_collisions.py`)

```
- collision() builds an IMPACT Event at t with the right participants/note.
- EventCounter.glyph(t) count == number of IMPACT events with time<=t.
- impulse_arrow length ∝ |J|; velocity_before_after draws two arrows.
- run_collision_sequence installs the schedule as assembly.timeline and applies
  the trajectory (body positions match traj at sampled t).
- phase-space GraphBinding plots one point per post-collision state.
```

## Render smoke
`M12Galperin`: frames after 1st, 2nd, 3rd bounce showing the counter increment,
the blocks' positions, and growing phase-space points. (Non-physics scene ⇒ low
quality fine, per Rule 11 — the trajectory is precomputed, not a pymunk sim.)

## Use cases unlocked
1-D elastic/inelastic blocks, ball–wall restitution, Newton's cradle, Galperin,
bouncing ball, ballistic pendulum (with M4), off-centre disk impact (angular
impulse), sticking (compound `RigidAssembly` after impact), explosion/
fragmentation (topology change). Completes PROBE D.
```
