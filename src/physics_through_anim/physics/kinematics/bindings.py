"""Animation bindings (Milestone M1.6). Scaffold.

One mechanism drives every rigid body: resolve refs against the assembly +
SystemState, compute a target Pose2D/point, apply via absolute ``set_pose``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Binding(Protocol):
    """Resolves state into a target pose/point and applies it."""

    def apply(self, assembly, state) -> None: ...


@dataclass
class RigidPoseBinding:
    """SystemState entity pose -> body pose."""

    body: str = ""
    pose_source: str = ""

    def apply(self, assembly, state) -> None:
        raise NotImplementedError("M1.6 RigidPoseBinding.apply")


@dataclass
class PointAttachmentBinding:
    """A child keypoint follows a parent keypoint."""

    child_point: str = ""
    parent_point: str = ""

    def apply(self, assembly, state) -> None:
        raise NotImplementedError("M1.6 PointAttachmentBinding.apply")


@dataclass
class PathPoseBinding:
    """A body follows a curve; orientation = tangent."""

    body: str = ""
    path: str = ""
    parameter: str = "s"
    orientation: str = "tangent"

    def apply(self, assembly, state) -> None:
        raise NotImplementedError("M1.6 PathPoseBinding.apply")


@dataclass
class RollingPoseBinding:
    """Translate + rotate at v = omega R (uses RollingKinematicRelation)."""

    body: str = ""
    surface: str = ""

    def apply(self, assembly, state) -> None:
        raise NotImplementedError("M1.6 RollingPoseBinding.apply")
