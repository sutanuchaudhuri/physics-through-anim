"""Rod body (Milestone M5). Scaffold — subclasses RigidBody2D at implementation."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from physics_through_anim.physics.core.pose import Vec2


@dataclass
class Rod:
    mass: float = 1.0
    length: float = 2.0
    angle_deg: float = 0.0
    center: Vec2 = (0.0, 0.0)
    massless: bool = False
    thickness: float = 5.0
    label: str = "m"

    def point_at(self, s: float) -> np.ndarray:
        """Point at parameter ``s`` in [0, 1] from A to B."""
        raise NotImplementedError("M5 Rod.point_at")
