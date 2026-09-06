"""Signals + GraphBinding (Milestone M9). Scaffold.

A ``Signal`` resolves an (t, SystemState) pair to a scalar, so graphs work across
the whole system (N vs theta, energy vs t, phase portraits) without State.extra.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from physics_through_anim.physics.core.refs import QuantityRef


class Signal(Protocol):
    def resolve(self, t: float, system_state) -> float: ...


@dataclass
class TimeSignal:
    def resolve(self, t: float, system_state) -> float:
        return t


@dataclass
class QuantitySignal:
    ref: QuantityRef = QuantityRef()

    def resolve(self, t: float, system_state) -> float:
        """Look ``ref`` up in ``system_state.observables``."""
        raise NotImplementedError("M9 QuantitySignal.resolve")


@dataclass
class GraphBinding:
    """Axes + plotted curve + a cursor synced to a trajectory."""

    x: object = None
    y: object = None
    x_range: tuple[float, float] = (0.0, 1.0)
    y_range: tuple[float, float] = (0.0, 1.0)
    cursor: bool = True

    def build(self, traj, t0: float, t1: float, n: int = 100):
        raise NotImplementedError("M9 GraphBinding.build")

    def bind(self, scene, tracker) -> None:
        raise NotImplementedError("M9 GraphBinding.bind")
