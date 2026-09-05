#!/usr/bin/env python3
"""Command line entry point for the offline physics video studio."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from physics_through_anim.lessons.compilation_registry import registry as compilation_registry
from physics_through_anim.lessons.lesson_registry import registry
from physics_through_anim.lessons.publish_registry import registry as publish_registry
from physics_through_anim.publish import complete_publication, prepare_publication
from physics_through_anim.registry import TOPICS
from physics_through_anim.render import (
    compile_video,
    render_lesson_scene,
    render_topic,
    stitch_compilation,
    stitch_lesson,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Plan and render short, narrated physics lessons with Manim."
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List the planned topics and scene names.")

    render_parser = subparsers.add_parser("render", help="Render one topic to a video.")
    render_parser.add_argument("topic", choices=sorted(TOPICS))
    render_parser.add_argument("--quality", choices=("low", "medium", "high"), default="low")
    render_parser.add_argument("--narration", choices=("off", "auto", "required"), default="auto")

    rolling_parser = subparsers.add_parser(
        "render-rolling",
        help="Render one scene, one chapter, or all of the rolling/slipping lesson.",
    )
    rolling_parser.add_argument("scene", choices=registry.get("rolling_slipping").scene_choices())
    rolling_parser.add_argument("--quality", choices=("low", "medium", "high"), default="low")
    rolling_parser.add_argument("--narration", choices=("off", "auto", "required"), default="auto")

    stitch_parser = subparsers.add_parser(
        "stitch-rolling", help="Concatenate all rendered scenes into one final video."
    )
    stitch_parser.add_argument("--quality", choices=("low", "medium", "high"), default="low")

    rod_parser = subparsers.add_parser(
        "render-rod",
        help="Render one scene, one chapter, or all of the rod-slipping lesson.",
    )
    rod_parser.add_argument("scene", choices=registry.get("rod_slipping").scene_choices())
    rod_parser.add_argument("--quality", choices=("low", "medium", "high"), default="low")
    rod_parser.add_argument("--narration", choices=("off", "auto", "required"), default="auto")

    stitch_rod_parser = subparsers.add_parser(
        "stitch-rod", help="Concatenate all rendered rod-slipping scenes into one final video."
    )
    stitch_rod_parser.add_argument("--quality", choices=("low", "medium", "high"), default="low")

    lesson_parser = subparsers.add_parser(
        "render-lesson",
        help="Render one scene, one chapter, or all scenes of any lesson in lessons.toml.",
    )
    lesson_parser.add_argument("lesson", choices=registry.all_lesson_names())
    lesson_parser.add_argument("scene")
    lesson_parser.add_argument("--quality", choices=("low", "medium", "high"), default="low")
    lesson_parser.add_argument("--narration", choices=("off", "auto", "required"), default="auto")

    stitch_lesson_parser = subparsers.add_parser(
        "stitch-lesson",
        help="Concatenate all rendered scenes of any lesson in lessons.toml into one video.",
    )
    stitch_lesson_parser.add_argument("lesson", choices=registry.all_lesson_names())
    stitch_lesson_parser.add_argument("--quality", choices=("low", "medium", "high"), default="low")

    compile_parser = subparsers.add_parser(
        "compile",
        help=(
            "Define and build a named, arbitrary-order video from a lesson's scenes "
            "(ranges, inserts, removals, overlapping groups all supported)."
        ),
    )
    compile_parser.add_argument("lesson", choices=registry.all_lesson_names())
    compile_parser.add_argument(
        "scenes",
        help='"all", a range like "01-10", or a comma list like "01-12,21,13-44".',
    )
    compile_parser.add_argument("--name", required=True, help="Name for this compilation.")
    compile_parser.add_argument(
        "--output", default=None, help="Output filename (default <name>.mp4)."
    )
    compile_parser.add_argument("--quality", choices=("low", "medium", "high"), default="low")
    compile_parser.add_argument("--narration", choices=("off", "auto", "required"), default="auto")

    stitch_compilation_parser = subparsers.add_parser(
        "stitch-compilation", help="Rebuild an already-defined compilation from compilations.toml."
    )
    stitch_compilation_parser.add_argument("name", choices=compilation_registry.all_names() or None)
    stitch_compilation_parser.add_argument(
        "--quality", choices=("low", "medium", "high"), default="low"
    )
    stitch_compilation_parser.add_argument(
        "--narration", choices=("off", "auto", "required"), default="off"
    )

    subparsers.add_parser(
        "list-compilations", help="List all defined compilations and their scenes."
    )

    publish_prepare_parser = subparsers.add_parser(
        "publish-prepare",
        help=(
            "Resolve a source video and persist a pending publish record "
            "(does not upload anything -- see the video-publishing skill)."
        ),
    )
    publish_prepare_parser.add_argument(
        "source",
        help="lesson:<name>, compilation:<name>, scene:<lesson>:<id>, or a bare file path.",
    )
    publish_prepare_parser.add_argument("--title", required=True)
    publish_prepare_parser.add_argument("--description", required=True)
    publish_prepare_parser.add_argument("--platform", default="youtube")
    publish_prepare_parser.add_argument("--tags", default="", help="Comma-separated tags.")
    publish_prepare_parser.add_argument(
        "--visibility", choices=("private", "unlisted", "public"), default="unlisted"
    )
    publish_prepare_parser.add_argument("--category", default="27", help="YouTube category id.")
    publish_prepare_parser.add_argument("--made-for-kids", action="store_true")
    publish_prepare_parser.add_argument("--playlist", default=None)
    publish_prepare_parser.add_argument("--thumbnail", default=None)
    publish_prepare_parser.add_argument(
        "--slug", default=None, help="Defaults to a slug of --title."
    )
    publish_prepare_parser.add_argument(
        "--quality", choices=("low", "medium", "high"), default="high"
    )

    publish_complete_parser = subparsers.add_parser(
        "publish-complete", help="Record a completed upload's returned video id/URL."
    )
    publish_complete_parser.add_argument("slug", choices=publish_registry.all_slugs() or None)
    publish_complete_parser.add_argument("--video-id", required=True)
    publish_complete_parser.add_argument("--url", required=True)

    subparsers.add_parser("list-publications", help="List all publish records and their status.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "list":
        for slug, topic in TOPICS.items():
            print(f"{slug:20} {topic.title} -> {topic.scene_name}")
        return 0
    if args.command == "render":
        return render_topic(args.topic, args.quality, args.narration)
    if args.command == "render-rolling":
        return render_lesson_scene("rolling_slipping", args.scene, args.quality, args.narration)
    if args.command == "stitch-rolling":
        return stitch_lesson("rolling_slipping", args.quality)
    if args.command == "render-rod":
        return render_lesson_scene("rod_slipping", args.scene, args.quality, args.narration)
    if args.command == "stitch-rod":
        return stitch_lesson("rod_slipping", args.quality)
    if args.command == "render-lesson":
        return render_lesson_scene(args.lesson, args.scene, args.quality, args.narration)
    if args.command == "stitch-lesson":
        return stitch_lesson(args.lesson, args.quality)
    if args.command == "compile":
        return compile_video(
            args.name, args.lesson, args.scenes, args.quality, args.narration, args.output
        )
    if args.command == "stitch-compilation":
        return stitch_compilation(args.name, args.quality, args.narration)
    if args.command == "list-compilations":
        for name in compilation_registry.all_names():
            comp = compilation_registry.get(name)
            print(
                f"{name:20} lesson={comp.lesson:20} "
                f"output={comp.output:30} scenes={comp.scene_ids}"
            )
        return 0
    if args.command == "publish-prepare":
        tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
        publication = prepare_publication(
            args.source,
            args.title,
            args.description,
            platform=args.platform,
            tags=tags,
            visibility=args.visibility,
            category=args.category,
            made_for_kids=args.made_for_kids,
            playlist=args.playlist,
            thumbnail=args.thumbnail,
            slug=args.slug,
            quality=args.quality,
        )
        print(f"Prepared publication '{publication.slug}': {publication.file}")
        print("Hand this file + metadata to the agent to upload via an MCP tool, then run:")
        print(f"  python main.py publish-complete {publication.slug} --video-id ... --url ...")
        return 0
    if args.command == "publish-complete":
        publication = complete_publication(args.slug, args.video_id, args.url)
        print(f"Marked '{publication.slug}' published: {publication.url}")
        return 0
    if args.command == "list-publications":
        for slug in publish_registry.all_slugs():
            pub = publish_registry.get(slug)
            print(f"{slug:20} status={pub.status:10} platform={pub.platform:10} url={pub.url}")
        return 0
    build_parser().print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
