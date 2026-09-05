from __future__ import annotations

import os
from pathlib import Path

from manim import Scene


class LocalNarrationScene(Scene):
    """Play a local narration file when the renderer supplies one."""

    def add_local_narration(self) -> None:
        narration_file = os.environ.get("PHYSICS_NARRATION_FILE")
        if narration_file and Path(narration_file).exists():
            self.add_sound(narration_file)
