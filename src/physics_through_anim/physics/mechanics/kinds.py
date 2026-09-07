"""Enumerations for the composable 2D mechanics asset library.

Kept as plain ``str`` enums so a future YAML config loader can round-trip them
by value (see plans/physics_asset_library.md, sign-off decision 1).
"""

from __future__ import annotations

from enum import Enum, StrEnum


class Bearing(float, Enum):
    """A rim/departure bearing in degrees (math convention: 0 = East, CCW).

    Names the common directions a rope leaves a pulley rim so a ``rope_angles``
    entry reads as intent instead of a stray number
    (``{"left": Bearing.SW, "right": Bearing.SE}``). Each member **is** its float,
    so a raw degree value is still accepted. The render layer re-exports this as
    ``Compass`` for scene code.
    """

    E = 0.0
    NE = 45.0
    N = 90.0
    NW = 135.0
    W = 180.0
    SW = 225.0
    S = 270.0
    SE = 315.0


class Keypoint(StrEnum):
    """A body's named attach point (``at=``/``toward=`` targets).

    Each member **is** its string, so it is a drop-in wherever the raw keypoint
    name was written (``at=Keypoint.TOP`` == ``at="top"``). These are the points a
    ``Block``/body registers; connectors add their own (``"from"``/``"to"``/``"mid"``).
    """

    CM = "CM"  # centre of mass
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"


class RelationKind(StrEnum):
    """The kind of a typed relationship between two (or more) named assets.

    Used by ``Assembly.relations`` so a scene's topology is a queryable list of
    ``Relation(kind, participants)`` instead of scattered implicit placements.
    """

    HANG = "hang"  # a body hung from a support (pulley <- ceiling)
    TOUCH = "touch"  # a body resting/sliding on a surface (a Contact)
    ROPE = "rope"  # a rope/cable link between two attach points
    PIN = "pin"  # a pinned/hinged joint
    AXLE = "axle"  # a fixed axle (pulley wheel to its mount)
    ROLLING = "rolling"  # rolling-without-slipping contact
    DISTANCE = "distance"  # a fixed separation between two points
    ROPE_LENGTH = "rope_length"  # inextensible rope-length constraint
    PATH = "path"  # a body confined to a path
    SLOT = "slot"  # a body confined to a slot
    FIXED_POINT = "fixed_point"  # a point pinned to the world
    CONTACT_LOCK = "contact_lock"  # a DOF dropped by an inelastic impact
    CONSTRAINT = "constraint"  # generic fallback for any other typed constraint


class BodyDynamics(StrEnum):
    """Whether an asset can move at all."""

    STATIC = "static"  # never moves: walls, ceiling, a fixed incline, a floor
    DYNAMIC = "dynamic"  # can move: a block, a cylinder, a hanging mass


class MotionState(StrEnum):
    """The *current* kinematic state of a (possibly dynamic) asset."""

    AT_REST = "at_rest"  # dynamic but currently v = 0 (block on a stopped belt)
    MOVING = "moving"  # currently translating and/or rotating (belt running)
    CONSTRAINED = "constrained"  # held by a constraint (pinned/roped), not free
    ABOUT_TO_MOVE = "about_to_move"  # on the verge of slipping (f_s = mu_s N)


class ContactRegime(StrEnum):
    """Physical contact state between a body and a supporting surface."""

    NO_CONTACT = "no_contact"
    RESTING = "resting"
    SLIDING = "sliding"
    ROLLING_NO_SLIP = "rolling_no_slip"
    SMOOTH = "smooth_contact"


class ContactPersistence(StrEnum):
    """Whether the material contact point stays put or sweeps with time."""

    FIXED = "fixed"  # the contact patch does not change (conveyor patch)
    MOVING = "moving"  # contact point P sweeps along the surface (cylinder on incline)


class Phase(StrEnum):
    """Temporal phase for an event scene (e.g. a collision)."""

    BEFORE = "before"  # pre-event state (pre-impact)
    DURING = "during"  # the event itself (impulse transfer / contact)
    AFTER = "after"  # post-event state (post-impact)


class ForceKind(StrEnum):
    """Semantic category of a force; determines its FBD colour (SKILL Rule 2)."""

    WEIGHT = "weight"  # mg
    NORMAL = "normal"  # N
    FRICTION = "friction"  # f
    APPLIED = "applied"  # F
    TENSION = "tension"  # T (rope/string)
    REACTION = "reaction"  # hinge/pin reaction
    SPRING = "spring"  # F_s (elastic restoring force)
    DAMPING = "damping"  # F_c (velocity-opposing dashpot force)
    GRAVITY = "gravity"  # F_g (central gravitation GMm/r^2; mg is the uniform-field label)
