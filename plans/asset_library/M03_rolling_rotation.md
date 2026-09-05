# M3 — Rolling / Rotation Bodies (Disk, Sphere2D, Cylinder, Pulley)

Status: **DRAFT FOR REVIEW**
Depends on: M1, M2. Files: `bodies.py` (+`CircularBody`,`Disk`,`Sphere2D`,
`Cylinder`,`Ring`,`Hoop`), `supports.py` (+`Pulley`), reuse SKILL Rule 7
`animate_rolling`, Rule 5 tangential vectors.

## Revisions (architecture review 2026-09-05)

> The sections below are **superseded where they conflict** with this block.

- **Bodies re-parent on `RigidBody2D`** (M1.5, review 4). `point_velocity` is a
  **generic rigid-body** method (`v_P = v_G + ω × r_{P/G}`), **not** a
  `CircularBody` feature. The `CircularBody.point_velocity` below is removed;
  scenes call `RigidBody2D.point_velocity(ref, state)` (the same Rule 5
  `(r_y, -r_x)` cross-product), which also serves rods, plywood sheets, and
  arbitrary points — the Krotov rigid-body kinematics family.
- **`Pulley` is a `RigidBody2D`, not a `Support`** (review 5). Move it to
  `bodies.py`. A fixed pulley is `Pulley + FixedAxleConstraint`; a movable
  pulley is `Pulley + RopeConstraint`; massive/released/accelerating-frame
  pulleys need **no new class**. Rationale: `Pulley(Support)` only models one
  fixed-axle diagram and fails for the movable/compound variants in Krotov.
  ```python
  class Pulley(RigidBody2D):
      radius=0.5; rope_points={"A":30,"B":60}   # local keypoints on the rim
      def animate_spin(...)   # visual spin about the axle keypoint
  # M4 pins it: FixedAxleConstraint(pulley, at="pulley.axle", to="ceiling.H").
  ```
- **Rolling is a `RollingConstraint`, not the mechanism that computes point
  velocities** (review 4/5). `motion.py::roll_group` stays as a *rendering*
  helper (translate+spin, no drift), but the velocity field comes from
  `RigidBody2D.point_velocity`, and "no slip" is expressed as a typed constraint
  (M4/M7), not baked into the body.

## Revisions (kinematics review 2026-09-05) — MUST

- **Rolling MUST use `RollingPoseBinding`** (M1.6), which applies the declared
  `RollingKinematicRelation` (`Δθ = -Δs/R`) via absolute pose — **never** an
  ad-hoc `.animate.shift().rotate()`. The `motion.py::roll_group` helper below is
  superseded by this binding.
- **The rolling velocity field and instantaneous centre MUST come from
  `overlays/kinematics.py`** (`RigidBodyVelocityField`, `VelocityAtPointView`),
  which use generic `kinematics/rigid_body.point_velocity` (the Rule 5
  `(r_y,-r_x)` construction) — not a body-specific `point_velocity`.
- **Rationale:** rolling is one instance of general plane motion; it MUST reuse
  the M1.6 transform/binding layer so keypoints, contact `P`, CM and arrows stay
  synchronised for free.

## Goal

Round bodies that **actually roll** (Rule 7) with a **moving contact point `P`**
(`ContactPersistence.MOVING`, `MaterialPairing.CHANGING`), plus a `Pulley` that
spins. Weight is drawn at the CM; rolling velocity fields use the exact Rule 5
`(r_y, -r_x)` construction.

## New bodies (`bodies.py`)

```python
@dataclass
class CircularBody(PhysicsAsset):
    name="disk"; mass=1.0; position=(0,0); radius=0.6
    inertia_factor=0.5           # I = factor*m*R^2  (0.5 disk, 1.0 hoop, 0.4 sphere)
    color=None; fill_opacity=0.25
    motion_state=AT_REST; omega=0.0
    show_cm=True; show_weight=True; show_spoke=True; label="m"
    def build():
        Circle(radius) at CM (+ spoke Line for visible rotation)
        keypoints: CM, top, bottom, left, right, rim_at(theta) via method
        YELLOW CM dot; auto WEIGHT ForceSpec at CM (down)
    rim_at(theta) -> CM + R*(cos,sin)                # any rim point
    contact_point() -> keypoints.get("P") or bottom  # set when placed
    # Rolling velocity field (Rule 5): perpendicular to line P->point
    point_velocity(point, v_cm) -> ( (point-P) rotated 90°, scaled )   # (r_y,-r_x)

@dataclass
class Disk(CircularBody):      inertia_factor=0.5
@dataclass
class Ring(CircularBody):      inertia_factor=1.0; fill_opacity=0.0
Hoop = Ring
@dataclass
class Sphere2D(CircularBody):  inertia_factor=0.4    # visual: circle + highlight arc
@dataclass
class Cylinder(CircularBody):
    show_cross_section=True                          # hatch to read as a solid cylinder
    build(): CircularBody.build() + cross-section hatch lines
```

