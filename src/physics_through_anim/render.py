from __future__ import annotations

import os
import shutil
import subprocess
import wave
from pathlib import Path

from physics_through_anim.lessons.compilation_registry import Compilation
from physics_through_anim.lessons.compilation_registry import registry as compilation_registry
from physics_through_anim.lessons.lesson_registry import LessonConfig, registry
from physics_through_anim.registry import TOPICS

ROOT = Path(__file__).resolve().parents[2]
AUDIO_DIR = ROOT / "assets" / "audio"
LESSON_SCRIPT = ROOT / "src" / "physics_through_anim" / "lessons" / "foundations.py"
FINAL_DIR = ROOT / "media" / "final"
QUALITY_FLAGS = {"low": "l", "medium": "m", "high": "h"}
QUALITY_RESOLUTIONS = {"low": "480p15", "medium": "720p30", "high": "1080p60"}


def _ensure_video_dir_config(lesson: LessonConfig) -> Path:
    """Write a manim.cfg nesting this lesson's videos under media/videos/<lesson_name>/...

    Without this, manim's default `video_dir` template
    (`{media_dir}/videos/{module_name}/{quality}`) dumps every lesson's scenes
    into the same flat `media/videos/` folder. Regenerated on every render so
    it always matches the lesson's current name.
    """
    cfg_path = lesson.dir / "manim.cfg"
    content = (
        "[CLI]\n"
        f"video_dir = {{media_dir}}/videos/{lesson.name}/{{module_name}}/{{quality}}\n"
    )
    if not cfg_path.exists() or cfg_path.read_text() != content:
        cfg_path.write_text(content)
    return cfg_path


def _narration_text(markdown_path: Path) -> str:
    lines = markdown_path.read_text().splitlines()
    body = [line.strip() for line in lines if line.strip() and not line.lstrip().startswith("#")]
    return " ".join(body)


def _draft_audio(topic_slug: str, text: str) -> Path:
    destination = AUDIO_DIR / f"{topic_slug}.wav"
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return destination
    say = shutil.which("say")
    if say:
        subprocess.run([say, "-o", str(destination), "--data-format=LEI16@44100", text], check=True)
        return destination
    with wave.open(str(destination), "w") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(44100)
        audio.writeframes(b"\0\0" * 44100)
    return destination


def _clip_path(lesson_name: str, entry, resolution: str) -> Path:
    """Path to one rendered scene's clip, grouped under media/videos/<lesson_name>/..."""
    return (
        ROOT
        / "media"
        / "videos"
        / lesson_name
        / entry.module_stem
        / resolution
        / f"{entry.class_name}.mp4"
    )


def _concat(concat_list_name: str, clips: list[Path], output_path: Path) -> int:
    """Concatenate clips, in the given order, into output_path via ffmpeg (no re-encode)."""
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    concat_list = FINAL_DIR / concat_list_name
    concat_list.write_text("".join(f"file '{clip.resolve()}'\n" for clip in clips))
    command = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_list),
        "-c",
        "copy",
        str(output_path),
    ]
    completed = subprocess.run(command, cwd=ROOT)
    return completed.returncode


def parse_scene_list(lesson: LessonConfig, selector: str) -> list[str]:
    """Parse a flexible, order-preserving scene selector into an explicit scene id list.

    ``selector`` is "all", or a comma-separated list of tokens where each token
    is either a single scene id ("07") or an inclusive numeric range
    ("01-10", re-zero-padded to match the lesson's id width). Tokens are kept
    in exactly the order given and may repeat or go out of numeric order --
    this is what lets a scene be spliced in out of place, e.g.
    "01-12,21,13-44" inserts scene 21 between scenes 12 and 13, and
    "01-10" followed elsewhere by a separate "06-11" selector are simply two
    different, independently valid scene lists (overlap is allowed).
    """
    if selector == "all":
        return list(lesson.scenes)
    width = len(next(iter(lesson.scenes))) if lesson.scenes else 2
    scene_ids: list[str] = []
    for raw_token in selector.split(","):
        token = raw_token.strip()
        if token in lesson.scenes:
            scene_ids.append(token)
            continue
        if "-" in token:
            start_str, end_str = token.split("-", 1)
            start, end = int(start_str), int(end_str)
            step = 1 if end >= start else -1
            scene_ids.extend(str(n).zfill(width) for n in range(start, end + step, step))
        else:
            scene_ids.append(token)
    unknown = [scene_id for scene_id in scene_ids if scene_id not in lesson.scenes]
    if unknown:
        raise KeyError(f"Unknown scene ids for lesson '{lesson.name}': {unknown}")
    return scene_ids


