"""Enumerations for the composable 2D mechanics asset library.

Kept as plain ``str`` enums so a future YAML config loader can round-trip them
by value (see plans/physics_asset_library.md, sign-off decision 1).
"""

from __future__ import annotations

from enum import StrEnum


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
