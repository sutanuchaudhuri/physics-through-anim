"""Generic rigid-body point kinematics (Milestone M1.6). Scaffold.

``v_P = v_O + omega x r_(P/O)`` and ``a_P = a_O + alpha x r + omega x (omega x r)``.
Not a body-specific feature -- every shape reuses these.
"""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.core.state import RigidKinematicState


def point_position(body, ref: str, state: RigidKinematicState) -> np.ndarray:
    raise NotImplementedError("M1.6 kinematics.point_position")


def point_velocity(body, ref: str, state: RigidKinematicState) -> np.ndarray:
    raise NotImplementedError("M1.6 kinematics.point_velocity")


def point_acceleration(body, ref: str, state: RigidKinematicState) -> np.ndarray:
    raise NotImplementedError("M1.6 kinematics.point_acceleration")