## `Pulley` (in `supports.py`, a spinnable support)

```python
@dataclass
class Pulley(Support):            # STATIC axle location, but rotates() visually
    name="pulley"; center=(0,2.0); radius=0.5; rotates=True
    hangs_from="ceiling"          # semantic; actual mount added in M4
    rope_angles: dict[str,float] = {"A":30, "B":60}   # named tangent points
    build():
        Circle(radius) at center + axle Dot
        keypoints: axle=center; for name,ang in rope_angles:
                       set_keypoint(name, center + R*(cos ang, sin ang))
        # A/B are where ropes leave the wheel (M4 draws ropes to them)
    animate_spin(scene, turns=1, run_time=3, cw=True):
        Rotate(self.mobject-wheel, angle=∓2π*turns about axle)   # spin in place
```

## Rolling animation (reuse Rule 7)

```python
Cylinder/Disk.animate_roll(scene, distance, run_time=3, rightward=True):
    # wrap common.animate_rolling: translate + spin at v=ωR, no drift.
    # BUT assets must not import lesson common.py -> provide a framework copy:
    #   assets/physics/mechanics/motion.py :: roll_group(scene, group, R, dist, ...)
    # identical ValueTracker+updater pattern (rebuild-from-copy each frame).
    update self.keypoints["CM"], ["P"] each frame so FBD/overlays track the body.
```

> New tiny module `motion.py` holds the framework-level `roll_group` so the
> asset layer never depends on any lesson's `common.py` (cross-cutting rule 5).

## Cylinder-on-incline (the M3 flagship)

```python
class M3CylinderOnIncline(Scene):
    a = Assembly()
    floor = Floor(); ramp = Incline(angle_deg=30, on_floor=True)
    cyl = Cylinder(radius=0.6, show_cross_section=True, label="m")
    a.add(floor); a.add(ramp); a.add(cyl, place_on=ramp)     # seats on slope, P moving
    # FBD at the right keypoints:
    cyl.add_force(NORMAL,   at="P",  label="N", direction=ramp.normal())
    cyl.add_force(FRICTION, at="P",  label="f", direction=ramp.slope_up())
    # weight already auto at CM (down)
    play(FadeIn(a.mobject)); play(FadeIn(a.fbd()))
    a.animate_roll_down(ramp, distance=3.0)     # Rule 7 rolling down the slope
    # show rolling velocity field at 3 rim points (Rule 5) at one frozen frame
    for P in (top, three_oclock, nine_oclock): draw perp-to-contact velocity arrow
    finish_with_narration()
```

## Tests (`tests/test_assets_rolling.py`)

```
- CircularBody.rim_at(0)==right rim; rim_at(pi/2)==top.
- point_velocity is perpendicular to (point - P): dot((point-P), v) ≈ 0  (Rule 5).
- contact "P" registered after place_on(incline); classified MOVING/CHANGING.
- inertia_factor per subclass: Disk 0.5, Ring 1.0, Sphere2D 0.4.
- Pulley keypoints A/B at 30°/60° on the rim; axle at center.
- roll_group advances CM by `distance` and rotates by distance/R (no drift):
  |Δθ - distance/R| < eps  (unit test on the tracker math, no render).
- weight auto-declared at CM (down) with COLOR_WEIGHT.
```

## Render smoke
`M3CylinderOnIncline` low quality; frame extracted mid-roll: cylinder on slope,
`N` ⟂ slope and `f` up-slope at `P`, `mg` down at CM, cross-section hatch visible.

## Use cases unlocked
Disk/cylinder rolling down incline (moving `P`); hoop-vs-disk inertia compare;
sphere on track (visual); pulley spin — feeds M4 (rope over pulley), the spool /
yo-yo family (M10), and probe **A** (cylinder at table edge, with M7+M8).
