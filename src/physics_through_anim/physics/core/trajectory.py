"""Trajectory providers (Milestone M6).

A ``Trajectory`` is any source of a ``SystemState`` at time t (analytic, sampled,
CSV, SciPy, precomputed). Assets never integrate; motion enters only here.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

import numpy as np

from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.core.state import RigidKinematicState, SystemState


@runtime_checkable
class Trajectory(Protocol):
    """Any source of a complete SystemState at time t."""

    def state_at(self, t: float) -> SystemState: ...


@dataclass
class AnalyticTrajectory:
    """Wraps a pure function ``t -> SystemState``."""

    fn: Callable[[float], SystemState]

    def state_at(self, t: float) -> SystemState:
        return self.fn(t)


def _lerp(a, b, f: float):
    return a + (b - a) * f


def _lerp_vec(a, b, f: float):
    if a is None or b is None:
        return a if a is not None else b
    return (_lerp(a[0], b[0], f), _lerp(a[1], b[1], f))


def _lerp_scalar(a, b, f: float):
    if a is None or b is None:
        return a if a is not None else b
    return _lerp(a, b, f)


def _lerp_state(a: RigidKinematicState, b: RigidKinematicState, f: float) -> RigidKinematicState:
    pose = Pose2D(
        position=_lerp_vec(a.pose.position, b.pose.position, f),
        angle=_lerp(a.pose.angle, b.pose.angle, f),
    )
    return RigidKinematicState(
        pose=pose,
        velocity=_lerp_vec(a.velocity, b.velocity, f),
        acceleration=_lerp_vec(a.acceleration, b.acceleration, f),
        omega=_lerp_scalar(a.omega, b.omega, f),
        alpha=_lerp_scalar(a.alpha, b.alpha, f),
    )


def _lerp_system(a: SystemState, b: SystemState, f: float) -> SystemState:
    entities = {}
    for ref, sa in a.entities.items():
        sb = b.entities.get(ref)
        entities[ref] = _lerp_state(sa, sb, f) if sb is not None else sa
    return SystemState(entities=entities, fields=a.fields, observables=a.observables)


@dataclass
class SampledTrajectory:
    """Linear interpolation between ``(times, states)`` samples."""

    times: np.ndarray = field(default_factory=lambda: np.zeros(0))
    states: list = field(default_factory=list)

    def state_at(self, t: float) -> SystemState:
        times = np.asarray(self.times, dtype=float)
        if times.size == 0:
            return SystemState()
        if t <= times[0]:
            return self.states[0]
        if t >= times[-1]:
            return self.states[-1]
        i = int(np.searchsorted(times, t)) - 1
        t0, t1 = times[i], times[i + 1]
        frac = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
        return _lerp_system(self.states[i], self.states[i + 1], frac)

