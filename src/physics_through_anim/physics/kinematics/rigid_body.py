"""Generic rigid-body point kinematics (Milestone M1.6).

``v_P = v_O + omega x r_(P/O)`` and ``a_P = a_O + alpha x r + omega x (omega x r)``.
Not a body-specific feature -- every shape (block, rod, disk, plate) reuses these.
A ``body`` is anything exposing a ``local_keypoints`` mapping; ``O`` is its CM.
"""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.core.state import RigidKinematicState


def _local(body, ref: str):
    return body.local_keypoints[ref]


def _cm_world(body, state: RigidKinematicState) -> np.ndarray:
    return state.pose.world_point(body.local_keypoints.get("CM", (0.0, 0.0)))


def point_position(body, ref: str, state: RigidKinematicState) -> np.ndarray:
    """World position of local keypoint ``ref`` under ``state.pose``."""
    return state.pose.world_point(_local(body, ref))


def point_velocity(body, ref: str, state: RigidKinematicState) -> np.ndarray:
    """``v_P = v_O + omega x r_(P/O)`` (omega x r = omega * (-r_y, r_x))."""
    r = point_position(body, ref, state) - _cm_world(body, state)
    v = state.velocity or (0.0, 0.0)
    omega = state.omega or 0.0
    v_o = np.array([v[0], v[1], 0.0])
    return v_o + omega * np.array([-r[1], r[0], 0.0])


def point_acceleration(body, ref: str, state: RigidKinematicState) -> np.ndarray:
    """``a_P = a_O + alpha x r + omega x (omega x r)``."""
    r = point_position(body, ref, state) - _cm_world(body, state)
    a = state.acceleration or (0.0, 0.0)
    omega = state.omega or 0.0
    alpha = state.alpha or 0.0
    a_o = np.array([a[0], a[1], 0.0])
    tangential = alpha * np.array([-r[1], r[0], 0.0])
    centripetal = -(omega**2) * r
    return a_o + tangential + centripetal

