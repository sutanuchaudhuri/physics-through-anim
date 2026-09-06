"""TDD spec for M12 -- collisions / impulse / event sequences."""

from __future__ import annotations

import pytest

from physics_through_anim.physics.core.events import EventKind
from physics_through_anim.physics.core.impact import ImpactData, PiecewiseTrajectory
from physics_through_anim.physics.overlays.events import EventCounter, collision

TDD = pytest.mark.xfail(reason="M12 not implemented (TDD spec)", strict=False)


def test_impact_data_carries_supplied_law() -> None:
    d = ImpactData(time=1.73, before={"m1.v": 4.2}, after={"m1.v": 1.4}, restitution=0.8)
    assert d.restitution == 0.8
    assert d.before["m1.v"] == 4.2
    assert EventCounter().kinds == (EventKind.IMPACT,)


@TDD
def test_piecewise_trajectory_state_at() -> None:
    PiecewiseTrajectory().state_at(0.5)


@TDD
def test_collision_builds_impact_event() -> None:
    ev = collision("M", "m", t=1.0, restitution=1.0)
    assert ev.kind is EventKind.IMPACT
