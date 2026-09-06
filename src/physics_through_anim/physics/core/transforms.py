"""SE(2) homogeneous transforms (Milestone M1.6). Scaffold — see M01_5_TESTPLAN sibling notes.

Point vs vector is mandatory: a point gets translation+rotation, a vector gets
rotation only.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from physics_through_anim.physics.core.pose import Pose2D, Vec2


@dataclass
class Transform2D:
    """A 3x3 SE(2) matrix transform."""

    m: np.ndarray = field(default_factory=lambda: np.eye(3))

    @classmethod
    def identity(cls) -> Transform2D:
        return cls(np.eye(3))

    @classmethod
    def rotation(cls, theta: float) -> Transform2D:
        raise NotImplementedError("M1.6 Transform2D.rotation")

    @classmethod
    def translation(cls, x: float, y: float) -> Transform2D:
        raise NotImplementedError("M1.6 Transform2D.translation")

    @classmethod
    def from_pose(cls, pose: Pose2D) -> Transform2D:
        raise NotImplementedError("M1.6 Transform2D.from_pose")

    def compose(self, other: Transform2D) -> Transform2D:
        raise NotImplementedError("M1.6 Transform2D.compose")

    def inverse(self) -> Transform2D:
        raise NotImplementedError("M1.6 Transform2D.inverse")

    def transform_point(self, p: Vec2) -> np.ndarray:
        """Translation + rotation."""
        raise NotImplementedError("M1.6 Transform2D.transform_point")

    def transform_vector(self, v: Vec2) -> np.ndarray:
        """Rotation only (no translation)."""
        raise NotImplementedError("M1.6 Transform2D.transform_vector")
