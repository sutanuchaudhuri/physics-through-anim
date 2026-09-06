"""Round rolling/rotation bodies (Milestone M3). Scaffold.

At implementation these subclass ``RigidBody2D``; here they are geometry stubs so
the inertia-factor + rim-geometry acceptance criteria can be tested first.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from physics_through_anim.physics.core.pose import Vec2


@dataclass
class CircularBody:
    mass: float = 1.0
    position: Vec2 = (0.0, 0.0)
    radius: float = 0.6
    inertia_factor: float = 0.5  # I = factor * m * R^2
    omega: float = 0.0
    label: str = "m"

    def rim_at(self, theta: float) -> np.ndarray:
        """Rim point at angle ``theta`` -> ``CM + R (cos, sin)``."""
        raise NotImplementedError("M3 CircularBody.rim_at")

    def point_velocity(self, point: np.ndarray, v_cm: float) -> np.ndarray:
        """Rolling velocity field (perp to line point->contact, Rule 5)."""
        raise NotImplementedError("M3 CircularBody.point_velocity")


@dataclass
class Disk(CircularBody):
    inertia_factor: float = 0.5


@dataclass
class Ring(CircularBody):
    inertia_factor: float = 1.0


Hoop = Ring


@dataclass
class Sphere2D(CircularBody):
    inertia_factor: float = 0.4


@dataclass
class Cylinder(CircularBody):
    show_cross_section: bool = True


@dataclass
class Pulley:
    center: Vec2 = (0.0, 2.0)
    radius: float = 0.5
    rope_angles: dict[str, float] = field(default_factory=lambda: {"A": 30.0, "B": 60.0})

    def rim_point(self, name: str) -> np.ndarray:
        raise NotImplementedError("M3 Pulley.rim_point")
