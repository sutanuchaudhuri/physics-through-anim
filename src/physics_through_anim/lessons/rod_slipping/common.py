"""Reusable geometry, forces, graphs, and layout helpers for the Rod Slipping
lesson. Mirrors the conventions in rolling_slipping/common.py (see
.github/skills/physics-animation-standards/SKILL.md) applied to a rod instead
of a wheel.
"""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from manim import (
    BLUE,
    DOWN,
    GRAY,
    GREEN,
    LEFT,
    ORANGE,
    PURPLE,
    RED,
    RIGHT,
    TEAL,
    UP,
    WHITE,
    YELLOW,
    Arrow,
    Axes,
    Dot,
    Line,
    MathTex,
    MovingCameraScene,
    RoundedRectangle,
    Text,
    VGroup,
    config,
)

from physics_through_anim.lessons.rod_slipping.simulation import (
    LENGTH,
    TABLE_HEIGHT,
    S,
    Trajectory,
    get_trajectory,
)
from physics_through_anim.scene_logging import SceneEventLogMixin

DEFAULT_FRAME_WIDTH = config.frame_width

COLOR_NORMAL = GREEN
COLOR_FRICTION = ORANGE
COLOR_WEIGHT = PURPLE
COLOR_VELOCITY = BLUE
COLOR_ANGULAR = TEAL
COLOR_ACCEL = "#FF2D95"
COLOR_ANGULAR_ACCEL = "#C77DFF"

FOOT_ORIGIN = np.array([0.0, -1.0, 0.0])  # table top drawn at y=-1.0 on screen


class RodLessonScene(SceneEventLogMixin, MovingCameraScene):
    """Shared base: local narration playback + camera zoom, matching
    RollingLessonScene's contract in the rolling_slipping lesson."""

    LESSON_NAME = "rod_slipping"

    def add_narration(self) -> None:
        narration_file = os.environ.get("PHYSICS_NARRATION_FILE")
        if narration_file and Path(narration_file).exists():
            self.add_sound(narration_file)

    def finish_with_narration(self, min_tail: float = 0.75) -> None:
        """Hold the final frame until the narration ends (see SKILL.md Rule 18)."""
        from physics_through_anim.narration import hold_for_narration

        hold_for_narration(self, min_tail=min_tail)

    def zoom_to(self, point, width: float = 2.4, run_time: float = 1.6) -> None:
        self.play(self.camera.frame.animate.move_to(point).set(width=width), run_time=run_time)

    def zoom_out(self, run_time: float = 2.0) -> None:
        self.play(
            self.camera.frame.animate.move_to([0, 0, 0]).set(width=DEFAULT_FRAME_WIDTH),
            run_time=run_time,
        )

    def scene_header(self, scene_id: str, heading: str, subtitle: str) -> VGroup:
        label = Text(f"Scene {scene_id}", font_size=16, color=GRAY).to_corner(UP + LEFT, buff=0.3)
        title = Text(heading, font_size=30, weight="BOLD").to_edge(UP, buff=0.25)
        sub = Text(subtitle, font_size=18, color=ORANGE).next_to(title, DOWN, buff=0.08)
        return VGroup(label, title, sub)

    def chapter_banner(self, number: str, name: str) -> VGroup:
        roman = Text(f"CHAPTER {number}", font_size=28, color=GRAY, weight="BOLD")
        heading = Text(name, font_size=36, weight="BOLD").next_to(roman, DOWN, buff=0.3)
        return VGroup(roman, heading)

    def play_subscenes(self, subscenes, mode="sequential", **kwargs):
        """Play a list of SubScene segments sequentially or together.
        See physics_through_anim.subscenes.play_subscenes for options."""
        from physics_through_anim.subscenes import play_subscenes

        return play_subscenes(self, subscenes, mode, **kwargs)


def table(half_width: float = 4.0, y: float = -1.0) -> VGroup:
    top = Line([-half_width, y, 0], [half_width, y, 0], color=GRAY, stroke_width=6)
    side = Line([half_width, y, 0], [half_width, y - TABLE_HEIGHT * 0.35, 0], color=GRAY, stroke_width=6)
    ticks = VGroup(
        *[
            Line([x, y, 0], [x - 0.12, y - 0.12, 0], color=GRAY, stroke_width=2)
            for x in np.linspace(-half_width, half_width, 14)
        ]
    )
    return VGroup(top, side, ticks)


def rod_at(theta: float, x_foot: float = 0.0, y_foot: float = -1.0, color=BLUE) -> VGroup:
    """Draw the rod at angle theta (from vertical) with its foot at (x_foot, y_foot)."""
    foot = np.array([x_foot, y_foot, 0.0])
    tip = foot + LENGTH * np.array([np.sin(theta), np.cos(theta), 0.0])
    body = Line(foot, tip, color=color, stroke_width=8)
    foot_dot = Dot(foot, color=RED, radius=0.08)
    cm = foot + S * np.array([np.sin(theta), np.cos(theta), 0.0])
    cm_dot = Dot(cm, color=YELLOW, radius=0.06)
    group = VGroup(body, foot_dot, cm_dot)
    group.foot = foot
    group.tip = tip
    group.cm = cm
    return group


def force_arrow(start, end, label: str, color=COLOR_FRICTION) -> VGroup:
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)
    arrow = Arrow(start, end, buff=0, color=color, stroke_width=6)
    direction = RIGHT if end[0] >= start[0] else LEFT
    text = MathTex(label, color=color).next_to(arrow, direction, buff=0.12)
    return VGroup(arrow, text)


def misconception_card(text: str) -> VGroup:
    box = RoundedRectangle(width=10.5, height=0.95, color=RED, corner_radius=0.15)
    label = Text("MISCONCEPTION", font_size=18, color=RED, weight="BOLD").next_to(
        box, UP, buff=0.08
    )
    body = Text(text, font_size=22, color=WHITE)
    if body.width > box.width - 0.6:
        body.scale_to_fit_width(box.width - 0.6)
    body.move_to(box.get_center())
    return VGroup(box, label, body)


def correction_card(text: str) -> VGroup:
    box = RoundedRectangle(width=10.5, height=0.95, color=GREEN, corner_radius=0.15)
    label = Text("CORRECTION", font_size=18, color=GREEN, weight="BOLD").next_to(box, UP, buff=0.08)
    body = Text(text, font_size=22, color=WHITE)
    if body.width > box.width - 0.6:
        body.scale_to_fit_width(box.width - 0.6)
    body.move_to(box.get_center())
    return VGroup(box, label, body)


def quadrant_anchors(spread: float = 3.2) -> dict[str, np.ndarray]:
    return {
        "top_left": np.array([-spread, 1.4, 0.0]),
        "top_right": np.array([spread, 1.4, 0.0]),
        "bottom_left": np.array([-spread, -1.4, 0.0]),
        "bottom_right": np.array([spread, -1.4, 0.0]),
    }


def trajectory() -> Trajectory:
    return get_trajectory()


def time_series_axes(
    x_range, y_range, x_label: str, y_label: str, width: float = 5.0, height: float = 2.6
) -> VGroup:
    axes = Axes(
        x_range=x_range,
        y_range=y_range,
        x_length=width,
        y_length=height,
        axis_config={"color": GRAY, "stroke_width": 2, "include_tip": False},
    )
    labels = axes.get_axis_labels(MathTex(x_label, font_size=24), MathTex(y_label, font_size=24))
    return VGroup(axes, labels)
