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

import numpy as np

Vec2 = tuple[float, float]


@dataclass(frozen=True)
class Pose2D:
    """Absolute position + orientation of a body frame in the world."""

    position: Vec2 = (0.0, 0.0)
    angle: float = 0.0  # absolute orientation in radians

    def world_point(self, local: Vec2) -> np.ndarray:
        """Rotate ``local`` by ``angle`` then translate by ``position`` (T+R).

        Returns a 3D world point ``[x, y, 0]``.
        """
        raise NotImplementedError("M1.5 pose.world_point")

    def world_vector(self, local_vec: Vec2) -> np.ndarray:
        """Rotate ``local_vec`` by ``angle`` only (no translation) -> ``[x, y, 0]``."""
        raise NotImplementedError("M1.5 pose.world_vector")

    def compose(self, child: Pose2D) -> Pose2D:
        """Return the world pose of ``child`` expressed in this (parent) frame."""
        raise NotImplementedError("M1.5 pose.compose")
