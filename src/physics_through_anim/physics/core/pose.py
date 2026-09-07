"""Pose2D: canonical geometry + absolute pose (Milestone M1.5).

Plan: plans/asset_library/M01_5_pose_rigidbody.md (moved to core per the
kinematics review). A ``Pose2D`` maps a body-frame (local) point or vector into
world coordinates. Poses are absolute, never accumulated, so repeated updater
calls (rolling, trajectories) do not drift.

Status: SCAFFOLD (M1.5). Method bodies are intentionally unimplemented; the
acceptance criteria live as tests in ``tests/test_m1_5_pose_rigidbody.py`` and
``plans/asset_library/M01_5_TESTPLAN.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, sin

import numpy as np

Vec2 = tuple[float, float]


@dataclass(frozen=True)
class Pose2D:
    """Absolute position + orientation of a body frame in the world."""

    position: Vec2 = (0.0, 0.0)
    angle: float = 0.0  # absolute orientation in radians

    def to_transform(self):
        """This pose as an SE(2) ``Transform2D`` (imported lazily to avoid a cycle)."""
        from physics_through_anim.physics.core.transforms import Transform2D

        return Transform2D.from_pose(self)

    def world_point(self, local: Vec2) -> np.ndarray:
        """Rotate ``local`` by ``angle`` then translate by ``position`` (T+R)."""
        c, s = cos(self.angle), sin(self.angle)
        x = self.position[0] + c * local[0] - s * local[1]
        y = self.position[1] + s * local[0] + c * local[1]
        return np.array([x, y, 0.0])

    def world_vector(self, local_vec: Vec2) -> np.ndarray:
        """Rotate ``local_vec`` by ``angle`` only (no translation) -> ``[x, y, 0]``."""
        c, s = cos(self.angle), sin(self.angle)
        x = c * local_vec[0] - s * local_vec[1]
        y = s * local_vec[0] + c * local_vec[1]
        return np.array([x, y, 0.0])

    def compose(self, child: Pose2D) -> Pose2D:
        """Return the world pose of ``child`` expressed in this (parent) frame."""
        wp = self.world_point(child.position)
        return Pose2D(position=(float(wp[0]), float(wp[1])), angle=self.angle + child.angle)
