"""M6 spec -- state + trajectory adapters."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.core.state import (
    AssetState,
    InterpolationPolicy,
    RigidKinematicState,
    StateSnapshot,
    SystemState,
)
from physics_through_anim.physics.core.trajectory import AnalyticTrajectory, SampledTrajectory


def test_system_state_is_domain_generic() -> None:
    s = SystemState()
    assert dict(s.entities) == {} and dict(s.fields) == {} and dict(s.observables) == {}
    assert AssetState().body is None
    assert StateSnapshot().show == ("body",)
    assert InterpolationPolicy.STEP_LEFT.value == "step_left"


def test_analytic_trajectory_returns_supplied_state() -> None:
    state = SystemState()
    traj = AnalyticTrajectory(fn=lambda t: state)
    assert traj.state_at(0.5) is state


def _state_at(x: float, y: float) -> SystemState:
    return SystemState(entities={"ball": RigidKinematicState(pose=Pose2D(position=(x, y)))})


def test_sampled_trajectory_interpolates_midway() -> None:
    traj = SampledTrajectory(times=np.array([0.0, 2.0]),
                             states=[_state_at(0.0, 0.0), _state_at(4.0, 2.0)])
    mid = traj.state_at(1.0).entities["ball"].pose
    np.testing.assert_allclose(mid.position, (2.0, 1.0), atol=1e-9)


def test_sampled_trajectory_clamps_ends() -> None:
    traj = SampledTrajectory(times=np.array([0.0, 1.0]),
                             states=[_state_at(0.0, 0.0), _state_at(1.0, 1.0)])
    np.testing.assert_allclose(traj.state_at(-5.0).entities["ball"].pose.position, (0.0, 0.0))
    np.testing.assert_allclose(traj.state_at(9.0).entities["ball"].pose.position, (1.0, 1.0))

