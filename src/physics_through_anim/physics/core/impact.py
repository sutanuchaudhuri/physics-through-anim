"""Impact model (Milestone M12). Scaffold.

Velocity is discontinuous across an impact: a ``PiecewiseTrajectory`` never
interpolates velocity through the impact (STEP), position stays continuous. The
impact law is supplied via ``ImpactData``, never solved.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ImpactData:
    time: float = 0.0
    before: Mapping = field(default_factory=dict)
    after: Mapping = field(default_factory=dict)
    restitution: float = 1.0
    impulse: float = 0.0


@dataclass
class PiecewiseTrajectory:
    """Pre-impact segment -> ImpactEvent -> post-impact segment."""

    segments: list = field(default_factory=list)
    impacts: list = field(default_factory=list)

    def state_at(self, t: float):
        raise NotImplementedError("M12 PiecewiseTrajectory.state_at")
