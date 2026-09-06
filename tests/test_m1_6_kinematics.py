"""TDD spec for M1.6 -- transforms, frames, state, kinematics, rolling relation."""

from __future__ import annotations

import numpy as np
import pytest

from physics_through_anim.physics.core.frames import Frame2D
from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.core.state import (
    BodyState2D,
    InterpolationPolicy,
    RigidKinematicState,
)
from physics_through_anim.physics.core.transforms import Transform2D
from physics_through_anim.physics.kinematics.rigid_body import point_velocity
from physics_through_anim.physics.kinematics.rolling import RollingKinematicRelation

TDD = pytest.mark.xfail(reason="M1.6 not implemented (TDD spec)", strict=False)


def test_identity_is_3x3() -> None:
    np.testing.assert_allclose(Transform2D.identity().m, np.eye(3))


def test_interpolation_policy_members() -> None:
    assert {p.value for p in InterpolationPolicy} >= {"linear", "angle_unwrap", "none"}


def test_bodystate_alias_and_defaults() -> None:
    assert BodyState2D is RigidKinematicState
    assert RigidKinematicState().velocity is None
    assert Frame2D().pose == Pose2D()


@TDD
def test_transform_point_vs_vector() -> None:
    t = Transform2D.from_pose(Pose2D(position=(2.0, 0.0), angle=np.pi / 2))
    np.testing.assert_allclose(t.transform_point((1.0, 0.0)), [2.0, 1.0, 0.0], atol=1e-9)
    np.testing.assert_allclose(t.transform_vector((1.0, 0.0)), [0.0, 1.0, 0.0], atol=1e-9)


@TDD
def test_rolling_relation_delta_theta() -> None:
    rel = RollingKinematicRelation(radius=2.0, direction=1)
    pose = rel.pose_from_arc(2.0)  # s = R -> Delta theta = -1 rad
    assert abs(pose.angle - (-1.0)) < 1e-9


@TDD
def test_point_velocity_signature() -> None:
    body = object()
    point_velocity(body, "P", RigidKinematicState(velocity=(0.0, 0.0), omega=1.0))
