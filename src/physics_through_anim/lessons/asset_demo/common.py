"""Base scene for the asset-library demo lesson (narration + logging + header).

Mirrors ``RodLessonScene``/``RollingLessonScene`` (SKILL Rules 11, 14, 18) with
only the helpers this demo needs.
"""

from __future__ import annotations

import os
from pathlib import Path

from manim import DOWN, GRAY, LEFT, ORANGE, UP, MovingCameraScene, Text, VGroup, config

from physics_through_anim.scene_logging import SceneEventLogMixin

DEFAULT_FRAME_WIDTH = config.frame_width


class AssetDemoScene(SceneEventLogMixin, MovingCameraScene):
    """Shared base: local narration playback + per-scene event log."""

    LESSON_NAME = "asset_demo"

    def add_narration(self) -> None:
        narration_file = os.environ.get("PHYSICS_NARRATION_FILE")
        if narration_file and Path(narration_file).exists():
            self.add_sound(narration_file)

    def finish_with_narration(self, min_tail: float = 0.75) -> None:
        """Hold the final frame until the narration ends (SKILL Rule 18)."""
        from physics_through_anim.narration import hold_for_narration

        hold_for_narration(self, min_tail=min_tail)

    def scene_header(self, scene_id: str, heading: str, subtitle: str) -> VGroup:
        label = Text(f"Scene {scene_id}", font_size=16, color=GRAY).to_corner(UP + LEFT, buff=0.3)
        title = Text(heading, font_size=28, weight="BOLD").to_edge(UP, buff=0.25)
        sub = Text(subtitle, font_size=18, color=ORANGE).next_to(title, DOWN, buff=0.08)
        return VGroup(label, title, sub)
