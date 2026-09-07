"""Orbital / central-force geometry (Milestone M13).

``CentralBody`` and ``OrbitPath`` are **geometry only** (an ellipse with one focus
at ``focus`` + apsis keypoints). Kepler *timing* lives in the separate analytic
provider ``KeplerEllipseTrajectory`` (solver-free: it evaluates the analytic orbit,
it does not integrate). ``toward``/``away_from`` are declarative directions that
resolve against a live anchor.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, sin, sqrt

import numpy as np
from manim import YELLOW, Circle, Dot, VMobject

from physics_through_anim.physics.core.pose import Pose2D, Vec2
from physics_through_anim.physics.core.state import RigidKinematicState, SystemState
from physics_through_anim.physics.mechanics.base import PhysicsAsset
from physics_through_anim.physics.mechanics.kinds import BodyDynamics
from physics_through_anim.physics.mechanics.palette import COLOR_ORBIT


@dataclass
class CentralBody(PhysicsAsset):
    """A static central mass (Sun/planet) at ``position`` -- the force centre."""

    name: str = "sun"
    position: Vec2 = (0.0, 0.0)
    radius: float = 0.4
    color: str = YELLOW
    label: str = "M"
    dynamics: BodyDynamics = BodyDynamics.STATIC

    def build(self):
        from manim import VGroup

        cx, cy = self.position
        disk = Circle(radius=self.radius, color=self.color, fill_color=self.color,
                      fill_opacity=1.0).move_to([cx, cy, 0.0])
        self.set_keypoint("CM", (cx, cy))
        return VGroup(disk)


@dataclass
class OrbitPath(PhysicsAsset):
    """An ellipse with one **focus** at ``focus`` (not its centre). Geometry only."""

    name: str = "orbit"
    a: float = 3.0  # semi-major axis
    e: float = 0.0  # eccentricity
    focus: Vec2 = (0.0, 0.0)
    rotation: float = 0.0  # periapsis direction (rad from +x)
    color: str = COLOR_ORBIT
    dynamics: BodyDynamics = BodyDynamics.STATIC

    def build(self):
        from manim import VGroup

        pts = [self.point_at(2.0 * np.pi * i / 120) for i in range(121)]
        ellipse = VMobject(color=self.color, stroke_width=3)
        ellipse.set_points_smoothly(pts)
        self.set_keypoint("focus", self.focus)
        self.set_keypoint("center", self.center()[:2])
        self.set_keypoint("other_focus", self.other_focus()[:2])
        self.set_keypoint("periapsis", self.periapsis()[:2])
        self.set_keypoint("apoapsis", self.apoapsis()[:2])
        return VGroup(ellipse)

    def _focus3(self) -> np.ndarray:
        return np.array([self.focus[0], self.focus[1], 0.0])

    def _axis(self) -> np.ndarray:
        return np.array([cos(self.rotation), sin(self.rotation), 0.0])  # periapsis direction

    def radius_at(self, theta: float) -> float:
        """Focus-centred polar radius ``r = a(1-e^2)/(1+e cos theta)``."""
        return self.a * (1.0 - self.e**2) / (1.0 + self.e * cos(theta))

    def point_at(self, theta: float) -> np.ndarray:
        """Point at true anomaly ``theta`` (0 at periapsis), one focus at ``focus``."""
        r = self.radius_at(theta)
        ang = theta + self.rotation
        return self._focus3() + r * np.array([cos(ang), sin(ang), 0.0])

    def periapsis(self) -> np.ndarray:
        return self.point_at(0.0)

    def apoapsis(self) -> np.ndarray:
        return self.point_at(np.pi)

    def center(self) -> np.ndarray:
        return self._focus3() - self.a * self.e * self._axis()

    def other_focus(self) -> np.ndarray:
        return self._focus3() - 2.0 * self.a * self.e * self._axis()


def _solve_kepler(mean_anomaly: float, e: float, iters: int = 40) -> float:
    """Eccentric anomaly E from ``M = E - e sin E`` (Newton's method)."""
    ecc = mean_anomaly if e < 0.8 else np.pi
    for _ in range(iters):
        ecc -= (ecc - e * sin(ecc) - mean_anomaly) / (1.0 - e * cos(ecc))
    return ecc


@dataclass
class KeplerEllipseTrajectory:
    """Analytic equal-areas timing over an ``OrbitPath`` (solver-free provider)."""

    orbit: OrbitPath = None
    period: float = 8.0
    entity: str = "m"
    t0: float = 0.0

    def state_at(self, t: float) -> SystemState:
        frac = ((t - self.t0) / self.period) % 1.0
        mean = 2.0 * np.pi * frac
        ecc = _solve_kepler(mean, self.orbit.e)
        theta = 2.0 * atan2(sqrt(1.0 + self.orbit.e) * sin(ecc / 2.0),
                            sqrt(1.0 - self.orbit.e) * cos(ecc / 2.0))
        pos = self.orbit.point_at(theta)
        r = self.orbit.a * (1.0 - self.orbit.e * cos(ecc))
        body = RigidKinematicState(pose=Pose2D(position=(pos[0], pos[1])))
        return SystemState(entities={self.entity: body},
                           observables={"r": float(r), "theta": float(theta)})


def toward(target: Vec2):
    """Declarative direction ``unit(target - anchor)``; call with the anchor point."""
    t = np.asarray(target, dtype=float)[:2]

    def resolve(anchor) -> np.ndarray:
        a = np.asarray(anchor, dtype=float)[:2]
        d = t - a
        n = float(np.linalg.norm(d))
        return d / n if n > 1e-9 else np.array([0.0, 0.0])

    return resolve


def away_from(target: Vec2):
    """Declarative direction ``unit(anchor - target)``; call with the anchor point."""
    t = np.asarray(target, dtype=float)[:2]

    def resolve(anchor) -> np.ndarray:
        a = np.asarray(anchor, dtype=float)[:2]
        d = a - t
        n = float(np.linalg.norm(d))
        return d / n if n > 1e-9 else np.array([0.0, 0.0])

    return resolve


def focus_marker(orbit: OrbitPath, *, color: str = YELLOW, radius: float = 0.06) -> Dot:
    """A small dot at the occupied focus of ``orbit``."""
    return Dot(orbit._focus3(), color=color, radius=radius)

