"""Registry for tracking video publications (e.g. to YouTube) to/via an MCP server.

This repo's `main.py`/`render.py` can only run local subprocesses (manim,
ffmpeg) -- they cannot call an MCP tool themselves, only the agent driving a
conversation can. So publishing is a three-step, two-actor workflow:

1. ``prepare_publication`` (scriptable): resolve a source (a lesson's final
   video, a named compilation, or one scene clip) to an actual file path,
   draft/validate metadata, and persist a ``status = "pending"`` record here.
2. The agent calls whichever YouTube-upload MCP tool is registered (found via
   ``tool_search`` at the time -- there is no fixed tool name, since it
   depends on which MCP server the user has configured) with the prepared
   file path and metadata.
3. ``complete_publication`` (scriptable): record the returned video id/URL and
   flip the record to ``status = "published"``.

Definitions live in ``lessons/publications.toml``, in the same read/write
TOML-registry style as ``compilation_registry.py``.

Field names here are our own tracking schema, not a 1:1 passthrough of any
one MCP server's API -- but they're chosen to map cleanly onto
``youtube-uploader-mcp`` (github.com/anwerj/youtube-uploader-mcp)'s
``upload_video``/``update_video`` tools specifically: ``visibility`` maps to
that tool's ``status`` parameter (public/private/unlisted); ``category``/
``made_for_kids`` are passed straight through to ``upload_video``;
``playlist``/``thumbnail`` are passed to the separate ``update_video`` tool
after upload. Our own ``status`` field ("pending"/"published") is a
different concept: it tracks *our* workflow state, not YouTube's privacy
status.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

PUBLICATIONS_DIR = Path(__file__).resolve().parent
MANIFEST_PATH = PUBLICATIONS_DIR / "publications.toml"


@dataclass(frozen=True)
class Publication:
    """One video's publish record, pending or completed."""

    slug: str
    source: str
    file: str
    platform: str
    title: str
    description: str
    tags: list[str] = field(default_factory=list)
    visibility: str = "unlisted"
    category: str = "27"  # YouTube category id; 27 = Education
    made_for_kids: bool = False
    playlist: str | None = None
    thumbnail: str | None = None
    status: str = "pending"
    video_id: str | None = None
    url: str | None = None


class PublishRegistry:
    """Reads and writes publish records in `publications.toml`."""

    def __init__(self, manifest_path: Path = MANIFEST_PATH):
        self._manifest_path = manifest_path

    def _load_manifest(self) -> dict:
        if not self._manifest_path.exists():
            return {"publications": {}}
        with self._manifest_path.open("rb") as handle:
            return tomllib.load(handle)

    def all_slugs(self) -> list[str]:
        return list(self._load_manifest().get("publications", {}))

    def get(self, slug: str) -> Publication:
        manifest = self._load_manifest()
        try:
            raw = manifest["publications"][slug]
        except KeyError as exc:
            raise KeyError(f"Unknown publication '{slug}' in {self._manifest_path}") from exc
        return Publication(
            slug=slug,
            source=raw["source"],
            file=raw["file"],
            platform=raw["platform"],
            title=raw["title"],
            description=raw["description"],
            tags=list(raw.get("tags", [])),
            visibility=raw.get("visibility", "unlisted"),
            category=raw.get("category", "27"),
            made_for_kids=raw.get("made_for_kids", False),
            playlist=raw.get("playlist") or None,
            thumbnail=raw.get("thumbnail") or None,
            status=raw.get("status", "pending"),
            video_id=raw.get("video_id"),
            url=raw.get("url"),
        )

    def save(self, publication: Publication) -> None:
        """Persist (create, or overwrite in place) one publish record."""
        manifest = self._load_manifest()
        publications = manifest.setdefault("publications", {})
        publications[publication.slug] = {
            "source": publication.source,
            "file": publication.file,
            "platform": publication.platform,
            "title": publication.title,
            "description": publication.description,
            "tags": publication.tags,
            "visibility": publication.visibility,
            "category": publication.category,
            "made_for_kids": publication.made_for_kids,
            "playlist": publication.playlist or "",
            "thumbnail": publication.thumbnail or "",
            "status": publication.status,
            "video_id": publication.video_id or "",
            "url": publication.url or "",
        }
        self._write_manifest(manifest)

    def _write_manifest(self, manifest: dict) -> None:
        lines: list[str] = []
        for slug, raw in manifest.get("publications", {}).items():
            lines.append(f"[publications.{slug}]")
            lines.append(f'source = "{raw["source"]}"')
            lines.append(f'file = "{raw["file"]}"')
            lines.append(f'platform = "{raw["platform"]}"')
            lines.append(f'title = "{_escape(raw["title"])}"')
            lines.append(f'description = "{_escape(raw["description"])}"')
            tags_repr = ", ".join(f'"{tag}"' for tag in raw["tags"])
            lines.append(f"tags = [{tags_repr}]")
            lines.append(f'visibility = "{raw["visibility"]}"')
            lines.append(f'category = "{raw["category"]}"')
            made_for_kids = str(raw["made_for_kids"]).lower()
            lines.append(f"made_for_kids = {made_for_kids}")
            lines.append(f'playlist = "{raw["playlist"]}"')
            lines.append(f'thumbnail = "{raw["thumbnail"]}"')
            lines.append(f'status = "{raw["status"]}"')
            lines.append(f'video_id = "{raw["video_id"]}"')
            lines.append(f'url = "{raw["url"]}"')
            lines.append("")
        self._manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self._manifest_path.write_text("\n".join(lines) + ("\n" if lines else ""))


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


registry = PublishRegistry()
