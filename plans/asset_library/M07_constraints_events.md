# M7 — Constraints + Event Model + Contact Switching / Separation

Status: **DRAFT FOR REVIEW**
Depends on: M1–M6. Files: `constraints.py` (NEW), `events.py` (NEW),
`contact.py` (enrich with `ContactPhase` transitions), `assembly.py`
(relations + event timeline), `kinds.py` (+`EventKind`, `ConstraintKind`).

## Revisions (architecture review 2026-09-05)

- **Events carry `changes`/`payload`, not full before/during/after `State`**
  (review 17). Duplicating trajectory data creates two sources of truth; instead
  derive before/after from `trajectory.state_at(t∓ε)`:
  ```python
  @dataclass(frozen=True)
  class Event:
      time: float; type: EventKind; participants: tuple[AssetRef,...] = ()
      changes: ConstraintChange | None = None    # activate/deactivate relations
      payload: Mapping[QuantityRef, QuantityValue] = ()   # e.g. impulse magnitude
      tag: str | None = None                     # "apoapsis", "rope_taut" (review 18)
  @dataclass(frozen=True)
  class ConstraintChange:
      activate: tuple[str,...] = (); deactivate: tuple[str,...] = ()
  ```
- **`EventKind` shrunk to a core + string tags** (review 18): `IMPACT`,
  `CONTACT_CHANGE`, `CONSTRAINT_CHANGE`, `THRESHOLD`, `TURNING_POINT`,
  `IMPULSE`, `CUSTOM`. `APOAPSIS`/`ROPE_TAUT`/`SPRING_NATURAL_LENGTH` become
  `tag=`s so recipes add named events without editing `kinds.py`.
- **Typed constraint classes**, not `Constraint(kind=ROLLING, data=dict)`
  (review 19): `PinConstraint`, `FixedPointConstraint`, `DistanceConstraint`,
  `RopeLengthConstraint`, `RollingConstraint`, `PathConstraint`, `SlotConstraint`
  (shared with M4). Each is an inspectable dataclass.
- **`Timeline` is its own object** (review 28), owning trajectory + events +
  moments; `Assembly` delegates to it (facade). Event highlights/counters are
  **overlays** (`overlays/events.py`), not part of the semantic `events.py`.
- **Contact lifecycle** uses the `ContactLifecycle` enum from M2
  (`ESTABLISHING/ACTIVE/SEPARATING`); separation is a `CONTACT_CHANGE` event
  whose `changes.deactivate` drops the contact — the N=0 criterion is supplied by
  the trajectory/threshold, not computed in the asset.

## Revisions (springs & fluids review 2026-09-05)

- **Spring / string events are `tag`s on the core `EventKind`, not new enum
  values** (reaffirms review 18). A spring crossing natural length is
  `Event(type=THRESHOLD, tag="spring_natural_length")`; a turning point is
  `Event(type=TURNING_POINT, tag="maximum_compression")`. Other tags:
  `maximum_extension`, `string_taut`, `string_slack`, `spring_released`,
  `spring_breaks`. Rationale: keeps `EventKind` small; recipes add named spring
  events without editing `kinds.py`. When each occurs is supplied by the
  trajectory/threshold, never solved in the asset.

## Revisions (presentation review 2026-09-05) — MUST

- **Three-way relationship taxonomy (MUST keep distinct):**
  1. **Geometric constraint** — must hold exactly (`n=0`): block-on-incline,
     pin/slot, hinge, fixed rope length, two blocks stuck. Removes a DOF.
  2. **Constitutive law** — produces force/torque from deformation (`F=-kx`):
     spring/damper/torsion. **A spring is NOT a geometric constraint** (its
     length is free); it lives in M10, referenced here for contrast.
  3. **Event / impact law** — relates before/after (`v_rel⁺ = -e·v_rel⁻`):
     collision, bounce, stick, rope-going-taut. Lives in the event/impact model.
- **Constraints are phase-dependent (MUST):** do not treat constraints as
  existing forever. A phase declares its **active** set:
  ```python
  PhaseSpec(name="before_collision", active_constraints=("m1_on_incline","m2_on_incline","spring_attach"))
  PhaseSpec(name="after_sticking",  active_constraints=(...,"m1_m2_locked_contact"))
  ```
  Same infrastructure handles rope-taut, body-leaves-track, rolling-begins,
  rolling→slipping, spring-loses-contact, rod-pivots-then-falls, block-hits-wall.
- **Contact candidates + gap function (MUST):** approaching bodies are a
  `ContactCandidate` with a **geometric** gap; a collision fires when `g=0`.
  ```python
  @dataclass
  class ContactCandidate:
      body_a: AssetRef; body_b: AssetRef; feature_a: PointOrSurfaceRef; feature_b: PointOrSurfaceRef
      def gap(self, system_state) -> float: ...      # g>0 separated, g=0 touching, g<0 impossible
  ```
- **Stick vs rebound = constraint-topology change (MUST):** a perfectly
  inelastic impact **activates** a `ContactLockConstraint` (`s2-s1=d`), dropping
  a DOF — the two bodies still exist (so both individual FBDs *and* the system
  FBD with the internal force cancelled remain available); it does NOT merge them
  into a new body. A rebound keeps both coordinates and just separates.
- **`ConstraintEquationSpec` validates, does not solve (MUST):**
  ```python
  ConstraintEquationSpec(id="blocks_stuck", latex=r"s_2-s_1-d=0",
                         residual=lambda s: s["block2.s"]-s["block1.s"]-d)
  # framework checks |residual| < tol on a SUPPLIED solution -> ✓/✗; never solves.
  ```

