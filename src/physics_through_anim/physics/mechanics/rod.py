"""Rod body (Milestone M5). Scaffold — subclasses RigidBody2D at implementation."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin

import numpy as np
from manim import GREEN, YELLOW, Dot, Line, VGroup

from physics_through_anim.physics.mechanics.base import PhysicsAsset
from physics_through_anim.physics.mechanics.kinds import BodyDynamics, ForceKind

Vec2 = tuple[float, float]


@dataclass
class Rod(PhysicsAsset):
    """A straight rod with keypoints ``A`` (start), ``B`` (end) and ``CM``."""

    name: str = "rod"
    mass: float = 1.0
    length: float = 2.0
    angle_deg: float = 0.0
    center: Vec2 = (0.0, 0.0)
    massless: bool = False
    thickness: float = 5.0
    color: str = GREEN
    show_cm: bool = True
    label: str | None = "m"
    dynamics: BodyDynamics = BodyDynamics.DYNAMIC

    def _endpoints(self) -> tuple[np.ndarray, np.ndarray]:
        theta = radians(self.angle_deg)
        d = np.array([cos(theta), sin(theta), 0.0])
        c = np.array([self.center[0], self.center[1], 0.0])
        return c - 0.5 * self.length * d, c + 0.5 * self.length * d

    def build(self) -> VGroup:
        a, b = self._endpoints()
        group = VGroup(Line(a, b, color=self.color, stroke_width=self.thickness))
        self.set_keypoint("A", a[:2])
        self.set_keypoint("B", b[:2])
        self.set_keypoint("CM", self.center)
        self.set_keypoint("mid", self.center)
        if self.show_cm and not self.massless:
            group.add(Dot([self.center[0], self.center[1], 0.0], color=YELLOW, radius=0.06))
        if not self.massless:
            self.add_force(ForceKind.WEIGHT, at="CM", label="mg", direction="down")
        return group

    def point_at(self, s: float) -> np.ndarray:
        """Point at parameter ``s`` in [0, 1] from A to B."""
        a, b = self._endpoints()
        return a + s * (b - a)

    @property
    def inertia_cm(self) -> float:
        """Moment of inertia about the CM: a uniform thin rod is ``m L^2 / 12``."""
        return 0.0 if self.massless else self.mass * self.length**2 / 12.0

    def mass_properties(self):
        """This rod's :class:`MassProperties` (mass + ``I_cm``) for impulse tools."""
        from physics_through_anim.physics.mechanics.massprops import MassProperties

        return MassProperties(mass=self.mass, inertia_cm=self.inertia_cm)
