# M5 — SKILL Rule 19 + Docs + First Gallery

Status: **DRAFT FOR REVIEW**
Depends on: M1–M4. Files: `.github/skills/physics-animation-standards/SKILL.md`
(add Rule 19, update Rule 11 + frontmatter), a gallery scene, `Rod` body if not
yet present, `tests/test_assets_catalog.py`.

## Revisions (architecture review 2026-09-05)

- **`Rod` is a `RigidBody2D`** (M1.5), inheriting generic `point_at`/
  `point_velocity`; the standalone `point_at` below is kept only as sugar.
- **Rule 19 wording updated** to the revised model: build from generic assets +
  **typed relations** (`Contact`, typed `Constraint`s), and get the FBD from the
  **renderer** (`MechanicsRenderer`), not by placing `Arrow`s. Overlays are
  requested as **specs** (review 29), not pre-built `VGroup`s.
- **Gallery reflects the facade split** (review 28): scenes talk to `Assembly`
  (the facade); the gallery exercises `MechanicsModel`/`MechanicsRenderer`/
  `Timeline` indirectly.

## Goal

Make the library *discoverable and reusable during scaffolding* by codifying it
as a SKILL rule, and ship a visual **gallery** that renders every catalogue
asset for QA (the "one small render per family" idea from the vision, §27).

## SKILL Rule 19 (new rule — pseudocode of the prose)

```
## 19. Build scenes from the physics asset library when asked
Trigger: user asks to "use/reuse the asset library", "build from assets",
"assemble this from the mechanics assets".
- Construct from physics_through_anim.assets.physics.mechanics (Block, Disk,
  Cylinder, Rod, Incline, Conveyor, Pulley, Rope, Hinge, Assembly, ...).
- Supply only the granular properties the problem states; rely on defaults.
- Get the FBD from assembly.fbd() — it already obeys Rules 2/5/8/9.
- Contacts via Contact asset; declare forces at named keypoints, never bare Arrow.
- Do NOT force this on lessons that did not ask.
Also: update Rule 11 checklist ("if asset-based, base scenes on the library")
and the frontmatter description to mention the asset library.
```

## `Rod` body (fills the last M1-era gap, needed by gallery + M4 hinge)

```python
@dataclass
class Rod(PhysicsAsset):
    name="rod"; mass=1.0; length=2.0; angle_deg=0.0; center=(0,0)
    massless=False; thickness=5; label="m"
    def build():
        dir=(cos,sin); a=center-L/2*dir; b=center+L/2*dir
        Line(a,b, stroke_width=thickness)
        keypoints: A=a, B=b, CM=center
        CM dot; if not massless: auto WEIGHT at CM (down)
    point_at(s in [0,1]) -> a + s*(b-a)
```

## Gallery scene (`assets/physics/mechanics/gallery.py` or a test scene)

```python
class AssetGallery(Scene):
    # one representative render per family, laid out with Rule 16 `together`
    segments = [
      block-on-floor (FBD), block-on-incline, cylinder-on-incline (roll),
      conveyor (moving), pulley+two ropes, hinged rod,
    ]
    play_subscenes(together, positions=grid)   # visual QA of the whole catalogue
```

## Tests (`tests/test_assets_catalog.py`)

```
- Every catalogue example builds without error (Block, Disk, Ring, Sphere2D,
  Cylinder, Rod, Floor, Wall, Ceiling, Incline, Conveyor, Pulley, Rope, Hinge).
- Each asset exposes its documented keypoints.
- Rod: A/B/CM registered; massless=True omits weight; point_at endpoints.
- Assembly gallery builds a VGroup with the expected member count.
```

## Deliverables checklist
- [ ] Rule 19 added; Rule 11 checklist line added; frontmatter updated.
- [ ] `Rod` shipped + tested.
- [ ] Gallery renders at low quality; frame eyeballed; artifacts cleaned.
- [ ] `__init__.py` exports the full M1–M4 catalogue + `Rod`.

## Use cases unlocked
The library is now a first-class, documented tool an AI/human reaches for during
scaffolding — the pivot point after which M6+ add *behaviour* (state, events,
overlays) on top of a stable object catalogue.
