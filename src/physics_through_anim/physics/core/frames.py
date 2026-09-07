"""Reference-frame transforms (Milestone M1.6).

A pure kinematic map between a frame's local coordinates and world coordinates.
It never integrates motion -- M14 supplies a moving frame's motion as a
``FrameState``. Points get translation + rotation; vectors get rotation only.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from physics_through_anim.physics.core.pose import Pose2D, Vec2


@dataclass
class Frame2D:
    """A 2D reference frame; pure kinematic map (never integrates)."""

    pose: Pose2D = field(default_factory=Pose2D)

    def to_world_point(self, p_local: Vec2) -> np.ndarray:
        return self.pose.world_point(p_local)

    def to_local_point(self, p_world: Vec2) -> np.ndarray:
        return self.pose.to_transform().inverse().transform_point(p_world)

    def to_world_vector(self, v_local: Vec2) -> np.ndarray:
        return self.pose.world_vector(v_local)

    def to_local_vector(self, v_world: Vec2) -> np.ndarray:
        return self.pose.to_transform().inverse().transform_vector(v_world)

