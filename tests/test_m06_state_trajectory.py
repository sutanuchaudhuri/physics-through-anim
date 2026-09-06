"""TDD spec for M6 -- state + trajectory adapters."""

from __future__ import annotations

import pytest

from physics_through_anim.physics.core.state import (
    AssetState,
    InterpolationPolicy,
    StateSnapshot,
    SystemState,
)
from physics_through_anim.physics.core.trajectory import AnalyticTrajectory, SampledTrajectory

TDD = pytest.mark.xfail(reason="M6 not implemented (TDD spec)", strict=False)


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


@TDD
def test_sampled_trajectory_interpolates() -> None:
    SampledTrajectory().state_at(0.5)
