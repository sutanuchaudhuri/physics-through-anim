"""Per-scene event transcript logging.

Independent of manim's own render log and of narration audio, this gives every
scene an append-only, human-readable transcript of "what happened when":
which mobjects were created/moved, at what on-screen position, in which
animation index, and at what wall-clock time. Use it to answer "what did the
rod's angle actually reach in scene 23" or "why did this vector end up
off-screen" after the fact, without re-rendering.

Every lesson's base `<Lesson>Scene` class should mix in `SceneEventLogMixin`
(see the scaffold rule in `.github/skills/physics-animation-standards/SKILL.md`)
so every new scene gets a transcript for free. Individual scenes can add extra
`self.log_event(...)` / `self.log_mobject(...)` calls by hand wherever the
automatic ones aren't enough -- this is meant to be extended manually, not
just auto-generated.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

LOG_ROOT = Path(__file__).resolve().parents[2] / "media" / "logs"


def _lookup_scene_id(lesson_name: str, class_name: str) -> str:
    """Find this scene's id in lessons.toml by class name, without per-scene wiring."""
    from physics_through_anim.lessons.lesson_registry import registry

    try:
        lesson = registry.get(lesson_name)
    except KeyError:
        return "NA"
    for scene_id, entry in lesson.scenes.items():
        if entry.class_name == class_name:
            return scene_id
    return "NA"


def configure_scene_logger(lesson_name: str, scene_id: str, class_name: str) -> logging.Logger:
    """Return a logger that appends to media/logs/<lesson_name>/<scene_id>_<ClassName>.log."""
    log_dir = LOG_ROOT / lesson_name
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{scene_id}_{class_name}.log"
    logger = logging.getLogger(f"physics_through_anim.{lesson_name}.{scene_id}")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
    handler = logging.FileHandler(log_path, mode="w")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


class SceneEventLogMixin:
    """Mix into a lesson's base Scene class to get an automatic per-scene transcript.

    Requires the subclass to define ``LESSON_NAME`` (str) as a class attribute.
    The scene id is looked up from ``lessons.toml`` by class name automatically
    -- no per-scene-file wiring needed. Call ``self.log_event(...)`` /
    ``self.log_mobject(...)`` from within ``construct()`` for anything the
    automatic setup/teardown hooks don't cover.
    """

    LESSON_NAME: str = "unknown_lesson"

    def setup(self) -> None:
        super().setup()
        scene_id = _lookup_scene_id(self.LESSON_NAME, type(self).__name__)
        self._event_logger = configure_scene_logger(
            self.LESSON_NAME, scene_id, type(self).__name__
        )
        self.log_event("scene_setup", scene_class=type(self).__name__)

    def log_event(self, label: str, **fields: Any) -> None:
        """Log a free-form event: label plus arbitrary key=value fields."""
        played = getattr(getattr(self, "renderer", None), "num_plays", "?")
        extra = " ".join(f"{key}={value!r}" for key, value in fields.items())
        self._event_logger.info("animation=%s event=%s %s", played, label, extra)

    def log_mobject(self, label: str, mobject: Any) -> None:
        """Log a mobject's current on-screen state: type, center, and color."""
        center = mobject.get_center()
        color = getattr(mobject, "color", None)
        rounded_center = tuple(round(float(c), 3) for c in center)
        self.log_event(
            label,
            type=type(mobject).__name__,
            center=rounded_center,
            color=str(color) if color is not None else None,
        )

    def tear_down(self) -> None:
        self.log_event("scene_teardown")
        super().tear_down()
