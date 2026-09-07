"""Scaffolded render engines. Manim is the prime (video) engine; the snapshot
back-ends (matplotlib/plotly/pymunk) are stubs that raise until wired.

Each declares its capabilities and, where a third-party backend is needed, checks
that it is importable so the error explains what to install.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

from physics_through_anim.physics.problems.scene_plan import ProblemScenePlan
from physics_through_anim.physics.rendering.base import Renderer, register


def _require(module: str, extra: str) -> None:
    if importlib.util.find_spec(module) is None:
        raise NotImplementedError(
            f"The {module!r} backend is not installed. Install it with "
            f"`pip install physics-through-anim[{extra}]` (or `pip install {module}`)."
        )


@register
class ManimRenderer(Renderer):
    """Prime engine: a transform/vector-driven Manim animation (or a still frame)."""

    name = "manim"
    kind = "video"
    default_suffix = ".png"

    def render(self, plan: ProblemScenePlan, output: Path) -> Path:
        import shutil

        from manim import Rotate, Scene, tempconfig

        from physics_through_anim.physics.rendering.manim_style import (
            build_manim_group,
            resolve_step_motions,
        )

        group, assembly = build_manim_group(plan)
        timeline = resolve_step_motions(plan, assembly)
        animated = any(motions for motions in timeline)
        output = Path(output)
        if animated and output.suffix.lower() == ".png":
            output = output.with_suffix(".mp4")

        class _PlanScene(Scene):
            def construct(scene) -> None:  # noqa: N805
                scene.add(group)
                for motions in timeline:
                    if not motions:
                        scene.wait(0.5)
                        continue
                    anims = []
                    for motion in motions:
                        if motion.angle_rad:
                            pivot = (motion.pivot if motion.pivot is not None
                                     else motion.mobject.get_center())
                            anims.append(Rotate(motion.mobject, motion.angle_rad,
                                                about_point=pivot, run_time=motion.run_time))
                        elif motion.shift:
                            anims.append(motion.mobject.animate.shift(
                                [motion.shift[0], motion.shift[1], 0.0]))
                    scene.play(*anims, run_time=motions[0].run_time)

        media = output.parent / "_manim_media"
        with tempconfig({
            "save_last_frame": not animated, "write_to_movie": animated,
            "quality": "low_quality", "media_dir": str(media), "output_file": output.stem,
            "background_color": "#0f1117",
        }):
            _PlanScene().render()
        ext = output.suffix.lstrip(".")
        produced = next(media.rglob(f"{output.stem}.{ext}"), None)
        if produced is None:
            raise NotImplementedError("Manim did not produce output; use --renderer svg.")
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(produced, output)
        shutil.rmtree(media, ignore_errors=True)
        return output


@register
class MatplotlibRenderer(Renderer):
    """Static snapshot via matplotlib (scaffold; needs the `viz` extra)."""

    name = "matplotlib"
    kind = "snapshot"
    default_suffix = ".png"

    def render(self, plan: ProblemScenePlan, output: Path) -> Path:
        _require("matplotlib", "viz")
        raise NotImplementedError("The matplotlib snapshot engine is scaffolded.")


@register
class PlotlyRenderer(Renderer):
    """Interactive snapshot via plotly (scaffold; needs the `viz` extra)."""

    name = "plotly"
    kind = "snapshot"
    default_suffix = ".html"

    def render(self, plan: ProblemScenePlan, output: Path) -> Path:
        _require("plotly", "viz")
        raise NotImplementedError("The plotly snapshot engine is scaffolded.")


@register
class PymunkRenderer(Renderer):
    """Physics-stepped preview via pymunk (scaffold; pymunk already a dependency)."""

    name = "pymunk"
    kind = "snapshot"
    default_suffix = ".png"

    def render(self, plan: ProblemScenePlan, output: Path) -> Path:
        raise NotImplementedError("The pymunk preview engine is scaffolded.")
