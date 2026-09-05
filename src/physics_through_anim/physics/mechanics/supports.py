"""Static supporting surfaces for the mechanics asset library.

Milestone 1 ships ``Floor``: a horizontal ground line with hatch ticks, at the
Rule 8 ground level by default. Walls, ceilings, inclines, and conveyors follow
in later milestones.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from manim import GRAY, Line, VGroup

from physics_through_anim.physics.mechanics.base import PhysicsAsset
from physics_through_anim.physics.mechanics.kinds import BodyDynamics

GROUND_Y = -2.0  # matches the SKILL Rule 8 layout contract


@dataclass
class Support(PhysicsAsset):
    """A static supporting surface (never moves by default)."""

    name: str = "support"
    dynamics: BodyDynamics = BodyDynamics.STATIC


@dataclass
class Floor(Support):
    """A horizontal ground surface with engineering hatch ticks."""

    name: str = "floor"
    y: float = GROUND_Y
    half_width: float = 5.5
    hatch: bool = True
    color: str = GRAY

    def build(self) -> VGroup:
        line = Line([-self.half_width, self.y, 0], [self.half_width, self.y, 0],
                    color=self.color, stroke_width=6)
        group = VGroup(line)
        if self.hatch:
            ticks = VGroup()
            for x in np.linspace(-self.half_width, self.half_width, int(self.half_width * 3) + 1):
                ticks.add(Line([x, self.y, 0], [x - 0.14, self.y - 0.14, 0],
                               color=self.color, stroke_width=2))
            group.add(ticks)
        self.set_keypoint("surface", [0.0, self.y])
        self.set_keypoint("left", [-self.half_width, self.y])
        self.set_keypoint("right", [self.half_width, self.y])
        return group

    def contact_under(self, x: float) -> np.ndarray:
        """World contact point directly below/above screen x on this floor."""
        return np.array([x, self.y, 0.0])
