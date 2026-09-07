"""Semantic value tokens: enums for the common magic numbers.

Each token **is** its underlying value (``float``/``tuple`` mix-in enums), so it is
a drop-in wherever a raw number was written -- and a raw number is still accepted
as the *custom* escape hatch:

    Block(width=Size.LARGE)          # instead of width=1.4
    Floor(half_width=Span.WIDE)      # instead of half_width=6.0
    ContactFrame(tangent=Dir.RIGHT, normal=Dir.UP)
    self.play(FadeIn(x), run_time=Beat.QUICK)   # instead of run_time=0.3
    Block(width=1.23)                # custom is always allowed
"""

from __future__ import annotations

from enum import Enum, IntEnum

from physics_through_anim.physics.mechanics.kinds import Bearing


class Size(float, Enum):
    """A body's characteristic size (e.g. block width / body extent), in scene units."""

    TINY = 0.4
    SMALL = 0.7
    MEDIUM = 1.0
    LARGE = 1.4
    XLARGE = 2.0


class Span(float, Enum):
    """A support half-width (floor/ceiling/belt reach), in scene units."""

    NARROW = 3.0
    NORMAL = 4.5
    WIDE = 6.0
    FULL = 7.0


class Beat(float, Enum):
    """A play/animation duration (seconds) -- named tempos instead of stray floats."""

    INSTANT = 0.15
    QUICK = 0.3
    NORMAL = 0.6
    SLOW = 1.2
    HOLD = 2.0


class Dir(tuple, Enum):
    """A unit direction as an ``(x, y)`` tuple (for tangents/normals/force directions)."""

    RIGHT = (1.0, 0.0)
    LEFT = (-1.0, 0.0)
    UP = (0.0, 1.0)
    DOWN = (0.0, -1.0)
    UP_RIGHT = (0.7071067811865476, 0.7071067811865476)
    UP_LEFT = (-0.7071067811865476, 0.7071067811865476)
    DOWN_RIGHT = (0.7071067811865476, -0.7071067811865476)
    DOWN_LEFT = (-0.7071067811865476, -0.7071067811865476)


class Angle(float, Enum):
    """A slope/orientation angle in **degrees** (e.g. an incline)."""

    FLAT = 0.0
    GENTLE = 15.0
    SHALLOW = 20.0
    MODERATE = 30.0
    HALF = 45.0
    STEEP = 60.0
    UPRIGHT = 90.0


# ``Compass`` is the render-layer name for the mechanics ``Bearing`` enum: a single
# source of truth so ``Pulley.rope_angles`` can be typed against it (mechanics never
# imports render). ``Compass.SW`` == ``Bearing.SW``.
Compass = Bearing


class Coils(IntEnum):
    """A spring's visible coil count (an integer)."""

    FEW = 4
    SOME = 6
    MANY = 8
    DENSE = 12


class Mass(float, Enum):
    """A body mass in arbitrary units -- named weights instead of bare floats."""

    FEATHER = 0.2
    LIGHT = 0.5
    MEDIUM = 1.0
    HEAVY = 2.0
    MASSIVE = 5.0


class ForceScale(float, Enum):
    """How long a force/impulse arrow is drawn per unit magnitude (a display choice)."""

    SUBTLE = 0.3
    NORMAL = 0.5
    BOLD = 0.8
    DRAMATIC = 1.2


class Level(float, Enum):
    """Common scene heights (world ``y``) so ``y=`` is self-documenting.

    The reference is the scene's world frame: ``GROUND``/``FLOOR`` is the standard
    ground line (``-2``), ``CEILING`` the hang line, ``TOP`` just under the header.
    """

    GROUND = -2.0
    FLOOR = -2.0
    LOW = -1.0
    MID = 0.0
    SHELF = 1.5
    CEILING = 3.2
    TOP = 3.8

