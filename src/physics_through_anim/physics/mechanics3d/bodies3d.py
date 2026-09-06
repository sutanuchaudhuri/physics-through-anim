"""3D bodies: Top, Gyroscope (Milestone M16). Scaffold.

The semantic layer (keypoints/forces/state/events) is reused; only geometry +
camera differ. ``Top.as_trajectory`` is an analytic (solver-free) provider.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import numpy as np

Vec3 = tuple[float, float, float]


class BodyStateND(Protocol):
    """2D/3D-uniform per-entity state (pose is Pose2D or Pose3D)."""

    @property
    def pose(self): ...


@dataclass
class Top:
    mass: float = 1.0
    height: float = 1.2
    radius: float = 0.4
    tilt_deg: float = 20.0
    spin_omega: float = 20.0
    precession_omega: float = 1.5
    pivot: Vec3 = (0.0, 0.0, 0.0)

    def axis_tip(self) -> np.ndarray:
        raise NotImplementedError("M16 Top.axis_tip")

    def as_trajectory(self, period: float):
        """Analytic precession provider (axis sweeps a cone)."""
        raise NotImplementedError("M16 Top.as_trajectory")


@dataclass
class Gyroscope:
    spin_omega: float = 30.0
    gimbal: bool = True
