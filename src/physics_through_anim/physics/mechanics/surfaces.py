"""Surface protocol + line surfaces (Milestone M2; extended in M8). Scaffold.

A surface is geometry owned by an entity (which may move), exposing
point/tangent/normal/curvature so contact mechanics come for free.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

from physics_through_anim.physics.core.pose import Vec2


class Surface(Protocol):
    """Parametric surface interface (s in [0, 1])."""

    def point_at(self, s: float) -> np.ndarray: ...
    def tangent_at(self, s: float) -> np.ndarray: ...
    def normal_at(self, s: float) -> np.ndarray: ...
    def curvature_at(self, s: float) -> float: ...
    def length(self) -> float: ...


@dataclass
class LineSurface:
    """A straight segment surface from ``a`` to ``b`` (parameter ``s`` in [0, 1])."""

    a: Vec2 = (0.0, 0.0)
    b: Vec2 = (1.0, 0.0)

    def _dir(self) -> np.ndarray:
        d = np.array([self.b[0] - self.a[0], self.b[1] - self.a[1], 0.0])
        n = np.linalg.norm(d)
        return d / n if n else np.array([1.0, 0.0, 0.0])

    def point_at(self, s: float) -> np.ndarray:
        return np.array(
            [self.a[0] + s * (self.b[0] - self.a[0]), self.a[1] + s * (self.b[1] - self.a[1]), 0.0]
        )

    def tangent_at(self, s: float) -> np.ndarray:
        return self._dir()

    def normal_at(self, s: float) -> np.ndarray:
        """Left (outward) unit normal: tangent rotated +90 degrees."""
        t = self._dir()
        return np.array([-t[1], t[0], 0.0])

    def curvature_at(self, s: float) -> float:
        return 0.0

    def length(self) -> float:
        return float(np.hypot(self.b[0] - self.a[0], self.b[1] - self.a[1]))


@dataclass
class FloorSurface(LineSurface):
    """A horizontal floor surface."""


@dataclass
class InclineSurface(LineSurface):
    """A straight inclined surface at ``angle`` radians."""

    angle: float = 0.0
