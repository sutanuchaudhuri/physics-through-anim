"""Compose multiple assets, place bodies on supports, and build a combined FBD.

An ``Assembly`` groups sub-assets into one ``VGroup``, resolves simple relative
placement (drop a body so it rests on a floor), namespaces every keypoint by
asset name (``"block.CM"``), and can render the union of all members' free-body
diagrams.
"""

from __future__ import annotations

import numpy as np
from manim import VGroup

from physics_through_anim.physics.mechanics.base import PhysicsAsset
from physics_through_anim.physics.mechanics.supports import Floor


class Assembly:
    """A named collection of placed assets."""

    def __init__(self) -> None:
        self.members: list[PhysicsAsset] = []
        self.mobject = VGroup()
        self.keypoints: dict[str, np.ndarray] = {}

    def add(self, asset: PhysicsAsset, place_on: PhysicsAsset | None = None) -> PhysicsAsset:
        """Add an asset, optionally resting it on ``place_on`` (a Floor for now)."""
        if place_on is not None:
            self._place_on(asset, place_on)
        self.members.append(asset)
        self.mobject.add(asset.mobject)
        for key, point in asset.keypoints.items():
            self.keypoints[f"{asset.name}.{key}"] = point
        return asset

    def _place_on(self, body: PhysicsAsset, support: PhysicsAsset) -> None:
        """Shift ``body`` so its bottom rests on ``support``'s surface."""
        if not isinstance(support, Floor):
            raise NotImplementedError("Milestone 1 only supports placement on a Floor.")
        if "bottom" not in body.keypoints:
            raise KeyError(f"'{body.name}' has no 'bottom' keypoint to rest on the floor.")
        gap = support.y - body.keypoint("bottom")[1]
        body.shift([0.0, gap])
        # Register the resting contact point on the body for FBD anchoring.
        contact_x = body.keypoint("CM")[0]
        body.set_keypoint("contact", support.contact_under(contact_x))

    def keypoint(self, key: str) -> np.ndarray:
        if key not in self.keypoints:
            raise KeyError(f"Unknown keypoint '{key}'. Known: {list(self.keypoints)}")
        return self.keypoints[key]

    def fbd(self, include=None) -> VGroup:
        """Union of every member's free-body diagram."""
        group = VGroup()
        for asset in self.members:
            group.add(asset.fbd(include=include))
        return group
