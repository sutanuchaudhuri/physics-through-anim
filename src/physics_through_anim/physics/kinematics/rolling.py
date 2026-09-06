"""Rolling as a declared kinematic relation (Milestones M1.6/M3). Scaffold.

``Delta theta = -Delta s / R`` about the contact -- a declared constraint, not
dynamics.
"""

from __future__ import annotations

from dataclasses import dataclass

from physics_through_anim.physics.core.pose import Pose2D


@dataclass(frozen=True)
class RollingKinematicRelation:
    """Maps arc length to an absolute pose for a rolling body."""

    radius: float = 1.0
    direction: int = 1  # +1 / -1

    def pose_from_arc(self, s: float) -> Pose2D:
        """Absolute pose after rolling arc length ``s`` (Delta theta = -s/R)."""
        raise NotImplementedError("M1.6 RollingKinematicRelation.pose_from_arc")
