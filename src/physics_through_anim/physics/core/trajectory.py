"""Trajectory providers (Milestone M6). Scaffold.

A ``Trajectory`` is any source of a ``SystemState`` at time t (analytic, sampled,
CSV, SciPy, precomputed). Assets never integrate; motion enters only here.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

import numpy as np

from physics_through_anim.physics.core.state import SystemState


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


@dataclass
class SampledTrajectory:
    """Linear interpolation between (times, states) samples."""

    times: np.ndarray = field(default_factory=lambda: np.zeros(0))
    states: list = field(default_factory=list)

    def state_at(self, t: float) -> SystemState:
        raise NotImplementedError("M6 SampledTrajectory.state_at")
