"""Static supporting surfaces for the mechanics asset library.

The one primitive is ``Wall`` -- an oriented static boundary at any angle. A
floor is a horizontal wall (normal up), a ceiling a horizontal wall (normal
down), a side-wall a vertical one, a ramp a wall at angle theta. **A wall never
has a free-body diagram**: it is ``STATIC``, declares no force, and only owns a
surface + supplies a reaction to the touching body's FBD. ``Floor`` (shipped in
M1) is the horizontal-up preset; ``Ceiling``/``Incline``/``Conveyor`` live in
``environment.py``.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin

import numpy as np
from manim import GRAY, Line, VGroup

from physics_through_anim.physics.core.pose import Vec2
from physics_through_anim.physics.mechanics.base import PhysicsAsset
from physics_through_anim.physics.mechanics.kinds import BodyDynamics
from physics_through_anim.physics.mechanics.surfaces import LineSurface

GROUND_Y = -2.0  # matches the SKILL Rule 8 layout contract


@dataclass
class Support(PhysicsAsset):
    """A static supporting surface (never moves by default)."""

    name: str = "support"
    dynamics: BodyDynamics = BodyDynamics.STATIC


@dataclass
class Wall(Support):
    """An oriented static boundary at ``angle_deg`` -- the one wall primitive.

    ``angle_deg`` 0 is horizontal, 90 vertical, anything else a ramp. It owns a
    ``LineSurface`` and exposes ``tangent``/``normal``/``contact_at``; it carries
    no force and its ``fbd()`` is always empty.
    """

    name: str = "wall"
    angle_deg: float = 90.0
    center: Vec2 = (0.0, 0.0)
    length: float = 5.6
    facing: str = "auto"  # outward-normal side: up | down | left | right | auto
    hatch: bool = True
    color: str = GRAY

    @property
    def _theta(self) -> float:
        return radians(self.angle_deg)

    def tangent(self) -> np.ndarray:
        return np.array([cos(self._theta), sin(self._theta), 0.0])

    def normal(self) -> np.ndarray:
        """Outward unit normal (tangent rotated +90 deg), flipped to ``facing``."""
        t = self.tangent()
        n = np.array([-t[1], t[0], 0.0])
        pref = {
            "up": np.array([0.0, 1.0, 0.0]),
            "down": np.array([0.0, -1.0, 0.0]),
            "left": np.array([-1.0, 0.0, 0.0]),
            "right": np.array([1.0, 0.0, 0.0]),
        }.get(self.facing)
        if pref is not None and float(np.dot(n, pref)) < 0:
            n = -n
        return n

    def _endpoints(self) -> tuple[np.ndarray, np.ndarray]:
        c = np.array([self.center[0], self.center[1], 0.0])
        half = 0.5 * self.length * self.tangent()
        return c - half, c + half

    def build(self) -> VGroup:
        start, end = self._endpoints()
        group = VGroup(Line(start, end, color=self.color, stroke_width=6))
        if self.hatch:
            tick = -0.14 * (self.tangent() + self.normal())
            ticks = VGroup()
            for s in np.linspace(0.0, 1.0, max(int(self.length * 3), 2) + 1):
                p = start + s * (end - start)
                ticks.add(Line(p, p + tick, color=self.color, stroke_width=2))
            group.add(ticks)
        self.set_keypoint("surface", self.center)
        self.set_keypoint("start", start[:2])
        self.set_keypoint("end", end[:2])
        return group

    def surface(self, name: str = "face") -> LineSurface:
        start, end = self._endpoints()
        return LineSurface(a=(start[0], start[1]), b=(end[0], end[1]))

    def contact_at(self, s: float) -> np.ndarray:
        """World point at fraction ``s`` in [0, 1] along the surface."""
        start, end = self._endpoints()
        return start + s * (end - start)


@dataclass
class Floor(Wall):
    """A horizontal ground surface (the ``angle_deg=0``, normal-up wall preset)."""

    name: str = "floor"
    angle_deg: float = 0.0
    facing: str = "up"
    y: float = GROUND_Y
    half_width: float = 5.5
    hatch: bool = True
    color: str = GRAY

    def __post_init__(self) -> None:
        self.center = (0.0, self.y)
        self.length = 2.0 * self.half_width
        super().__post_init__()

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
        self.set_keypoint("start", [-self.half_width, self.y])
        self.set_keypoint("end", [self.half_width, self.y])
        return group

    def contact_under(self, x: float) -> np.ndarray:
        """World contact point directly below/above screen x on this floor."""
        return np.array([x, self.y, 0.0])

