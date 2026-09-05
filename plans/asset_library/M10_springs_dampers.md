# M10 — Springs / Dampers / Richer Connectors

Status: **DRAFT FOR REVIEW**
Depends on: M1–M9. Files: `springs.py` (NEW), `kinds.py` (+`ForceKind.SPRING`,
`ForceKind.DAMPING`), `palette.py` (+spring/damper colours), reuse M9 overlays
+ M6 state + M7 events (SPRING_NATURAL_LENGTH).

## Revisions (architecture review 2026-09-05)

- **Split spring geometry, constitutive law, and constraint** (review 23):
  ```python
  SpringGeometry     # the drawn coil: endpoints A/B, coils, width, current length
  HookeLaw           # F(x) = -k x   (or a nonlinear/preloaded/piecewise variant)
  SpringConstraint   # / SpringConnector: ties two points, uses a law
  ```
  Rationale: nonlinear, preloaded, massive, rubber-string, and piecewise springs
  need geometry and force-law to be independent (Krotov elastic-element problems).
- **Solver-free boundary clarified** (review 23, mirrored in README/M06):
  evaluating `F = -k x` is a **local constitutive law**, which assets *may* do;
  it is not integrating equations of motion. The boundary is: *mechanics
  components may evaluate local force/constraint laws; they do not integrate the
  equations of motion.*
- Spring force is a `ForceSpec` with `value: QuantityRef|float` (M1.5) and
  `kind=InteractionKind.SPRING`; arrow length is a `VectorScalePolicy` decision,
  not the physical value.

## Revisions (springs & fluids review 2026-09-05)

- **Rename the primitive `Spring` → `LinearSpring`** with `Spring = LinearSpring`
  kept as a convenience alias. Rationale: leaves room for nonlinear/torsional/
  massive variants without overloading one name.
- **Extension / compression are derived signals, NOT enums** (springs review 1).
  Do **not** add `EXTENDED/COMPRESSED/NATURAL` to `kinds.py`. `deformation() =
  current_length - natural_length` (>0 extension, =0 natural, <0 compression) is
  a `QuantityRef("spring:1:x")` observable that `GraphBinding` (M9) can plot.
  ```python
  @dataclass
  class LinearSpring(Connector):
      natural_length: float = 1.0
      def deformation(self): return self.current_length - self.natural_length
      def extension(self):   return max(0.0, self.deformation())
      def compression(self): return max(0.0, -self.deformation())
  ```
- **Constitutive laws live in `constitutive.py`, separate from geometry**
  (springs review 2). `LinearSpring` is *geometry/endpoints only*; the force law
  is a separate object: `HookeLaw(k)`, `LinearDamperLaw(c)`, `TorsionalHookeLaw`.
  Evaluating `F = -k x` is a **local constitutive law** (allowed; not
  integration).
- **`TorsionSpring` produces a real torque via `TorqueSpec`** (springs review 3),
  not a mere `torque_hint`:
  ```python
  @dataclass
  class TorsionSpring:
      at: PointRef; body_a: AssetRef; body_b: AssetRef | None = None
      rest_angle: float = 0.0; stiffness: float | None = None
      def angular_deformation(self, system_state) -> float: ...
      def torque_on_a(self, system_state) -> TorqueSpec:     # tau = -kappa*(theta-theta0)
      def torque_on_b(self, system_state) -> TorqueSpec | None:
  ```
- **A *massive* spring is NOT a `LinearSpring`** (springs review 8). It is a
  distributed body — built on M11's `DistributedBody` base (`MassiveSpring`,
  alongside `ElasticString`, `FlexibleRod`). `LinearSpring` stays massless/ideal.
- **Extension/compression *visualisation* is an M9 overlay**
  (`overlays/deformation.py`), not baked into `LinearSpring.build`.
- **Spring events are M7 `tag`s** (`spring_natural_length`,
  `maximum_compression`, ...), not new `EventKind` values.

## Revisions (kinematics review 2026-09-05) — MUST

- **A spring's moving endpoint MUST follow its body via `PointAttachmentBinding`**
  (M1.6); the coil redraws through the binding + scene graph when the block
  moves. No scene recomputes the endpoint each frame.
- **`LookAtBinding` MUST be used where a force arrow points along the spring**
  (or a radius vector points at a target), instead of recomputing the direction.

## Goal