def build_compilation(
    name: str, lesson_name: str, scene_ids: list[str], output: str, quality: str, narration: str
) -> int:
    """Render any missing scenes, then concatenate exactly the given scene ids, in that
    exact order, into media/final/<output>. Order/repeats/gaps are the caller's choice --
    this does not assume the lesson's own scene order."""
    lesson = registry.get(lesson_name)
    resolution = QUALITY_RESOLUTIONS[quality]
    clips: list[Path] = []
    for scene_id in scene_ids:
        if scene_id not in lesson.scenes:
            raise KeyError(f"Unknown scene id '{scene_id}' for lesson '{lesson_name}'")
        entry = lesson.scenes[scene_id]
        clip = _clip_path(lesson_name, entry, resolution)
        if not clip.exists():
            completed = render_lesson_scene(lesson_name, scene_id, quality, narration)
            if completed != 0:
                return completed
        if not clip.exists():
            raise FileNotFoundError(f"Scene '{scene_id}' still missing after render: {clip}")
        clips.append(clip)
    return _concat(f"compilation_{name}_concat_list.txt", clips, FINAL_DIR / output)


def compile_video(
    name: str,
    lesson_name: str,
    selector: str,
    quality: str,
    narration: str,
    output: str | None = None,
) -> int:
    """Define (persisting to compilations.toml) and build a named scene compilation.

    Re-running this with a different ``selector`` for the same ``name``
    overwrites that compilation's definition in place -- this is how a
    reorder, an inserted scene, or a removed scene gets "recreated" in the
    registry rather than left as a one-off, forgotten ffmpeg run.
    """
    lesson = registry.get(lesson_name)
    scene_ids = parse_scene_list(lesson, selector)
    output_name = output or f"{name}.mp4"
    compilation_registry.save(
        Compilation(name=name, lesson=lesson_name, scene_ids=scene_ids, output=output_name)
    )
    return build_compilation(name, lesson_name, scene_ids, output_name, quality, narration)


def stitch_compilation(name: str, quality: str, narration: str = "off") -> int:
    """Rebuild an already-defined compilation (e.g. after re-rendering one of its scenes)."""
    compilation = compilation_registry.get(name)
    return build_compilation(
        compilation.name,
        compilation.lesson,
        compilation.scene_ids,
        compilation.output,
        quality,
        narration,
    )


def render_topic(topic_slug: str, quality: str, narration: str) -> int:
    topic = TOPICS[topic_slug]
    environment = os.environ.copy()
    if narration == "required":
        audio_file = AUDIO_DIR / f"{topic_slug}.wav"
        if not audio_file.exists():
            raise FileNotFoundError(f"Reviewed narration is required: {audio_file}")
    elif narration == "auto":
        audio_file = _draft_audio(topic_slug, topic.narration)
    else:
        audio_file = None
    if audio_file:
        environment["PHYSICS_NARRATION_FILE"] = str(audio_file)
    command = [
        "manim",
        "render",
        "-p",
        f"-q{QUALITY_FLAGS[quality]}",
        str(LESSON_SCRIPT),
        topic.scene_name,
    ]
    completed = subprocess.run(command, cwd=ROOT, env=environment)
    return completed.returncode


def render_lesson_scene(lesson_name: str, selector: str, quality: str, narration: str) -> int:
    """Render one scene, one chapter, or every scene ("all") of the given lesson."""
    lesson = registry.get(lesson_name)
    config_file = _ensure_video_dir_config(lesson)
    scene_ids = lesson.resolve_scene_ids(selector)
    unknown = [scene_id for scene_id in scene_ids if scene_id not in lesson.scenes]
    if unknown:
        raise KeyError(
            f"'{selector}' is not a valid scene, chapter, or 'all' for lesson '{lesson_name}'. "
            f"Valid selectors: {lesson.scene_choices()}"
        )
    for scene_id in scene_ids:
        entry = lesson.scenes[scene_id]
        environment = os.environ.copy()
        audio_file = AUDIO_DIR / lesson.audio_subdir / f"{entry.narration}.wav"
        narration_file = lesson.dir / "narration" / f"{entry.narration}.md"
        if narration == "required" and not audio_file.exists():
            raise FileNotFoundError(f"Reviewed narration is required: {audio_file}")
        if narration == "auto":
            audio_file = _draft_audio(
                f"{lesson.audio_subdir}/{entry.narration}", _narration_text(narration_file)
            )
        if narration != "off":
            environment["PHYSICS_NARRATION_FILE"] = str(audio_file)
        command = [
            "manim",
            "render",
            "-p",
            "-c",
            str(config_file),
            f"-q{QUALITY_FLAGS[quality]}",
            str(lesson.dir / entry.file),
            entry.class_name,
        ]
        completed = subprocess.run(command, cwd=ROOT, env=environment)
        if completed.returncode != 0:
            return completed.returncode
    return 0


def stitch_lesson(lesson_name: str, quality: str, output_name: str | None = None) -> int:
    """Concatenate every rendered scene of the given lesson, in scene order, into one video."""
    lesson = registry.get(lesson_name)
    resolution = QUALITY_RESOLUTIONS[quality]
    clips: list[Path] = []
    missing: list[str] = []
    for scene_id, entry in lesson.scenes.items():
        clip = _clip_path(lesson_name, entry, resolution)
        if clip.exists():
            clips.append(clip)
        else:
            missing.append(scene_id)
    if missing:
        raise FileNotFoundError(f"Missing rendered scenes at {resolution}: {', '.join(missing)}")
    output_path = FINAL_DIR / (output_name or lesson.final_output)
    return _concat(f"{lesson_name}_concat_list.txt", clips, output_path)

