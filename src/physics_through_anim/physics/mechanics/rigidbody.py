"""RigidBody2D + BodyState2D (Milestone M1.5).

Plan: plans/asset_library/M01_5_pose_rigidbody.md. Generic rigid-body point
kinematics -- ``v_P = v_G + omega x r_(P/G)`` -- exposed as a body method that any
shape (block, rod, disk, plate) reuses. Poses are absolute (no drift).

At implementation time this merges into ``bodies.py`` and delegates its point
kinematics to ``physics/kinematics/rigid_body.py`` (M1.6); it lives in its own
module here so the M1.5 scaffold does not touch shipped M1 code.

Status: SCAFFOLD (M1.5). Method bodies are unimplemented; see the test plan.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.mechanics.massprops import MassProperties

Vec2 = tuple[float, float]


@dataclass
class BodyState2D:
    """A solver-supplied per-body kinematic state (alias of RigidKinematicState, M6)."""

    pose: Pose2D = Pose2D()
    velocity: Vec2 = (0.0, 0.0)
    omega: float = 0.0
    acceleration: Vec2 = (0.0, 0.0)
    alpha: float = 0.0


@dataclass
class RigidBody2D:
    """A rigid body: canonical local keypoints + absolute pose + mass properties."""

    mass_props: MassProperties = MassProperties()
    pose: Pose2D = Pose2D()
    local_keypoints: dict[str, Vec2] = field(default_factory=dict)

    def set_pose(self, pose: Pose2D) -> None:
        """Set the ABSOLUTE pose (rebuild from canonical geometry -- never accumulate)."""
        self.pose = pose

    def keypoint(self, key: str) -> np.ndarray:
        """World coordinates of a local keypoint under the current pose."""
        return self.pose.world_point(self.local_keypoints[key])

    def _cm_world(self, state: BodyState2D | None) -> np.ndarray:
        pose = state.pose if state is not None else self.pose
        return pose.world_point(self.local_keypoints.get("CM", (0.0, 0.0)))

    def point_position(self, ref: str, state: BodyState2D | None = None) -> np.ndarray:
        """World position of local keypoint ``ref`` (using ``state.pose`` if given)."""
        pose = state.pose if state is not None else self.pose
        return pose.world_point(self.local_keypoints[ref])

    def point_velocity(self, ref: str, state: BodyState2D) -> np.ndarray:
        """``v_P = v_G + omega x r_(P/G)`` -- delegates to ``kinematics.rigid_body``."""
        from physics_through_anim.physics.kinematics.rigid_body import point_velocity

        return point_velocity(self, ref, state)

    def point_acceleration(self, ref: str, state: BodyState2D) -> np.ndarray:
        """``a_P = a_G + alpha x r + omega x (omega x r)`` -- delegates to kinematics."""
        from physics_through_anim.physics.kinematics.rigid_body import point_acceleration

        return point_acceleration(self, ref, state)

    def inertia_about(self, ref: str) -> float:
        """Inertia about local keypoint ``ref`` via the CM offset (parallel axis)."""
        local_cm = np.array(self.local_keypoints.get("CM", (0.0, 0.0)))
        offset = np.array(self.local_keypoints[ref]) - local_cm
        return self.mass_props.inertia_about((float(offset[0]), float(offset[1])))