A connector family for oscillations. A spring **knows** its endpoints `A`,`B`,
current length, natural length, and draws a proper coil that stretches/compresses;
the solver (or a scene formula) supplies the actual force magnitude if needed.

## New enums / colours

```python
ForceKind += SPRING="spring"   # F_spring  -> COLOR_SPRING (a distinct hue)
ForceKind += DAMPING="damping" # F_damp    -> COLOR_DAMPING
COLOR_SPRING = "#5C7CFA"; COLOR_DAMPING = "#9775FA"
FORCE_COLORS updated.
```

## `springs.py` (NEW)

```python
@dataclass
class Spring(Connector):
    name="spring"; from_point=(0,0); to_point=(1,0)
    natural_length=1.0; coils=8; width=0.25; k=None   # k optional (for labels only)
    show_force=True; force_label="F_s"
    def build():
        a,b = as_point(from_point), as_point(to_point)
        axis = b-a; L=|axis|; coil = zigzag/helix polyline of `coils` along axis, width
        keypoints: A=a, B=b, mid; register current_length=L
        return VGroup(coil)
    def set_endpoints(a,b): rebuild coil between a,b (updates stretch visually)
    def deformation(): return current_length - natural_length   # + stretch / - compress
    def spring_force_on(body_ref, at, k_val=None):
        # F = -k*x along the spring axis toward natural length; direction only here.
        dir = unit(natural_config - current) ; body.add_force(SPRING, at, force_label, dir)
    def as_updater(scene, get_a, get_b):   # live-follow two moving bodies each frame

@dataclass
class Damper(Connector):
    name="damper"; from_point; to_point; show_force=True; force_label="F_c"
    build(): piston-in-cylinder glyph along the axis; keypoints A,B
    damping_force_on(body_ref, at, v_rel): dir opposes v_rel; add_force(DAMPING,...)

@dataclass
class TorsionSpring(Connector):
    name="torsion"; at=(0,0); rest_angle=0.0; turns=2
    build(): spiral glyph at `at`; keypoint H
    torque_hint(body_ref): angular restoring indicator (COLOR_SPRING arc)
```

## Spring in an assembly (live deformation)

```python
Assembly.animate_trajectory(...) already moves bodies; a spring bound with
`spring.as_updater(scene, get_a=lambda:body("m").keypoint("left"),
                   get_b=lambda:wall.contact_at(y))` redraws its coil each frame
so the coil visibly stretches/compresses as the mass moves — no bespoke updater.
```

## Demo — horizontal mass–spring (SHM) with phase portrait

```python
class M10MassSpring(Scene):
    a=Assembly(); wall=Wall(x=-3); m=Block(width=0.8, label="m")
    a.add(wall); a.add(m, place_on=Floor())
    spr=Spring(from_ref="wall.surface", to_ref="m.left", natural_length=2.0)
    a.connect(spr)
    # motion supplied by an analytic SHM trajectory (solver-free asset):
    def shm(t)->State: x=A*cos(ω t); return State(position=(x0+x,y), velocity=(-A*ω*sin(ω t),0))
    spr.spring_force_on("m", at="m.left")           # F_s along axis (FBD)
    graph = GraphBinding(x=lambda s:s.position[0]-x0, y=lambda s:s.velocity[0],
                         x_label="x", y_label="v").build(traj,0,T)   # phase portrait
    a.animate_trajectory(self, {"m": AnalyticTrajectory(shm)}, 0, T, run_time=8)
    # spring coil deforms live; F_s flips at natural length -> SPRING_NATURAL_LENGTH event
    finish_with_narration()
```

## Tests (`tests/test_assets_springs.py`)

```
- Spring.build keypoints A/B at endpoints; coil is a single VMobject with points.
- set_endpoints changes current_length; deformation() sign correct (stretch +).
- spring_force_on adds a SPRING force at the point, colour COLOR_SPRING,
  direction along the spring axis.
- Damper.damping_force_on direction opposes supplied v_rel.
- TorsionSpring registers H; torque_hint present.
- coil vertex count scales with `coils`.
```

## Render smoke
Mass–spring: coil visibly compresses/stretches over a cycle; `F_s` reverses at
natural length; phase-portrait cursor traces an ellipse. Confirm by two frames
(max compression, max stretch).

## Use cases unlocked
Horizontal/vertical mass-spring, coupled oscillators, normal modes, spring on
incline, pendulum+spring, damped/driven oscillator (with M9 graph), torsion
pendulum, effective spring combinations, spring-release collisions (M12).
