# Render — Masks, Laminae & the Point-Mass Skin

Status: **DESIGN + SHIPPED** (`physics/render/mask.py`, `tests/test_render_mask.py`)
Layer: `render` (imports Manim; **nothing depends on render**).

## The idea in one line

> **A body's picture is a cosmetic *mask*; the physics is a *point mass* at its
> centre of mass.** The renderer may accept any object / image / matrix as the
> skin, but the framework reasons only about the CM and the physically meaningful
> vectors and lever arms.

A boat drifting, a human running, a stone thrown off a cliff — each is, to the
physics, a **point mass at a CM** with a velocity vector, maybe a force or two,
and (if it matters) a lever arm. The hull, the runner, the pebble are just
*skins*: they make the scene legible, but the solver never reads their shape.

## Two hard separations (MUST)

### 1. Geometry is cosmetic; the CM is physical

The mask is an arbitrary visual — a Manim `Mobject`, an image/SVG on disk, or a
raw **matrix** (a lamina rendered as an image). The physics never inspects it. A
mask can even be **fully transparent** (`opacity=0`): the body is *still* a point
mass; only the picture is hidden. This is why a "stone" and a "boat" share one
model — both are `Mask` skins over the same point-mass CM.

```
input:  image | sprite | SVG | Mobject | matrix   (the SKIN)
model:  CM (a point) + vectors + lever arms        (the PHYSICS)
render: place the skin so its CM lands on the CM pose; draw the vectors
```

### 2. Mask rotation is cosmetic; vector/lever-arm rotation is physical

Spinning a stone's sprite as it flies is **decoration**. What actually determines
the dynamics is the **lever arm** `r` (CM → point of application) and the **force
vector** `F` rotating — torque is `τ = r × F`. So:

- The **mask** rotates only for looks (`cosmetic_rotation=True`), or stays upright
  (`cosmetic_rotation=False`) while the meaningful rotation is shown by the
  vectors/lever arms drawn by the kinematics/overlay layers (M1.6 / M9).
- A wrench turning a bolt might keep a steady picture while its **lever arm and
  applied force** sweep — because *that* is the physics; the sprite spin is not.

> Lever arms and `τ = r × F` are computed in `physics/kinematics` (the point
> `r = P − CM`, `point_velocity`, `Transform2D`). The mask never owns them; it
> only follows the CM `Pose2D`.

## API (`physics/render/mask.py`)

```python
@dataclass
class Mask:
    source: Any                      # Mobject | image path | numpy matrix
    cm_local: Vec2 = (0.0, 0.0)      # CM offset from the skin's centre (mask-local)
    scale: float = 1.0
    opacity: float = 1.0             # 0.0 => transparent (point mass, hidden skin)
    cosmetic_rotation: bool = True   # False => picture stays upright; vectors carry rotation
    mobject: Mobject                 # the cosmetic Manim mobject (built in __post_init__)

    def place(self, pose: Pose2D) -> Mobject   # seat the CM at pose.position (drift-free)

    @classmethod
    def from_matrix(cls, matrix, **kw) -> Mask  # a lamina/array as an image skin
    @classmethod
    def transparent(cls, source, **kw) -> Mask  # opacity 0: hidden skin, real point mass
```

`place` is **absolute** (drift-free across repeated updater calls, like every
pose in this framework): the CM — not the skin centre — is the anchor, so the
point-mass invariant holds every frame regardless of `cm_local`.

## Worked examples

```python
# A stone as a projectile: cosmetic sprite, physics is a point mass at the CM.
stone = Mask(source="assets/stone.png", scale=0.4)          # or from_matrix(pixels)
for t in trajectory.samples():                              # states supplied (M6)
    stone.place(state_at(t).pose)                           # CM follows the arc
    # velocity/acceleration arrows drawn from the CM by overlays (M9) -- the physics

# A running human as a point mass: the animation is decoration.
runner = Mask(source=runner_svg, cosmetic_rotation=False)   # upright while moving
runner.place(Pose2D(position=cm_xy))                        # only the CM matters

# A spinning stone: skin spins for looks; torque is r x F, drawn separately.
stone = Mask(source=pebble, cosmetic_rotation=True)
stone.place(Pose2D(position=cm_xy, angle=theta))            # cosmetic spin
# lever arm r = P - CM and force F are the physics (kinematics/overlays)

# A transparent mask: keep the picture out, show only the point-mass physics.
ghost = Mask.transparent(source=boat_svg)
ghost.place(Pose2D(position=cm_xy))                         # CM + vectors only
```

## Why this belongs in `render`

- The mask is *presentation*: it turns a CM pose + a chosen skin into pixels.
- It reads a `Pose2D` (core) and produces a `Mobject` (Manim); it declares no
  force, contact or constraint, and **nothing depends on `render`** (layering
  rule in `plans/ARCHITECTURE.md`).
- Because the skin is decoupled from the model, the *same* lesson works with a
  circle, a photo, an SVG, or a matrix — swap the mask, keep the physics.

## Tests (`tests/test_render_mask.py`)

- `place` seats the CM at `pose.position`; repeated calls are drift-free.
- `cosmetic_rotation=False` keeps the skin upright (angle stays 0).
- `cm_local` offset anchors the offset point (CM), not the skin centre.
- `transparent` masks keep `opacity=0` yet still follow the CM (point mass).
- `from_matrix` builds an image skin from a raw array (a lamina).

## Unlocks / used by

Projectiles and free bodies where the picture is incidental (stones, boats,
runners, crates, planets-as-points); any scene that wants a photo/sprite skin
over the exact same point-mass physics; and the separation that lets M9 overlays
own the *meaningful* vector/lever-arm rotation while the skin stays cosmetic.
