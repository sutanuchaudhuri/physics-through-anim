"""Reference frames + pseudo-forces (Milestone M14). Scaffold.

A frame consumes a supplied ``FrameState``; it never integrates. Pseudo-forces are
a separate semantic class (drawn dashed) from real interaction forces.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import numpy as np

from physics_through_anim.physics.core.pose import Pose2D, Vec2


class FrameKind(StrEnum):
    INERTIAL = "inertial"
    TRANSLATING = "translating"
    ROTATING = "rotating"


class PseudoForceKind(StrEnum):
    INERTIAL_PSEUDO = "inertial"
    CENTRIFUGAL = "centrifugal"
    CORIOLIS = "coriolis"
    EULER = "euler"


@dataclass(frozen=True)
class FrameState:
    """Supplied frame motion (never integrated)."""

    pose: Pose2D = Pose2D()
    velocity: Vec2 = (0.0, 0.0)
    angular_velocity: float = 0.0
    acceleration: Vec2 = (0.0, 0.0)
    angular_acceleration: float = 0.0


@dataclass
class ReferenceFrame:
    kind: FrameKind = FrameKind.INERTIAL
    label: str = "S"

    def to_frame(self, point: Vec2, frame_state: FrameState) -> np.ndarray:
        """World point -> frame-relative point (pure coordinate map)."""
        raise NotImplementedError("M14 ReferenceFrame.to_frame")
