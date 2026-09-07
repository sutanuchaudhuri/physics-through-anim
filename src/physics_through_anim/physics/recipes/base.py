"""Recipe: textbook compositions (Milestone M15).

A ``Recipe`` stores **specs** (not VGroups): a semantic ``Assembly`` + an event
timeline + named overlays/trajectories/moments/camera anchors. A human writes
``kepler_orbit(e=0.6)``; an AI builds the same graph; both yield the same
declarative bundle a renderer/scene can drive without knowing internals.
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
        """Resolve a named body / overlay / trajectory / moment / camera anchor."""
        if self.assembly is not None and hasattr(self.assembly, "body"):
            try:
                return self.assembly.body(key)
            except (KeyError, ValueError):
                pass
        for table in (self.overlays, self.trajectories, self.moments, self.camera_anchors):
            if key in table:
                return table[key]
        raise KeyError(f"Recipe has nothing named '{key}'.")

