"""Signals + GraphBinding (Milestone M9).

A ``Signal`` resolves an (t, SystemState) pair to a scalar, so graphs work across
the whole system (N vs theta, energy vs t, phase portraits) without State.extra.
``GraphBinding`` samples a trajectory into an axes + curve and syncs a cursor to a
``ValueTracker`` so a moving body and a live plot stay in lock-step.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from manim import YELLOW, Axes, Dot, VGroup, VMobject

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
        """Look ``ref`` up in ``system_state.observables`` (scalar or ``(t, s) -> float``)."""
        observables = getattr(system_state, "observables", None) or {}
        value = observables[str(self.ref)]
        return float(value(t, system_state)) if callable(value) else float(value)


@dataclass
class CallableSignal:
    """Adapts a plain ``lambda s: ...`` (or ``lambda t, s: ...``) to the Signal protocol."""

    fn: object = None

    def resolve(self, t: float, system_state) -> float:
        try:
            return float(self.fn(t, system_state))
        except TypeError:
            return float(self.fn(system_state))


def _as_signal(spec) -> Signal:
    if spec is None or isinstance(spec, str):
        return TimeSignal()
    if hasattr(spec, "resolve"):
        return spec
    return CallableSignal(spec)


def _with_step(rng: tuple[float, float]) -> tuple[float, float, float]:
    lo, hi = rng
    step = (hi - lo) / 5.0 or 1.0
    return (lo, hi, step)


@dataclass
class GraphBinding:
    """Axes + plotted curve + a cursor synced to a trajectory."""

    x: object = None
    y: object = None
    x_range: tuple[float, float] = (0.0, 1.0)
    y_range: tuple[float, float] = (0.0, 1.0)
    cursor: bool = True
    axes: Axes | None = field(default=None, init=False)
    curve: VMobject | None = field(default=None, init=False)
    cursor_dot: Dot | None = field(default=None, init=False)
    _traj: object = field(default=None, init=False)

    def _point(self, axes: Axes, t: float, system_state):
        xs = _as_signal(self.x)
        ys = _as_signal(self.y)
        return axes.c2p(xs.resolve(t, system_state), ys.resolve(t, system_state))

    def build(self, traj, t0: float, t1: float, n: int = 100) -> VGroup:
        axes = Axes(
            x_range=_with_step(self.x_range),
            y_range=_with_step(self.y_range),
            x_length=4.0,
            y_length=3.0,
            tips=False,
        )
        points = [self._point(axes, t0 + (t1 - t0) * i / n, traj.state_at(t0 + (t1 - t0) * i / n))
                  for i in range(n + 1)]
        curve = VMobject(color=YELLOW, stroke_width=4)
        curve.set_points_as_corners(points)
        group = VGroup(axes, curve)
        cursor_dot = Dot(points[0], color=YELLOW, radius=0.07)
        if self.cursor:
            group.add(cursor_dot)
        self.axes, self.curve, self.cursor_dot, self._traj = axes, curve, cursor_dot, traj
        return group

    def bind(self, scene, tracker) -> None:
        """Drive ``cursor_dot`` along the curve as ``tracker`` advances (a ValueTracker)."""
        if self.cursor_dot is None or self.axes is None:
            raise RuntimeError("GraphBinding.bind requires build() first")

        def _update(dot):
            t = tracker.get_value()
            dot.move_to(self._point(self.axes, t, self._traj.state_at(t)))

        self.cursor_dot.add_updater(_update)