## Goal

Make **relationships** and their **changes** first-class. A `Constraint` says
what governs motion (rolling, pinning, fixed-distance, rope-length, slot); an
`Event` marks the instant a relationship changes (impact, release, separation,
rope-taut, slip-start, contact-switch). Neither solves physics — a scene /
trajectory supplies *when* events happen; the assets make them easy to
visualise. This is the architecture lesson of the falling-rod doc: every time
the constraint changes, the governing description must be reconsidered.

## New enums (`kinds.py`)

```python
class ConstraintKind(StrEnum):
    CONTACT = "contact"; ROLLING = "rolling"; PINNED = "pinned"
    FIXED_DISTANCE = "fixed_distance"; ROPE_LENGTH = "rope_length"; SLOT = "slot"

class EventKind(StrEnum):
    IMPACT="impact"; SEPARATION="separation"
    CONTACT_ESTABLISHED="contact_established"; CONTACT_SWITCH="contact_switch"
    SLIP_START="slip_start"; SLIP_STOP="slip_stop"; ROLLING_START="rolling_start"
    ROPE_TAUT="rope_taut"; ROPE_SLACK="rope_slack"
    CONSTRAINT_RELEASE="constraint_release"; CONSTRAINT_ACTIVATE="constraint_activate"
    SPRING_NATURAL_LENGTH="spring_natural_length"; TURNING_POINT="turning_point"
    APOAPSIS="apoapsis"; PERIAPSIS="periapsis"; ESCAPE="escape"
```

## `constraints.py` (NEW)

```python
@dataclass
class Constraint:
    kind: ConstraintKind
    participants: tuple[str,...]      # asset refs, e.g. ("cyl","incline")
    active: bool = True               # constraints can switch off at an event
    data: dict = field(default_factory=dict)   # e.g. {"length": 2.0} for a rope
    def marker(assembly) -> VGroup:   # optional glyph (e.g. dashed radius, slot rails)
```

## `events.py` (NEW)

```python
@dataclass(frozen=True)
class Event:
    time: float
    kind: EventKind
    participants: tuple[str,...] = ()
    before: State | None = None
    during: State | None = None
    after:  State | None = None
    note: str | None = None           # symbolic-only tag (Rule 9)

@dataclass
class EventSequence:                  # §6, §11 — a first-class subsystem
    events: list[Event] = field(default_factory=list)
    _cursor: int = 0
    def add(event); def sort_by_time()
    @property current -> Event; next -> Event|None; count -> int
    def advance() -> Event            # step the cursor
    def at_or_before(t) -> Event      # last event with time<=t
    def highlight(assembly, event) -> VGroup:   # flash participants (uses Phase)

# Phase helpers (generalise M1's Phase enum) — before/during/after a collision:
def phase_of(seq, t) -> Phase        # BEFORE first event / DURING an event / AFTER
def triptych(scene, build_before, build_during, build_after):
    # lay the three phase snapshots side by side (Rule 16 together) with labels
```

## Contact lifecycle (enrich `contact.py`)

```python
Contact.transition_to(phase: ContactPhase, scene=None):
    # ESTABLISHING -> ACTIVE -> SEPARATING; animate marker fade/scale accordingly
Contact.on_separation():             # N -> 0: fade the normal arrow, mark P gone
    # a scene calls this at a SEPARATION Event (criterion N=0 supplied externally)
```

## Assembly: relations + timeline

```python
Assembly.add_relation(obj):          # Contact | Constraint  (stored, namespaced)
Assembly.constraints -> list; contacts -> list
Assembly.timeline: EventSequence
Assembly.at(t):                      # apply the relationship set valid at time t
    ev = timeline.at_or_before(t); toggle constraints/contacts per ev.kind
Assembly.play_events(scene, traj_map): # drive trajectory + fire each event's highlight
```

## Flagship demo — contact switch + separation (probe A skeleton, no M8 edge yet)

```python
class M7ContactSwitch(Scene):
    # a body constrained to a surface, then released -> free flight
    a = Assembly(); floor=Floor(); blk=Block()
    a.add(floor); a.add(blk, place_on=floor)
    c = Contact(body_ref="block", surface_ref="floor", regime=RESTING)
    a.add_relation(c)
    a.add_relation(Constraint(CONTACT, ("block","floor")))
    a.timeline.add(Event(time=1.0, kind=CONSTRAINT_RELEASE, participants=("block","floor")))
    # trajectory: rest until t=1, then projectile fall
    a.play_events(self, {"block": AnalyticTrajectory(rest_then_fall)})
    # at t=1: contact.on_separation() fades N; body free-falls; event highlight flashes
    finish_with_narration()
```

## Tests (`tests/test_assets_events.py`)

```
- EventSequence.sort_by_time orders; current/next/advance/count behave.
- at_or_before(t) returns the last event with time<=t (and None before the first).
- phase_of: t<first => BEFORE; within an event's [t,t+dur] => DURING; else AFTER.
- Constraint.active toggles at CONSTRAINT_RELEASE via Assembly.at(t).
- Contact.transition_to changes phase; on_separation removes the normal ForceSpec.
- Assembly.add_relation stores Contact and Constraint separately; queryable.
```

## Render smoke
`M7ContactSwitch`: frame at t=0.5 (resting, N present), frame at t=1.5 (falling,
N gone) — the constraint change is visible.

## Use cases unlocked
Contact switch / separation / release as generic events; before/during/after
triptychs; the timeline that M12 (collision sequences) and M13 (apsis/escape
events) build on. Completes the constraint half of probes **A** and **D**.
