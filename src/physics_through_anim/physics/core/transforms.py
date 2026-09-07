"""SE(2) homogeneous transforms (Milestone M1.6).

Point vs vector is mandatory: a **point** gets translation + rotation, a
**vector** (velocity, force direction) gets rotation only. Lesson writers never
hand-build ``R = [[cos, -sin], [sin, cos]]`` -- they use ``Transform2D`` or the
body API. Reuse the transformation mathematics; never reuse a physics solution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import cos, sin

import numpy as np

from physics_through_anim.physics.core.pose import Pose2D, Vec2


@dataclass(frozen=True)
class Transform2D:
    """A 3x3 SE(2) matrix transform ``[[R, t], [0, 1]]``."""

    m: np.ndarray = field(default_factory=lambda: np.eye(3))

    @classmethod
    def identity(cls) -> Transform2D:
        return cls(np.eye(3))

    @classmethod
    def rotation(cls, theta: float) -> Transform2D:
        """Rotation by ``theta`` about the origin."""
        c, s = cos(theta), sin(theta)
        m = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
        return cls(m)

    @classmethod
    def translation(cls, x: float, y: float) -> Transform2D:
        m = np.array([[1.0, 0.0, x], [0.0, 1.0, y], [0.0, 0.0, 1.0]])
        return cls(m)

    @classmethod
    def from_pose(cls, pose: Pose2D) -> Transform2D:
        """``[[R(angle), position], [0, 1]]`` -- rotate first, then translate."""
        c, s = cos(pose.angle), sin(pose.angle)
        m = np.array(
            [
                [c, -s, pose.position[0]],
                [s, c, pose.position[1]],
                [0.0, 0.0, 1.0],
            ]
        )
        return cls(m)

    def compose(self, other: Transform2D) -> Transform2D:
        """``self ∘ other`` -- apply ``other`` first (matrix product ``self.m @ other.m``)."""
        return Transform2D(self.m @ other.m)

    def inverse(self) -> Transform2D:
        return Transform2D(np.linalg.inv(self.m))

    def transform_point(self, p: Vec2) -> np.ndarray:
        """Translation + rotation. Returns a manim ``[x, y, 0]`` point."""
        h = np.array([p[0], p[1], 1.0])
        out = self.m @ h
        return np.array([out[0], out[1], 0.0])

    def transform_vector(self, v: Vec2) -> np.ndarray:
        """Rotation only (ignores the translation column). Returns ``[x, y, 0]``."""
        h = np.array([v[0], v[1], 0.0])
        out = self.m @ h
        return np.array([out[0], out[1], 0.0])
