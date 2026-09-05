# M4 — Connectors & Assemblies (Rope, Hinge, PinJoint)

Status: **DRAFT FOR REVIEW**
Depends on: M1–M3. Files: `connectors.py` (NEW), `assembly.py` (attach/hang,
namespaced rope segments, combined FBD with tensions), `__init__.py`.

## Revisions (architecture review 2026-09-05)

> The sections below are **superseded where they conflict** with this block.

- **Split connectors from constraints** (review 6). A rope is a flexible physical
  link; a hinge/pin is primarily a *joint/constraint*. They no longer share a
  `Connector` base:
  ```python
  # connectors.py  (flexible physical links)
  Rope, MasslessLink, Cable
  # constraints.py (typed, inspectable — review 19, no kind+data dict)
  PinConstraint, FixedPointConstraint, DistanceConstraint, RopeLengthConstraint,
  RollingConstraint, PathConstraint, SlotConstraint
  # glyphs.py / overlays/constraints.py (visuals only)
  HingeMarker, PinMarker
  ```
- **`hinge(...)` becomes a convenience** that creates a `HingeMarker` (glyph) +
  a `PinConstraint` — the semantic model stays clean while callers keep a
  one-liner. `Hinge`/`PinJoint` as `Connector` subclasses (below) are removed.
- **Typed constraint classes instead of `Constraint(kind=..., data=dict)`**
  (review 19). Rationale: an AI can inspect a constructor contract; a dict
  becomes the same untyped dumping ground as `State.extra`.
- **`Pulley` is attached via a constraint, not `Assembly.hang()` implicit
  physics** (review 5): `FixedAxleConstraint(pulley, at="pulley.axle",
  to="ceiling.H")`. `hang()` may remain as pure *placement* sugar, but it must
  not encode the pin relationship.
- Tensions are declared as `ForceSpec`/`loads` with a `value: QuantityRef`
  (M1.5), so `T_A`/`T_B` can later be bound to a solver quantity, not just an
  arrow length.

## Revisions (kinematics review 2026-09-05) — MUST

- **Rope/spring endpoints and pulley mounts MUST follow their bodies via
  bindings** (M1.6): `PointAttachmentBinding` (endpoint follows a body keypoint)
  and `RelativePoseBinding` (weld a mount to a moving support). No scene
  recomputes attachment geometry by hand.
- **`Assembly` MUST maintain the parent-child transform graph** so moving a body
  propagates to its attached rope/spring/hinge endpoints automatically
  (Block moves → hook world point moves → connector redraws).
- **`hinge()` = `HingeMarker` + `PinConstraint`**, and the pin's render adapter
  MUST align `rod.A` to `H` through a binding, not manual placement.

## Goal

