"""Resolve a publish source to a file, and manage the prepare/complete workflow.

See `physics_through_anim.lessons.publish_registry` for why publishing is a
two-actor (script + agent) workflow: this module implements the scriptable
halves (`prepare_publication`, `complete_publication`); the actual upload call
to a YouTube (or other platform) MCP tool is made by the agent, not from here.
"""

from __future__ import annotations

import re
from pathlib import Path

from physics_through_anim.lessons.compilation_registry import registry as compilation_registry
from physics_through_anim.lessons.lesson_registry import registry as lesson_registry
from physics_through_anim.lessons.publish_registry import Publication
from physics_through_anim.lessons.publish_registry import registry as publish_registry
from physics_through_anim.render import QUALITY_RESOLUTIONS, ROOT, _clip_path

VALID_VISIBILITIES = ("private", "unlisted", "public")


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "video"


def resolve_source(source: str, quality: str = "high") -> tuple[Path, str]:
    """Resolve a source string to (file_path, human-readable source label).

    Accepted forms:
      - "lesson:<lesson_name>"            -> that lesson's final stitched video
      - "compilation:<name>"              -> that named compilation's output
      - "scene:<lesson_name>:<scene_id>"  -> one rendered scene clip
      - a bare path to an existing .mp4 file
    """
    if source.startswith("lesson:"):
        lesson_name = source.removeprefix("lesson:")
        lesson = lesson_registry.get(lesson_name)
        path = ROOT / "media" / "final" / lesson.final_output
        return path, f"lesson:{lesson_name}"
    if source.startswith("compilation:"):
        name = source.removeprefix("compilation:")
        compilation = compilation_registry.get(name)
        path = ROOT / "media" / "final" / compilation.output
        return path, f"compilation:{name}"
    if source.startswith("scene:"):
        _, lesson_name, scene_id = source.split(":", 2)
        lesson = lesson_registry.get(lesson_name)
        if scene_id not in lesson.scenes:
            raise KeyError(f"Unknown scene id '{scene_id}' for lesson '{lesson_name}'")
        entry = lesson.scenes[scene_id]
        resolution = QUALITY_RESOLUTIONS[quality]
        path = _clip_path(lesson_name, entry, resolution)
        return path, f"scene:{lesson_name}:{scene_id}"
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(
            f"'{source}' is not a lesson:/compilation:/scene: reference and no such file exists"
        )
    return path, source


def prepare_publication(
    source: str,
    title: str,
    description: str,
    platform: str = "youtube",
    tags: list[str] | None = None,
    visibility: str = "unlisted",
    category: str = "27",
    made_for_kids: bool = False,
    playlist: str | None = None,
    thumbnail: str | None = None,
    slug: str | None = None,
    quality: str = "high",
) -> Publication:
    """Resolve the source, validate the file exists, and persist a pending publish record.

    Does NOT upload anything -- the agent performs the actual upload via
    whichever MCP tool is configured, then calls `complete_publication`.
    """
    if visibility not in VALID_VISIBILITIES:
        raise ValueError(f"visibility must be one of {VALID_VISIBILITIES}, got '{visibility}'")
    path, source_label = resolve_source(source, quality)
    if not path.exists():
        raise FileNotFoundError(f"Resolved source file does not exist: {path}")
    publication = Publication(
        slug=slug or _slugify(title),
        source=source_label,
        file=str(path),
        platform=platform,
        title=title,
        description=description,
        tags=tags or [],
        visibility=visibility,
        category=category,
        made_for_kids=made_for_kids,
        playlist=playlist,
        thumbnail=thumbnail,
        status="pending",
    )
    publish_registry.save(publication)
    return publication


def complete_publication(slug: str, video_id: str, url: str) -> Publication:
    """Record a successful upload's returned id/URL and mark the record published."""
    publication = publish_registry.get(slug)
    updated = Publication(
        slug=publication.slug,
        source=publication.source,
        file=publication.file,
        platform=publication.platform,
        title=publication.title,
        description=publication.description,
        tags=publication.tags,
        visibility=publication.visibility,
        category=publication.category,
        made_for_kids=publication.made_for_kids,
        playlist=publication.playlist,
        thumbnail=publication.thumbnail,
        status="published",
        video_id=video_id,
        url=url,
    )
    publish_registry.save(updated)
    return updated
