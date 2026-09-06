"""Static environment supports (Milestone M2). Scaffold — merges into supports.py.

Wall / Ceiling / Incline / Conveyor. A Conveyor is a Floor whose surface moves.
"""

from __future__ import annotations

from dataclasses import dataclass

from physics_through_anim.physics.core.pose import Vec2

GROUND_Y = -2.0


@dataclass
class Wall:
    x: float = -5.0
    half_height: float = 2.8
    side: str = "right"

    def contact_at(self, y: float):
        raise NotImplementedError("M2 Wall.contact_at")


@dataclass
class Ceiling:
    y: float = 3.0
    half_width: float = 5.5

    def anchor(self, x: float):
        raise NotImplementedError("M2 Ceiling.anchor")


@dataclass
class Incline:
    angle_deg: float = 30.0
    length: float = 5.0
    mu: float = 0.0
    base: Vec2 = (-2.0, GROUND_Y)

    def surface_at(self, s: float):
        raise NotImplementedError("M2 Incline.surface_at")

    def normal(self):
        raise NotImplementedError("M2 Incline.normal")


@dataclass
class Conveyor:
    belt_speed: float = 0.0
    direction: int = 1
    mu: float = 0.4

    @property
    def motion_state(self) -> str:
        """AT_REST when the belt is frozen, else MOVING."""
        raise NotImplementedError("M2 Conveyor.motion_state")