Physical links that connect two named points, tension declared at the right
keypoints, and the flagship **pulley + ceiling + two ropes (30°/60°)** assembly
with `T_A`/`T_B`. Hinge and pulley mount are **separable** assets (a hinge is
distinct from the wall it pins to — the vision's separability requirement).

## `connectors.py` (NEW)

```python
@dataclass
class Connector(PhysicsAsset):
    name="connector"; dynamics=STATIC
    from_ref: str = ""            # "pulley.A"  (assembly keypoint ref)
    to_ref:   str = ""            # "mass1.top"
    # resolved to world points by the Assembly at add() time

@dataclass
class Rope(Connector):
    name="rope"; from_point=(0,0); to_point=(0,-1)   # world; or set via refs
    tension_label="T"; slips=False; sag=0.0          # sag>0 draws a slack catenary-ish curve
    show_tension=True
    def build():
        a,b = as_point(from_point), as_point(to_point)
        Line(a,b, stroke_width=3) (or slack arc if sag>0)
        keypoints: from=a, to=b, mid=(a+b)/2
        if slips: add slip hash marks near the wheel end
    tension_on(body_ref, at, toward):        # declare a TENSION ForceSpec
        body.add_force(TENSION, at=at, label=tension_label, direction=unit(toward-at))
    # A rope pulls each end toward the other along its own line.

@dataclass
class Hinge(Connector):           # a pin joint that FIXES a point; SEPARATE asset
    name="hinge"; at=(0,0); pins="rod.A"; to="wall"
    def build():
        Dot(at) + small ring glyph   # visual pin
        set_keypoint("H", at)
    reaction_on(body_ref):         # hinge exerts a reaction (unknown dir) at H
        body.add_force(REACTION, at="H", label="R", direction="auto")

@dataclass
class PinJoint(Connector):        # semantic "A pinned to B at point": reaction PAIR
    name="pin"; at=(0,0); a_ref=""; b_ref=""
    build(): Dot(at); set_keypoint("H", at)
    # declares equal/opposite REACTION on both bodies (Newton's 3rd) when asked
```

## Assembly enhancements (`assembly.py`)

```python
add(asset, place_on=None, attach=None):
    ...
    if attach:                      # ("ceiling", x) or a keypoint ref
        anchor = resolve(attach)
        shift asset so its mount keypoint == anchor
resolve(ref) -> np.ndarray:         # "pulley.A" -> world point (semantic query)
    return self.keypoints[ref]
connect(rope):                      # resolve from_ref/to_ref -> world, then add
    rope.from_point = resolve(rope.from_ref); rope.to_point = resolve(rope.to_ref)
    re-build rope; add; namespace rope keypoints ("rope1.from"/"rope1.to")
hang(pulley, from_ceiling):         # place pulley below a ceiling anchor
fbd(include): union members' FBDs   # now includes rope tensions & hinge reactions
```

## Flagship demo — pulley + ceiling + two ropes at 30°/60°

```python
class M4PulleyTwoRopes(Scene):
    a = Assembly()
    ceil = Ceiling(y=3.0)
    pul  = Pulley(center=(0,2.2), radius=0.5, rope_angles={"A":30,"B":60}, rotates=True)
    mA = Block(width=0.7, label="m_1"); mB = Block(width=0.7, label="m_2")
    a.add(ceil); a.hang(pul, from_ceiling=ceil)
    a.add(mA); a.add(mB)
    ropeA = Rope(from_ref="pulley.A", to_ref="m_1.top", tension_label="T_A")
    ropeB = Rope(from_ref="pulley.B", to_ref="m_2.top", tension_label="T_B", slips=True)
    a.connect(ropeA); a.connect(ropeB)
    # tensions at the pulley keypoints A/B (up along each rope):
    pul... declare TENSION T_A at "A" toward m_1, T_B at "B" toward m_2
    # masses feel tension up along their rope:
    ropeA.tension_on("m_1", at="m_1.top", toward=resolve("pulley.A"))
    ropeB.tension_on("m_2", at="m_2.top", toward=resolve("pulley.B"))
    play(FadeIn(a.mobject)); play(FadeIn(a.fbd()))     # T_A, T_B, mg's all correct
    pul.animate_spin(self, turns=0.5)                  # or frozen if rotates=False
    # slip vs no-slip: ropeB.slips=True shows slip hashes at the wheel
    finish_with_narration()
```

Separability demo (hinge distinct from wall):
```python
wall = Wall(x=-3); rod = Rod(...); hinge = Hinge(at=wall.contact_at(1.5), pins="rod.A", to="wall")
a.add(wall); a.add(rod); a.add(hinge)     # each fades in/out independently
hinge.reaction_on("rod")                  # reaction R at H on the rod's FBD
```

## Tests (`tests/test_assets_connectors.py`)

```
- Rope resolves from_ref/to_ref via Assembly.resolve to correct world points.
- Rope keypoints from/to/mid; tension_on adds a TENSION force at the given point,
  direction = unit(toward - at), colour == COLOR_TENSION.
- Hinge registers "H"; reaction_on adds a REACTION force (COLOR_REACTION).
- Pulley two-rope assembly: T_A at pulley.A, T_B at pulley.B, angles 30/60.
- slips=True adds slip-marker submobjects; slips=False does not.
- Assembly.resolve("pulley.A") returns the same point Pulley registered.
```

## Render smoke
`M4PulleyTwoRopes` low quality; frame shows two ropes leaving the wheel at
30°/60°, tension labels `T_A`,`T_B` up along each rope, both masses with `mg`
down, slip hashes on rope B.

## Use cases unlocked
Atwood (M15 recipe), massive/movable pulley variants, rope-over-peg (with M8),
hinged rod / physical pendulum (with M3 `Rod` + this `Hinge`), and the
tension/reaction FBD vocabulary reused by springs (M10) and collisions (M12).
