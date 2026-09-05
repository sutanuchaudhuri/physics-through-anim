"""Factory for building lesson configurations from a text-based (TOML) manifest.

Instead of hardcoding scene registries as Python dict literals, every lesson's
scene list lives in ``lessons/lessons.toml``. This module parses that manifest
once and hands out immutable ``LessonConfig`` objects through
``LessonRegistry``, a small factory that the rendering pipeline in
``render.py`` consumes generically -- one code path for every lesson instead
of one copy-pasted pair of functions per lesson.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

LESSONS_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = LESSONS_DIR / "lessons.toml"


@dataclass(frozen=True)
class SceneEntry:
    """One renderable scene within a lesson."""

    scene_id: str
    file: str
    class_name: str
    narration: str
    chapter: str

    @property
    def module_stem(self) -> str:
        """The scene file name without its ``.py`` suffix (used for manim's output folder)."""
        return self.file[:-3] if self.file.endswith(".py") else self.file


@dataclass(frozen=True)
class LessonConfig:
    """Everything the render pipeline needs to know about one lesson."""

    name: str
    dir: Path
    audio_subdir: str
    final_output: str
    scenes: dict[str, SceneEntry] = field(default_factory=dict)
    chapter_scene_ids: dict[str, list[str]] = field(default_factory=dict)

    def resolve_scene_ids(self, selector: str) -> list[str]:
        """Expand "all", a chapter id, or a single scene id into a scene id list."""
        if selector == "all":
            return list(self.scenes)
        if selector in self.chapter_scene_ids:
            return self.chapter_scene_ids[selector]
        return [selector]

    def scene_choices(self) -> tuple[str, ...]:
        """All valid selectors for this lesson: "all", chapter ids, and scene ids."""
        return ("all", *self.scenes, *self.chapter_scene_ids)


class LessonRegistry:
    """Factory that builds and caches ``LessonConfig`` objects from the TOML manifest."""

    def __init__(self, manifest_path: Path = MANIFEST_PATH, lessons_root: Path = LESSONS_DIR):
        self._manifest_path = manifest_path
        self._lessons_root = lessons_root
        self._cache: dict[str, LessonConfig] = {}

    def _load_manifest(self) -> dict:
        with self._manifest_path.open("rb") as handle:
            return tomllib.load(handle)

    def _build(self, name: str, raw: dict) -> LessonConfig:
        scenes: dict[str, SceneEntry] = {}
        chapter_scene_ids: dict[str, list[str]] = {}
        for scene_id, scene_raw in raw["scenes"].items():
            entry = SceneEntry(
                scene_id=scene_id,
                file=scene_raw["file"],
                class_name=scene_raw["class_name"],
                narration=scene_raw["narration"],
                chapter=scene_raw["chapter"],
            )
            scenes[scene_id] = entry
            chapter_scene_ids.setdefault(entry.chapter, []).append(scene_id)
        return LessonConfig(
            name=name,
            dir=self._lessons_root / raw["dir"],
            audio_subdir=raw["audio_subdir"],
            final_output=raw["final_output"],
            scenes=scenes,
            chapter_scene_ids=chapter_scene_ids,
        )

    def all_lesson_names(self) -> list[str]:
        return list(self._load_manifest()["lessons"])

    def get(self, name: str) -> LessonConfig:
        if name not in self._cache:
            manifest = self._load_manifest()
            try:
                raw = manifest["lessons"][name]
            except KeyError as exc:
                raise KeyError(f"Unknown lesson '{name}' in {self._manifest_path}") from exc
            self._cache[name] = self._build(name, raw)
        return self._cache[name]


registry = LessonRegistry()
