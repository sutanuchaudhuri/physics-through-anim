"""Registry for named, arbitrary-order video compilations ("playlists").

Distinct from `LessonRegistry`/`lessons.toml` (which describes one lesson's
full, fixed scene order): a *compilation* is an explicit, persisted, ordered
list of scene ids from a single lesson that may skip scenes, repeat a scene,
insert a scene out of its numeric order, or overlap with another
compilation's scene list entirely -- e.g. a "01-10" compilation and a
separate "06-11" compilation are both allowed to exist side by side.

Definitions live in `lessons/compilations.toml`. `render.py`'s
`compile_video`/`stitch_compilation` write/read through this registry so a
reorder, insert, or removal is always persisted, not just a one-off ffmpeg
run that's forgotten immediately after.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

COMPILATIONS_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = COMPILATIONS_DIR / "compilations.toml"


@dataclass(frozen=True)
class Compilation:
    """One named, ordered selection of a lesson's scenes."""

    name: str
    lesson: str
    scene_ids: list[str]
    output: str


class CompilationRegistry:
    """Reads and writes named compilation definitions in `compilations.toml`."""

    def __init__(self, manifest_path: Path = MANIFEST_PATH):
        self._manifest_path = manifest_path

    def _load_manifest(self) -> dict:
        if not self._manifest_path.exists():
            return {"compilations": {}}
        with self._manifest_path.open("rb") as handle:
            return tomllib.load(handle)

    def all_names(self) -> list[str]:
        return list(self._load_manifest().get("compilations", {}))

    def get(self, name: str) -> Compilation:
        manifest = self._load_manifest()
        try:
            raw = manifest["compilations"][name]
        except KeyError as exc:
            raise KeyError(f"Unknown compilation '{name}' in {self._manifest_path}") from exc
        return Compilation(
            name=name, lesson=raw["lesson"], scene_ids=list(raw["scenes"]), output=raw["output"]
        )

    def save(self, compilation: Compilation) -> None:
        """Persist (create, or overwrite in place) one compilation's definition."""
        manifest = self._load_manifest()
        compilations = manifest.setdefault("compilations", {})
        compilations[compilation.name] = {
            "lesson": compilation.lesson,
            "scenes": compilation.scene_ids,
            "output": compilation.output,
        }
        self._write_manifest(manifest)

    def delete(self, name: str) -> None:
        manifest = self._load_manifest()
        manifest.get("compilations", {}).pop(name, None)
        self._write_manifest(manifest)

    def _write_manifest(self, manifest: dict) -> None:
        lines: list[str] = []
        for name, raw in manifest.get("compilations", {}).items():
            lines.append(f"[compilations.{name}]")
            lines.append(f'lesson = "{raw["lesson"]}"')
            scenes_repr = ", ".join(f'"{scene_id}"' for scene_id in raw["scenes"])
            lines.append(f"scenes = [{scenes_repr}]")
            lines.append(f'output = "{raw["output"]}"')
            lines.append("")
        self._manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self._manifest_path.write_text("\n".join(lines) + ("\n" if lines else ""))


registry = CompilationRegistry()
