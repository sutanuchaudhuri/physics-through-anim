"""Reusable geometry, forces, camera zoom, and layout helpers for the
Rolling, Slipping and Friction lesson (see plans/rolling_slipping_concepts_misconcepts.md).

Layout contract (avoids the panel-overlap bugs from the previous version):
- Title band:        y in [2.9, 3.8]   -> `scene_header()`
- Main visual band:   y in [-2.0, 2.6]  -> wheels, blocks, force arrows
- Ground line:        y = GROUND_Y = -2.0, objects are placed *tangent* to it
- Bottom band:        y in [-3.8, -2.4] -> equations, misconception/correction cards
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
    Arc,
    Arrow,
    Circle,
    Dot,
    DoubleArrow,
    FadeIn,
    FadeOut,
    Line,
    MathTex,
    MovingCameraScene,
    Rectangle,
    RoundedRectangle,
    SVGMobject,
    Text,
    ValueTracker,
    VGroup,
    Write,
    config,
    linear,
)

from physics_through_anim.scene_logging import SceneEventLogMixin

GROUND_Y = -2.0
BOTTOM_BAND_Y = -3.3
# Captured once at import time: camera.frame_width changes after zooming, so
# zoom_out() must restore to this fixed value, not to the (already-zoomed) current one.
DEFAULT_FRAME_WIDTH = config.frame_width
ICONS_DIR = Path(__file__).resolve().parents[4] / "assets" / "icons"

# FBD (force) vectors -- sharp, warm/cool distinct colors, one per force type.
COLOR_APPLIED = YELLOW
COLOR_FRICTION = ORANGE
COLOR_NORMAL = GREEN
COLOR_WEIGHT = PURPLE

# Kinematic vectors -- a completely separate palette from the forces above,
# so a force diagram and a kinematics diagram are never visually confusable.
COLOR_VELOCITY = BLUE
COLOR_ANGULAR = TEAL
COLOR_ACCEL = "#FF2D95"
COLOR_ANGULAR_ACCEL = "#C77DFF"


class RollingLessonScene(SceneEventLogMixin, MovingCameraScene):
    """Shared base: local narration playback plus a real camera zoom for the
    'contact microscope' motif described in the plan (section 5)."""

    LESSON_NAME = "rolling_slipping"

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

    def zoom_out(self, run_time: float = 2.2) -> None:
        self.play(
            self.camera.frame.animate.move_to([0, 0, 0]).set(width=DEFAULT_FRAME_WIDTH),
            run_time=run_time,
        )

    def scene_header(self, scene_id: str, heading: str, subtitle: str) -> VGroup:
        label = Text(f"Scene {scene_id}", font_size=18, color=GRAY).to_corner(UP + LEFT, buff=0.3)
        title = Text(heading, font_size=34, weight="BOLD").to_edge(UP, buff=0.3)
        sub = Text(subtitle, font_size=20, color=ORANGE).next_to(title, DOWN, buff=0.1)
        return VGroup(label, title, sub)

    def chapter_banner(self, number: str, name: str) -> VGroup:
        roman = Text(f"CHAPTER {number}", font_size=30, color=GRAY, weight="BOLD")
        heading = Text(name, font_size=40, weight="BOLD").next_to(roman, DOWN, buff=0.3)
        return VGroup(roman, heading)

    def play_subscenes(self, subscenes, mode="sequential", **kwargs):
        """Play a list of SubScene segments sequentially or together.
        See physics_through_anim.subscenes.play_subscenes for options."""
        from physics_through_anim.subscenes import play_subscenes

        return play_subscenes(self, subscenes, mode, **kwargs)


def rough_ground(half_width: float = 5.5, y: float = GROUND_Y) -> VGroup:
    line = Line([-half_width, y, 0], [half_width, y, 0], color=GRAY, stroke_width=6)
    ticks = VGroup()
    for i in range(int(half_width * 3) + 1):
        x = -half_width + i / (half_width * 3) * (2 * half_width)
        ticks.add(Line([x, y, 0], [x - 0.14, y - 0.14, 0], color=GRAY, stroke_width=2))
    return VGroup(line, ticks)


def wheel_setup(radius: float = 1.1, x: float = 0.0, y: float = GROUND_Y) -> VGroup:
    """A disk resting tangent to the ground at (x, y): bottom touches, no gap."""
    center = np.array([x, y + radius, 0.0])
    wheel = Circle(radius=radius, color=BLUE, stroke_width=7).move_to(center)
    hub = Dot(center, color=ORANGE, radius=0.08)
    contact = Dot([x, y, 0.0], color=RED, radius=0.1)
    group = VGroup(wheel, hub, contact)
    group.wheel_center = center
    group.radius = radius
    return group


def thin_block(
    width: float = 1.6, height: float = 0.5, x: float = 0.0, y: float = GROUND_Y
) -> VGroup:
    block = Rectangle(
        width=width, height=height, color=BLUE, fill_color=BLUE, fill_opacity=0.25, stroke_width=5
    )
    block.move_to([x, y + height / 2, 0.0])
    return block


def force_arrow(start, end, label: str, color=COLOR_FRICTION) -> VGroup:
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)
    arrow = Arrow(start, end, buff=0, color=color, stroke_width=6)
    direction = RIGHT if end[0] >= start[0] else LEFT
    text = MathTex(label, color=color).next_to(arrow, direction, buff=0.12)
    return VGroup(arrow, text)


def velocity_arrow(start, end, label: str, color=COLOR_VELOCITY) -> VGroup:
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)
    arrow = Arrow(start, end, buff=0, color=color, stroke_width=4)
    text = MathTex(label, color=color).next_to(arrow, UP, buff=0.1)
    return VGroup(arrow, text)


def angular_arc(
    center, radius: float = 0.55, clockwise: bool = True, label: str = r"\omega"
) -> VGroup:
    angle = -1.5 * np.pi if clockwise else 1.5 * np.pi
    arc = Arc(
        radius=radius, start_angle=np.pi / 2, angle=angle, color=COLOR_ANGULAR, stroke_width=6
    )
    arc.add_tip(tip_length=0.16)
    arc.move_to(np.array(center, dtype=float))
    text = MathTex(label, color=COLOR_ANGULAR).next_to(arc, UP, buff=0.1)
    return VGroup(arc, text)


def contact_microscope(surface_y: float = -1.0, wheel_radius: float = 3.4) -> VGroup:
    """Magnified, geometrically tangent close-up of the wheel-ground contact."""
    surface = Line([-3.4, surface_y, 0], [3.4, surface_y, 0], color=GRAY, stroke_width=6)
    ticks = VGroup(
        *[
            Line([x, surface_y, 0], [x - 0.12, surface_y - 0.12, 0], color=GRAY, stroke_width=2)
            for x in np.linspace(-3.2, 3.2, 12)
        ]
    )
    wheel_center = np.array([0.0, surface_y + wheel_radius, 0.0])
    wheel_edge = Circle(radius=wheel_radius, color=BLUE, stroke_width=7).move_to(wheel_center)
    contact = Dot([0.0, surface_y, 0.0], color=RED, radius=0.09)
    normal = force_arrow([0, surface_y, 0], [0, surface_y + 1.1, 0], "N", COLOR_NORMAL)
    return VGroup(surface, ticks, wheel_edge, contact, normal)


def _fit_text_in_box(text: str, box: RoundedRectangle, font_size: int, color) -> Text:
    body = Text(text, font_size=font_size, color=color)
    max_width = box.width - 0.6
    if body.width > max_width:
        body.scale_to_fit_width(max_width)
    body.move_to(box.get_center())
    return body


def misconception_card(text: str) -> VGroup:
    box = RoundedRectangle(width=10.5, height=0.95, color=RED, corner_radius=0.15)
    label = Text("MISCONCEPTION", font_size=18, color=RED, weight="BOLD").next_to(
        box, UP, buff=0.08
    )
    body = _fit_text_in_box(text, box, font_size=24, color=WHITE)
    return VGroup(box, label, body)


def correction_card(text: str) -> VGroup:
    box = RoundedRectangle(width=10.5, height=0.95, color=GREEN, corner_radius=0.15)
    label = Text("CORRECTION", font_size=18, color=GREEN, weight="BOLD").next_to(box, UP, buff=0.08)
    body = _fit_text_in_box(text, box, font_size=24, color=WHITE)
    return VGroup(box, label, body)


def friction_meter(fraction: float) -> VGroup:
    track = Line(LEFT * 2.5, RIGHT * 2.5, color=GRAY, stroke_width=8)
    pointer = Dot(
        track.point_from_proportion(min(max(fraction, 0.0), 1.0)), color=ORANGE, radius=0.12
    )
    zero_label = Text("0", font_size=20).next_to(track, DOWN, buff=0.1).align_to(track, LEFT)
    max_label = (
        MathTex(r"\mu_s N", font_size=28).next_to(track, DOWN, buff=0.1).align_to(track, RIGHT)
    )
    return VGroup(track, pointer, zero_label, max_label)


def translation_rotation_panels(translation_tex: str, rotation_tex: str) -> VGroup:
    left_title = Text("TRANSLATION", font_size=22, color=BLUE).shift(LEFT * 3.3 + UP * 0.9)
    right_title = Text("ROTATION", font_size=22, color=ORANGE).shift(RIGHT * 3.3 + UP * 0.9)
    left_eq = MathTex(translation_tex, color=BLUE).next_to(left_title, DOWN, buff=0.3)
    right_eq = MathTex(rotation_tex, color=ORANGE).next_to(right_title, DOWN, buff=0.3)
    for eq in (left_eq, right_eq):
        if eq.width > 3.2:
            eq.scale_to_fit_width(3.2)
    divider = Line(UP * 1.3, DOWN * 0.9, color=GRAY)
    return VGroup(left_title, right_title, left_eq, right_eq, divider)


def rolling_constraint_bridge() -> VGroup:
    arrow = DoubleArrow(LEFT * 2.4, RIGHT * 2.4, color=GREEN, buff=0)
    label = Text("NO SLIPPING", font_size=20, color=GREEN).next_to(arrow, DOWN, buff=0.1)
    equation = MathTex(r"a_{\rm CM}=\alpha R", color=GREEN).next_to(arrow, UP, buff=0.15)
    return VGroup(arrow, label, equation)


def acceleration_arrow(start, end, label: str, color=COLOR_ACCEL) -> VGroup:
    """Kinematic acceleration vector -- distinct color/style from force arrows
    and from velocity_arrow so the two vector families are never confused."""
    start = np.array(start, dtype=float)
    end = np.array(end, dtype=float)
    arrow = Arrow(start, end, buff=0, color=color, stroke_width=5, tip_length=0.22)
    text = MathTex(label, color=color).next_to(arrow, UP, buff=0.1)
    return VGroup(arrow, text)


def angular_accel_arc(
    center, radius: float = 0.75, clockwise: bool = True, label: str = r"\alpha"
) -> VGroup:
    """Angular acceleration -- same arc convention as angular_arc but its own
    color, so omega and alpha are never visually interchangeable."""
    angle = -1.3 * np.pi if clockwise else 1.3 * np.pi
    arc = Arc(
        radius=radius, start_angle=np.pi / 2, angle=angle, color=COLOR_ANGULAR_ACCEL, stroke_width=6
    )
    arc.add_tip(tip_length=0.16)
    arc.move_to(np.array(center, dtype=float))
    text = MathTex(label, color=COLOR_ANGULAR_ACCEL).next_to(arc, UP, buff=0.1)
    return VGroup(arc, text)


def rolling_point_velocities(disk: VGroup, v_scale: float = 1.0) -> VGroup:
    """Sample rim points (top, 3 o'clock, 9 o'clock) and draw each velocity
    vector perpendicular to the line joining that point to the contact point
    (the instantaneous axis of rotation), via v_P = omega x r_(P/contact).
    The contact point itself is marked with v=0.
    """
    center = disk.wheel_center
    radius = disk.radius
    group = VGroup()
    for deg in (90, 0, 180):
        theta = np.radians(deg)
        point = center + radius * np.array([np.cos(theta), np.sin(theta), 0.0])
        r = point - center
        v_dir = np.array([r[1], -r[0], 0.0])
        dot = Dot(point, color=COLOR_VELOCITY, radius=0.06)
        arrow = Arrow(point, point + v_dir * v_scale, buff=0, color=COLOR_VELOCITY, stroke_width=4)
        group.add(dot, arrow)
    contact = center + radius * np.array([0.0, -1.0, 0.0])
    group.add(Dot(contact, color=RED, radius=0.08))
    return group


def quadrant_anchors(spread: float = 3.4) -> dict[str, np.ndarray]:
    """Four non-overlapping anchor points, one per screen quadrant. Use these
    to lay out multiple formula+animation pairs side by side instead of
    stacking text down the middle of the screen."""
    return {
        "top_left": np.array([-spread, 1.5, 0.0]),
        "top_right": np.array([spread, 1.5, 0.0]),
        "bottom_left": np.array([-spread, -1.5, 0.0]),
        "bottom_right": np.array([spread, -1.5, 0.0]),
    }


def derive_with_assumption(
    scene, general_tex: str, assumption_tex: str, result_tex: str, position=None
) -> MathTex:
    """Show a general relation, fade in the modeling assumption it depends on
    (e.g. I = m R^2 / 2 for a *solid disk*), then fade both out as the
    specific result fades in -- so the substitution is visible on screen
    instead of a boxed answer appearing out of nowhere."""
    position = np.array([0.0, 0.0, 0.0]) if position is None else np.array(position, dtype=float)
    general = MathTex(general_tex).move_to(position + UP * 0.9)
    assumption = MathTex(assumption_tex, color=ORANGE).move_to(position)
    result = MathTex(result_tex).move_to(position + DOWN * 0.9)
    scene.play(Write(general))
    scene.play(FadeIn(assumption))
    scene.wait(0.6)
    scene.play(FadeOut(general), FadeOut(assumption), FadeIn(result))
    return result


def animate_rolling(
    scene,
    wheel_group: VGroup,
    radius: float,
    distance: float,
    run_time: float = 3.0,
    rightward: bool = True,
) -> None:
    """Translate wheel_group across `distance` while rotating it at the
    matching rate (v = omega * R), so it visibly *rolls* instead of sliding.
    Any scene that moves a wheel must use this rather than a bare `.shift`."""
    original = wheel_group.copy()
    start_center = wheel_group.get_center()
    direction = 1.0 if rightward else -1.0
    tracker = ValueTracker(0.0)

    def _update(mob):
        d = tracker.get_value()
        mob.become(original.copy())
        mob.shift(RIGHT * direction * d)
        mob.rotate(-direction * d / radius, about_point=start_center + RIGHT * direction * d)

    wheel_group.add_updater(_update)
    scene.play(tracker.animate.set_value(distance), run_time=run_time, rate_func=linear)
    wheel_group.remove_updater(_update)


def inertial_observer_icon(scale: float = 1.0):
    icon = SVGMobject(str(ICONS_DIR / "inertial_observer.svg"))
    icon.set_color(WHITE)
    return icon.scale(scale)


def non_inertial_observer_icon(scale: float = 1.0):
    icon = SVGMobject(str(ICONS_DIR / "non_inertial_observer.svg"))
    icon.set_color(WHITE)
    return icon.scale(scale)


def reference_frame_icon(scale: float = 1.0):
    icon = SVGMobject(str(ICONS_DIR / "reference_frame.svg"))
    icon.set_color(GRAY)
    return icon.scale(scale)
