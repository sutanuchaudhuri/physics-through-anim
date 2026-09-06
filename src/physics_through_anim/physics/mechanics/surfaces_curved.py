"""Curved surfaces / edges / tracks (Milestone M8). Scaffold — extends M2 surfaces.

A ``ParametricSurface`` gives any curve point/tangent/normal/curvature for free.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from physics_through_anim.physics.core.pose import Vec2


@dataclass
class ParametricSurface:
    def point_at(self, s: float) -> np.ndarray:
        raise NotImplementedError("M8 ParametricSurface.point_at")

    def normal_at(self, s: float) -> np.ndarray:
        raise NotImplementedError("M8 ParametricSurface.normal_at")

    def curvature_at(self, s: float) -> float:
        raise NotImplementedError("M8 ParametricSurface.curvature_at")


@dataclass
class CircularTrack(ParametricSurface):
    center: Vec2 = (0.0, 0.0)
    radius: float = 2.0
    arc: tuple[float, float] = (0.0, 6.283185307179586)
    inner: bool = False


@dataclass
class ConvexSurface(ParametricSurface):
    center: Vec2 = (0.0, 0.0)
    radius: float = 2.0


@dataclass
class ConcaveSurface(ParametricSurface):
    center: Vec2 = (0.0, 0.0)
    radius: float = 2.0


@dataclass
class RoundedEdge(CircularTrack):
    """A small-radius arc: smooth normal evolution."""


@dataclass
class Table:
    top_y: float = 0.5
    left: float = -3.0
    right: float = 1.0

    def edge(self):
        """Return the SharpEdge at (right, top_y)."""
        raise NotImplementedError("M8 Table.edge")


@dataclass
class SharpEdge:
    at: Vec2 = (0.0, 0.0)

    def point(self) -> np.ndarray:
        raise NotImplementedError("M8 SharpEdge.point")


@dataclass
class Peg:
    at: Vec2 = (0.0, 0.0)
    radius: float = 0.06


@dataclass
class Rail(ParametricSurface):
    a: Vec2 = (0.0, 0.0)
    b: Vec2 = (1.0, 0.0)


@dataclass
class Slot:
    from_point: Vec2 = (0.0, 0.0)
    to_point: Vec2 = (1.0, 0.0)
    gap: float = 0.2
