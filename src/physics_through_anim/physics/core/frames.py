"""Reference-frame transforms (Milestone M1.6). Scaffold."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from physics_through_anim.physics.core.pose import Pose2D, Vec2


@dataclass
class Frame2D:
    """A 2D reference frame; pure kinematic map (never integrates)."""

    pose: Pose2D = Pose2D()

    def to_world_point(self, p_local: Vec2) -> np.ndarray:
        raise NotImplementedError("M1.6 Frame2D.to_world_point")

    def to_local_point(self, p_world: Vec2) -> np.ndarray:
        raise NotImplementedError("M1.6 Frame2D.to_local_point")

    def to_world_vector(self, v_local: Vec2) -> np.ndarray:
        raise NotImplementedError("M1.6 Frame2D.to_world_vector")

    def to_local_vector(self, v_world: Vec2) -> np.ndarray:
        raise NotImplementedError("M1.6 Frame2D.to_local_vector")
