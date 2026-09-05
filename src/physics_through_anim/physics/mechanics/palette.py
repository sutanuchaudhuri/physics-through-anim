"""Canonical colours for the mechanics asset library.

These match the per-lesson ``common.py`` palette so assets look identical to
hand-built scenes (SKILL Rule 2), and add ``COLOR_TENSION`` for rope/string
tension (sign-off decision 3). ``FORCE_COLORS`` maps each ``ForceKind`` to its
arrow colour.
"""

from __future__ import annotations

from manim import BLUE, GREEN, ORANGE, PURPLE, YELLOW

from physics_through_anim.physics.mechanics.kinds import ForceKind

# Force (FBD) family -- one colour per force type.
COLOR_APPLIED = YELLOW
COLOR_FRICTION = ORANGE
COLOR_NORMAL = GREEN
COLOR_WEIGHT = PURPLE
COLOR_TENSION = "#0CA678"  # teal-green, distinct from the warm force hues
COLOR_REACTION = "#868E96"  # neutral grey for hinge/pin reactions

# Kinematic family -- separate palette so a force and a velocity are never
# visually confused (SKILL Rule 2).
COLOR_VELOCITY = BLUE
COLOR_ANGULAR = "#20C997"
COLOR_ACCEL = "#FF2D95"

FORCE_COLORS: dict[ForceKind, object] = {
    ForceKind.WEIGHT: COLOR_WEIGHT,
    ForceKind.NORMAL: COLOR_NORMAL,
    ForceKind.FRICTION: COLOR_FRICTION,
    ForceKind.APPLIED: COLOR_APPLIED,
    ForceKind.TENSION: COLOR_TENSION,
    ForceKind.REACTION: COLOR_REACTION,
}
