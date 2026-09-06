"""Orbital / central-force geometry (Milestone M13). Scaffold.

``OrbitPath`` is geometry only; Kepler timing lives in a motion/analytic provider.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from physics_through_anim.physics.core.pose import Vec2


@dataclass
class CentralBody:
    position: Vec2 = (0.0, 0.0)
    radius: float = 0.4
    label: str = "M"


@dataclass
class OrbitPath:
    a: float = 3.0  # semi-major axis
    e: float = 0.0  # eccentricity
    focus: Vec2 = (0.0, 0.0)
    rotation: float = 0.0

    def point_at(self, theta: float) -> np.ndarray:
        """True-anomaly point on the ellipse (one focus at ``focus``)."""
        raise NotImplementedError("M13 OrbitPath.point_at")

    def periapsis(self) -> np.ndarray:
        raise NotImplementedError("M13 OrbitPath.periapsis")

    def apoapsis(self) -> np.ndarray:
        raise NotImplementedError("M13 OrbitPath.apoapsis")


def toward(target: Vec2):
    """Semantic direction: unit(target - anchor), resolved against SystemState."""
    raise NotImplementedError("M13 orbital.toward")


def away_from(target: Vec2):
    raise NotImplementedError("M13 orbital.away_from")
