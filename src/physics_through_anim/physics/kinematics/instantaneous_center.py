"""Instantaneous centre of rotation (Milestone M1.6).

For a body in plane motion the velocity of any point ``P`` is a pure rotation
about the instantaneous centre ``I``: ``v_P = omega x (P - I)`` -- perpendicular
to ``IP`` with magnitude ``omega * |IP|`` (SKILL Rule 5).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from physics_through_anim.physics.core.pose import Vec2


@dataclass(frozen=True)
class InstantaneousCenterState:
    """The instantaneous centre ``point`` and the body's angular rate ``omega``."""

    point: Vec2 = (0.0, 0.0)
    omega: float = 0.0
    body: str = ""


def velocity_at(icr: InstantaneousCenterState, p: Vec2) -> np.ndarray:
    """``omega x (P - I)`` -- perpendicular to ``IP``, ``|v| = omega * |IP|``."""
    r = np.array([p[0] - icr.point[0], p[1] - icr.point[1], 0.0])
    return icr.omega * np.array([-r[1], r[0], 0.0])
