"""Apply the shared style layer to Manim mobjects and assemble a scene group.

``build_manim_group`` turns a plan into a styled Manim ``VGroup`` (assembly +
markers/vectors/paths) in world coordinates -- constructing mobjects only, so it
is testable without rendering a frame. The ``manim`` engine renders that group.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import radians

import numpy as np
from manim import Arrow, Dot, Text, VGroup, VMobject

from physics_through_anim.physics.problems.scene_plan import ProblemScenePlan
from physics_through_anim.physics.rendering.manim_masks import build_manim_mask
from physics_through_anim.physics.rendering.style import ResolvedStyle, resolve_style
from physics_through_anim.physics.serialization.assembly_io import plan_to_assembly

__all__ = ["apply_style", "build_manim_group", "Motion", "resolve_step_motions"]


def _resolve_mask_anchor(mask, assembly) -> tuple[float, float] | None:
    """Resolve a MaskSpec to its world anchor (``at`` ref, ``point``, or ``points[0]``)."""
    if mask.at:
        try:
            p = assembly.resolve(mask.at)
        except KeyError:
            return None
        return (float(p[0]), float(p[1]))
    if mask.point is not None:
        return (float(mask.point[0]), float(mask.point[1]))
    if mask.points:
        return (float(mask.points[0][0]), float(mask.points[0][1]))
    return None

_ROLE_COLORS = {
    "velocity": "#4dabf7", "acceleration": "#ff2d95", "angular": "#20c997",
    "force": "#ffd43b", "weight": "#e64980", "normal": "#51cf66",
    "friction": "#ffa94d", "tension": "#0ca678", "momentum": "#845ef7",
    "position": "#ffd43b", "radius": "#ff922b",
}


def apply_style(mobject: VMobject, style: ResolvedStyle) -> VMobject:
    """Apply resolved opacities/dash to a Manim mobject (best-effort)."""
    mobject.set_stroke(opacity=style.stroke_opacity)
    if not style.hashed:
        mobject.set_fill(opacity=style.fill_opacity)
    return mobject


def _world(point) -> np.ndarray:
    return np.array([float(point[0]), float(point[1]), 0.0])


def build_manim_group(plan: ProblemScenePlan):
    """Return ``(group, assembly)``: a styled Manim ``VGroup`` for the whole plan."""
    assembly = plan_to_assembly(plan)
    styles = {e.name: resolve_style(e.style) for e in plan.entities}
    group = VGroup()
    for mask in plan.masks:  # cosmetic overlays sit on the bottom layer
        anchor = _resolve_mask_anchor(mask, assembly)
        if anchor is not None:
            mobject = build_manim_mask(mask, anchor)
            if mobject is not None:
                group.add(mobject)
    for member in assembly.members:
        apply_style(member.mobject, styles.get(member.name, ResolvedStyle()))
        group.add(member.mobject)

    for path in plan.paths:
        if len(path.points) >= 2:
            curve = VMobject(color=path.color, stroke_width=2)
            curve.set_points_as_corners([_world(p) for p in path.points])
            group.add(curve)

    for vec in plan.vectors:
        if not vec.anchor or vec.vector is None:
            continue
        try:
            base = _world(assembly.resolve(vec.anchor))
        except KeyError:
            continue
        tip = base + _world(vec.vector)
        group.add(Arrow(base, tip, buff=0.0, color=_ROLE_COLORS.get(vec.role, "#ffd43b")))

    for marker in plan.markers:
        point = None
        if marker.at:
            try:
                point = _world(assembly.resolve(marker.at))
            except KeyError:
                point = None
        elif marker.point is not None:
            point = _world(marker.point)
        if point is not None:
            group.add(Dot(point, color=marker.color or "#ff4444", radius=0.08))
            if marker.label:
                group.add(Text(marker.label, font_size=18,
                               color=marker.color or "#ff4444").next_to(point, np.array([0, 1, 0])))
    return group, assembly


@dataclass
class Motion:
    """One entity's vector-driven motion within a timestep."""

    mobject: object
    run_time: float
    shift: tuple[float, float] | None = None
    angle_rad: float = 0.0
    pivot: np.ndarray | None = None


def resolve_step_motions(plan: ProblemScenePlan, assembly) -> list[list[Motion]]:
    """Resolve each timestep's ``TransformSpec``s to concrete ``Motion``s (in ``at`` order).

    Steps with no transforms yield an empty list (a hold). Rotation carries the
    body along its arc about ``about`` (a keypoint pivot) or its own centre.
    """
    name_to_mobject = {member.name: member.mobject for member in assembly.members}
    timeline: list[list[Motion]] = []
    for step in sorted(plan.steps, key=lambda s: s.at):
        motions: list[Motion] = []
        run_time = step.dt or 1.0
        for tf in step.transforms:
            mobject = name_to_mobject.get(tf.target)
            if mobject is None:
                continue
            pivot = None
            if tf.about:
                try:
                    p = assembly.resolve(tf.about)
                    pivot = np.array([float(p[0]), float(p[1]), 0.0])
                except KeyError:
                    pivot = None
            motions.append(Motion(
                mobject=mobject, run_time=run_time,
                shift=tuple(tf.translate) if tf.translate else None,
                angle_rad=radians(tf.rotate_deg), pivot=pivot))
        timeline.append(motions)
    return timeline
