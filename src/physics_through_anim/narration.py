"""Keep a scene's video length in sync with its narration audio.

TTS narration (generated from the scene's ``narration/*.md``) is often longer
than the scene's animated timeline. Without help, the video ends while the
voice-over is still talking -- narration playing over nothing. These helpers
let a scene hold its final frame until the narration finishes, so audio and
video always end together.

``add_narration()`` on each lesson base class registers the audio; call
``self.finish_with_narration()`` as the last line of ``construct()`` to pad the
ending. See SKILL.md Rule 18.
"""

from __future__ import annotations

import contextlib
import os
import wave
from pathlib import Path
from typing import Any


def narration_seconds(path: str | None = None) -> float:
    """Duration in seconds of the active narration WAV, or 0.0 if none/unreadable."""
    path = path or os.environ.get("PHYSICS_NARRATION_FILE")
    if not path or not Path(path).exists():
        return 0.0
    try:
        with contextlib.closing(wave.open(path, "rb")) as handle:
            return handle.getnframes() / float(handle.getframerate())
    except (wave.Error, OSError):
        return 0.0


def hold_for_narration(scene: Any, min_tail: float = 0.75, min_hold: float = 0.4) -> None:
    """Wait so the scene's total length reaches (narration length + min_tail).

    If narration is off/absent, or the visuals already outlast it, just holds a
    short ``min_hold`` so the last frame doesn't cut instantly. ``scene.time`` is
    manim's accumulated rendered time.
    """
    target = narration_seconds()
    elapsed = float(getattr(scene, "time", 0.0))
    remaining = (target + min_tail) - elapsed
    logger = getattr(scene, "log_event", None)
    if callable(logger):
        logger("narration_hold", narration_s=round(target, 2), elapsed_s=round(elapsed, 2),
               pad_s=round(max(remaining, min_hold), 2))
    scene.wait(max(remaining, min_hold))
