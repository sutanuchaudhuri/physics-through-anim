"""Live state snapshots: freeze an ``Assembly``'s placed geometry (Milestone M17).

Where ``assembly_io`` serialises the *authoring* spec (constructor params), this
captures the *current* world geometry -- every member's live keypoints and its
applied rotation -- after placement/animation. Snapshots are serialisable via
``serialization.codec`` (JSON/XML) and are what the non-Manim renderers draw.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from physics_through_anim.physics.mechanics import Assembly, PhysicsAsset

__all__ = ["AssetSnapshot", "AssemblySnapshot", "snapshot_asset", "snapshot_assembly"]


@dataclass
class AssetSnapshot:
    """One asset's placed geometry: world keypoints (x, y) plus applied angle."""

    name: str = ""
    kind: str = ""
    angle: float = 0.0  # radians, from PhysicsAsset._applied_angle
    color: str | None = None  # the asset's own colour as a hex string (if any)
    keypoints: dict[str, tuple[float, float]] = field(default_factory=dict)


@dataclass
class AssemblySnapshot:
    """A freeze-frame of an assembly at scene time ``t``."""

    t: float = 0.0
    assets: list[AssetSnapshot] = field(default_factory=list)


def _hex_color(value: object) -> str | None:
    """Best-effort convert an asset colour (hex str or ManimColor) to a hex string."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    to_hex = getattr(value, "to_hex", None)
    return to_hex() if callable(to_hex) else None


def snapshot_asset(asset: PhysicsAsset) -> AssetSnapshot:
    """Capture one asset's live keypoints, applied rotation, and colour."""
    keypoints = {
        key: (float(point[0]), float(point[1]))
        for key, point in asset.keypoints.items()
    }
    return AssetSnapshot(
        name=asset.name,
        kind=type(asset).__name__,
        angle=float(getattr(asset, "_applied_angle", 0.0)),
        color=_hex_color(getattr(asset, "color", None)),
        keypoints=keypoints,
    )


def snapshot_assembly(assembly: Assembly, *, t: float = 0.0) -> AssemblySnapshot:
    """Freeze every member's placed geometry into a serialisable snapshot."""
    return AssemblySnapshot(t=t, assets=[snapshot_asset(m) for m in assembly.members])
