"""Relative position and velocity between two body points (Milestone M1.6).

``r_(B/A) = r_B - r_A`` and ``v_(B/A) = v_B - v_A`` -- pure kinematics. A ``ref``
is a ``(body, keypoint)`` pair; both points are evaluated under the same state.
"""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.core.state import RigidKinematicState
from physics_through_anim.physics.kinematics.rigid_body import point_position, point_velocity


def relative_position(
    a_body, a_ref: str, b_body, b_ref: str, state: RigidKinematicState
) -> np.ndarray:
    """``r_(B/A) = r_B - r_A``."""
    return point_position(b_body, b_ref, state) - point_position(a_body, a_ref, state)


def relative_velocity(
    a_body, a_ref: str, b_body, b_ref: str, state: RigidKinematicState
) -> np.ndarray:
    """``v_(B/A) = v_B - v_A``."""
    return point_velocity(b_body, b_ref, state) - point_velocity(a_body, a_ref, state)
