"""Animation bindings (Milestone M1.6).

One mechanism drives every rigid body: each binding computes an **absolute**
target ``Pose2D`` (or a target point) and applies it via ``body.set_pose(...)``
-- absolute, so repeated calls never drift. A ``body`` is any object exposing
``set_pose(Pose2D)``, a ``pose`` attribute, and ``keypoint(name)`` (world point).

Bindings are pure pose/geometry (no Manim, no dynamics): they resolve *where*
things go from a supplied state; they never decide ``omega(t)``/forces.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

import numpy as np

from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.kinematics.rolling import RollingKinematicRelation


@runtime_checkable
class Posable(Protocol):
    """A body a binding can drive."""

    pose: Pose2D

    def set_pose(self, pose: Pose2D) -> None: ...
    def keypoint(self, key: str) -> np.ndarray: ...


@dataclass
class RigidPoseBinding:
    """Drive ``body`` from a ``SystemState`` entity's pose."""

    body: Any
    entity: str = ""

    def apply(self, state) -> None:
        self.body.set_pose(state.entities[self.entity].pose)


@dataclass
class PointAttachmentBinding:
    """Move ``child`` (keeping its angle) so its keypoint lands on the parent's."""

    child: Any
    parent: Any
    parent_point: str = ""
    child_point: str = ""

    def apply(self, state=None) -> None:
        target = self.parent.keypoint(self.parent_point)
        current = self.child.keypoint(self.child_point)
        delta = target - current
        pos = self.child.pose.position
        self.child.set_pose(
            Pose2D(position=(pos[0] + delta[0], pos[1] + delta[1]), angle=self.child.pose.angle)
        )


@dataclass
class RelativePoseBinding:
    """Weld ``child`` to ``parent`` at a fixed relative pose (scene-graph edge)."""

    child: Any
    parent: Any
    relative_pose: Pose2D = field(default_factory=Pose2D)

    def apply(self, state=None) -> None:
        self.child.set_pose(self.parent.pose.compose(self.relative_pose))


@dataclass
class PathPoseBinding:
    """Place ``body`` at ``path.point_at(s)``; orient along the tangent by default."""

    body: Any
    path: Any
    s: float = 0.0
    orientation: str = "tangent"

    def apply(self, state=None) -> None:
        pt = self.path.point_at(self.s)
        if self.orientation == "tangent":
            angle = self.path.tangent_angle(self.s)
        else:
            angle = self.body.pose.angle
        self.body.set_pose(Pose2D(position=(float(pt[0]), float(pt[1])), angle=angle))


@dataclass
class RollingPoseBinding:
    """Translate + rotate at ``v = omega R`` via ``RollingKinematicRelation``.

    An optional ``clamp`` post-processes the target pose (e.g. a non-penetration
    projection that keeps a rolling body out of walls) before it is applied.
    """

    body: Any
    relation: RollingKinematicRelation = field(default_factory=RollingKinematicRelation)
    origin: Pose2D = field(default_factory=Pose2D)
    s: float = 0.0
    clamp: Callable[[Pose2D], Pose2D] | None = None

    def apply(self, state=None) -> None:
        pose = self.origin.compose(self.relation.pose_from_arc(self.s))
        if self.clamp is not None:
            pose = self.clamp(pose)
        self.body.set_pose(pose)
