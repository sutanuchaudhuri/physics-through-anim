"""Typed references (Milestone M1.5).

Plan: plans/asset_library/M01_5_pose_rigidbody.md. String-parseable, YAML-friendly
handles used to name assets, keypoints, surfaces, and physical quantities without
passing raw objects around.

Status: SCAFFOLD (M1.5). ``parse`` is unimplemented; see the test plan.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AssetRef:
    """A named asset, e.g. ``AssetRef("disk")``."""

    name: str = ""

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class PointRef:
    """A keypoint on an asset, e.g. ``PointRef("disk", "P")`` -> ``"disk.P"``."""

    asset: str = ""
    key: str = ""

    def __str__(self) -> str:
        return f"{self.asset}.{self.key}"


@dataclass(frozen=True)
class SurfaceRef:
    """A named surface on an asset, e.g. ``SurfaceRef("wedge", "incline")``."""

    asset: str = ""
    name: str = ""

    def __str__(self) -> str:
        return f"{self.asset}.{self.name}"


@dataclass(frozen=True)
class QuantityRef:
    """A physical observable, e.g. ``QuantityRef("contact:disk.floor:N")``."""

    path: str = ""

    def __str__(self) -> str:
        return self.path


def parse(ref: str) -> PointRef:
    """Parse ``"asset.key"`` into a :class:`PointRef` (round-trips via ``str``)."""
    raise NotImplementedError("M1.5 refs.parse")
