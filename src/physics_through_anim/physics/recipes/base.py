"""Recipe: textbook compositions (Milestone M15). Scaffold.

A Recipe stores specs (not VGroups): assembly + events + overlays + trajectories +
named moments, so an AI/human can drive it without knowing internals.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Recipe:
    assembly: object = None
    events: object = None
    overlays: dict = field(default_factory=dict)
    trajectories: dict = field(default_factory=dict)
    moments: dict = field(default_factory=dict)
    camera_anchors: dict = field(default_factory=dict)

    def named(self, key: str) -> object:
        """Resolve a named body/point/overlay/moment."""
        raise NotImplementedError("M15 Recipe.named")
