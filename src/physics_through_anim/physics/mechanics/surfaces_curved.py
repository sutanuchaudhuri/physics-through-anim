"""Curved surfaces / edges / tracks (Milestone M8) -- extends the M2 Surface protocol.

A ``ParametricSurface`` gives any parametric curve point/tangent/normal/curvature
for free (finite differences); ``CircularTrack``/``ConvexSurface``/``ConcaveSurface``/
``Rail`` are pure geometry (owned by an entity, static or moving). ``Table``,
``SharpEdge`` and ``Peg`` are drawable environment supports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import cos, sin

import numpy as np
from manim import GRAY, YELLOW, Dot, Line, VGroup

from physics_through_anim.physics.core.pose import Vec2
from physics_through_anim.physics.mechanics.constraints import SlotConstraint
from physics_through_anim.physics.mechanics.supports import Support
from physics_through_anim.physics.mechanics.surfaces import LineSurface


@dataclass
class ParametricSurface:
    """Any parametric curve ``s in [0,1] -> world point`` with derived frames."""

    def _curve(self, s: float) -> np.ndarray:
        raise NotImplementedError("ParametricSurface subclasses define _curve")

    def point_at(self, s: float) -> np.ndarray:
        return self._curve(float(np.clip(s, 0.0, 1.0)))

    def tangent_at(self, s: float, *, h: float = 1e-4) -> np.ndarray:
        s = float(np.clip(s, 0.0, 1.0))
        p0 = self._curve(max(0.0, s - h))
        p1 = self._curve(min(1.0, s + h))
        t = p1 - p0
        n = float(np.linalg.norm(t))
        return t / n if n else np.array([1.0, 0.0, 0.0])

    def normal_at(self, s: float) -> np.ndarray:
        """Outward normal: tangent rotated +90 degrees."""
        t = self.tangent_at(s)
        return np.array([-t[1], t[0], 0.0])

    def curvature_at(self, s: float, *, h: float = 1e-3) -> float:
        s = float(np.clip(s, h, 1.0 - h))
        pm, p0, pp = self._curve(s - h), self._curve(s), self._curve(s + h)
        r1 = (pp - pm) / (2.0 * h)
        r2 = (pp - 2.0 * p0 + pm) / (h * h)
        speed = float(np.linalg.norm(r1))
        if speed < 1e-9:
            return 0.0
        cross = r1[0] * r2[1] - r1[1] * r2[0]
        return abs(cross) / speed**3

    def length(self) -> float:
        pts = [self._curve(s) for s in np.linspace(0.0, 1.0, 64)]
        return float(sum(np.linalg.norm(pts[i + 1] - pts[i]) for i in range(len(pts) - 1)))


@dataclass
class CircularTrack(ParametricSurface):
    """An arc of a circle; ``inner`` flips the normal toward the centre."""

    center: Vec2 = (0.0, 0.0)
    radius: float = 2.0
    arc: tuple[float, float] = (0.0, 2.0 * np.pi)
    inner: bool = False

    def _angle(self, s: float) -> float:
        return self.arc[0] + float(np.clip(s, 0.0, 1.0)) * (self.arc[1] - self.arc[0])

    def _curve(self, s: float) -> np.ndarray:
        a = self._angle(s)
        return np.array([self.center[0] + self.radius * cos(a),
                         self.center[1] + self.radius * sin(a), 0.0])

    def normal_at(self, s: float) -> np.ndarray:
        a = self._angle(s)
        radial = np.array([cos(a), sin(a), 0.0])  # outward from the centre
        return -radial if self.inner else radial

    def curvature_at(self, s: float, *, h: float = 1e-3) -> float:
        return 1.0 / self.radius if self.radius else 0.0

    def length(self) -> float:
        return self.radius * abs(self.arc[1] - self.arc[0])


@dataclass
class ConvexSurface(CircularTrack):
    """A hill: a body rides the *outside*; the normal points away from the centre."""

    inner: bool = False


@dataclass
class ConcaveSurface(CircularTrack):
    """A bowl: a body rides the *inside*; the normal points toward the centre."""

    inner: bool = True


@dataclass
class RoundedEdge(CircularTrack):
    """A small-radius arc: smooth normal evolution around a corner."""

    radius: float = 0.2


@dataclass
class Rail(ParametricSurface):
    """A straight slider guide from ``a`` to ``b``."""

    a: Vec2 = (0.0, 0.0)
    b: Vec2 = (1.0, 0.0)

    def _curve(self, s: float) -> np.ndarray:
        s = float(np.clip(s, 0.0, 1.0))
        return np.array([self.a[0] + s * (self.b[0] - self.a[0]),
                         self.a[1] + s * (self.b[1] - self.a[1]), 0.0])

    def curvature_at(self, s: float, *, h: float = 1e-3) -> float:
        return 0.0


@dataclass
class SharpEdge(Support):
    """A corner a body pivots about / separates at (contact POINT, fixed geometry)."""

    name: str = "edge"
    at: Vec2 = (0.0, 0.0)
    color: str = YELLOW

    def build(self) -> VGroup:
        p = [self.at[0], self.at[1], 0.0]
        self.set_keypoint("E", self.at)
        return VGroup(Dot(p, color=self.color, radius=0.06))

    def point(self) -> np.ndarray:
        return np.array([self.at[0], self.at[1], 0.0])


@dataclass
class Table(Support):
    """A table top on two legs; owns a top ``Surface`` and a ``SharpEdge``."""

    name: str = "table"
    top_y: float = 0.5
    left: float = -3.0
    right: float = 1.0
    leg: bool = True
    leg_bottom: float = -2.4
    color: str = GRAY

    def build(self) -> VGroup:
        group = VGroup(
            Line([self.left, self.top_y, 0], [self.right, self.top_y, 0],
                 color=self.color, stroke_width=6)
        )
        if self.leg:
            for x in (self.left + 0.4, self.right - 0.4):
                group.add(Line([x, self.top_y, 0], [x, self.leg_bottom, 0],
                               color=self.color, stroke_width=5))
        self.set_keypoint("top_left", [self.left, self.top_y])
        self.set_keypoint("top_right", [self.right, self.top_y])
        self.set_keypoint("edge", [self.right, self.top_y])
        self.set_keypoint("surface", [(self.left + self.right) / 2.0, self.top_y])
        return group

    def top_surface(self) -> LineSurface:
        return LineSurface(a=(self.left, self.top_y), b=(self.right, self.top_y))

    def edge(self) -> SharpEdge:
        return SharpEdge(at=(self.right, self.top_y))


@dataclass
class Peg(Support):
    """A small round peg a string can catch on (M4 rope + M7 event)."""

    name: str = "peg"
    at: Vec2 = (0.0, 0.0)
    radius: float = 0.06
    color: str = GRAY

    def build(self) -> VGroup:
        from manim import Circle

        self.set_keypoint("at", self.at)
        return VGroup(
            Circle(radius=self.radius, color=self.color, fill_color=self.color,
                   fill_opacity=1.0).move_to([self.at[0], self.at[1], 0.0])
        )


@dataclass
class Slot:
    """A bead/rod slot: two parallel guide lines; yields a SLOT constraint."""

    from_point: Vec2 = (0.0, 0.0)
    to_point: Vec2 = (1.0, 0.0)
    gap: float = 0.2
    participants: tuple[str, ...] = field(default_factory=tuple)

    def guide_constraint(self) -> SlotConstraint:
        return SlotConstraint(participants=self.participants, slot="slot")


def separation_imminent(n_value: float, *, tol: float = 0.0) -> bool:
    """A contact separates when the normal force reaches zero (``N <= tol``)."""
    return n_value <= tol

