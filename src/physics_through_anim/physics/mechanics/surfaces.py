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
    """A straight segment surface."""

    a: Vec2 = (0.0, 0.0)
    b: Vec2 = (1.0, 0.0)

    def point_at(self, s: float) -> np.ndarray:
        raise NotImplementedError("M2 LineSurface.point_at")

    def tangent_at(self, s: float) -> np.ndarray:
        raise NotImplementedError("M2 LineSurface.tangent_at")

    def normal_at(self, s: float) -> np.ndarray:
        raise NotImplementedError("M2 LineSurface.normal_at")

    def curvature_at(self, s: float) -> float:
        return 0.0

    def length(self) -> float:
        raise NotImplementedError("M2 LineSurface.length")


@dataclass
class FloorSurface(LineSurface):
    """A horizontal floor surface."""


@dataclass
class InclineSurface(LineSurface):
    """A straight inclined surface at ``angle`` radians."""

    angle: float = 0.0
