"""Kinematic overlays (Milestone M9) — render VGroups from supplied state."""

from __future__ import annotations

import numpy as np
from manim import RED, WHITE, Arrow, Dot, MathTex, VGroup

from physics_through_anim.physics.mechanics.palette import COLOR_ACCEL, COLOR_VELOCITY

# Clock-face / cardinal names -> angle (radians, CCW from +x).
_CLOCK = {
    "top": np.pi / 2, "12": np.pi / 2,
    "bottom": -np.pi / 2, "6": -np.pi / 2,
    "right": 0.0, "3": 0.0,
    "left": np.pi, "9": np.pi,
}


def _vec3(v, scale: float = 1.0) -> np.ndarray:
    a = np.asarray(v, dtype=float)
    if a.shape[0] == 2:
        a = np.array([a[0], a[1], 0.0])
    return a * scale


def velocity_vector(body, scale: float = 1.0, frame_label: str | None = None) -> VGroup:
    """Arrow ``COLOR_VELOCITY`` at CM along ``body._state.velocity`` (Rule 2/6)."""
    anchor = _vec3(body.keypoint("CM"))
    v = _vec3(body._state.velocity, scale)
    arrow = Arrow(anchor, anchor + v, buff=0.0, color=COLOR_VELOCITY, stroke_width=4)
    label = MathTex("v", color=COLOR_VELOCITY).scale(0.7).next_to(arrow.get_end(), buff=0.1)
    group = VGroup(arrow, label)
    if frame_label:
        group.add(MathTex(frame_label).scale(0.5).next_to(label, buff=0.05))
    return group


def acceleration_vector(body, scale: float = 1.0) -> VGroup:
    """Arrow ``COLOR_ACCEL`` at CM along ``body._state.acceleration``."""
    anchor = _vec3(body.keypoint("CM"))
    a = _vec3(body._state.acceleration, scale)
    arrow = Arrow(anchor, anchor + a, buff=0.0, color=COLOR_ACCEL, stroke_width=4)
    label = MathTex("a", color=COLOR_ACCEL).scale(0.7).next_to(arrow.get_end(), buff=0.1)
    return VGroup(arrow, label)


def rolling_velocity_field(
    disk, v_cm: float, points: tuple[str, ...] = ("top", "3", "9"), scale: float = 1.0
) -> VGroup:
    """Rule-5 exact field: each rim ``v`` is perp to (point - contact); contact marked v=0."""
    group = VGroup()
    for name in points:
        rim = disk.rim_at(_CLOCK[name])
        v = disk.point_velocity(rim, v_cm)
        group.add(Arrow(_vec3(rim), _vec3(rim) + _vec3(v, scale),
                        buff=0.0, color=COLOR_VELOCITY, stroke_width=4))
    contact = _vec3(disk.contact_point())
    group.add(Dot(contact, color=RED, radius=0.07))
    label = MathTex("v=0", color=RED).scale(0.5)
    group.add(label.next_to(contact, direction=_vec3([0, -1]), buff=0.1))
    return group


def trajectory_trail(body, traj, t0: float, t1: float, n: int = 60, color=WHITE) -> VGroup:
    """Polyline of the CM position sampled from ``traj`` over ``[t0, t1]``."""
    from manim import VMobject

    ref = next(iter(traj.state_at(t0).entities), None)
    points = []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        state = traj.state_at(t)
        entity = state.entities.get(ref) if ref is not None else None
        pos = entity.pose.position if entity is not None else (0.0, 0.0)
        points.append(_vec3(pos))
    line = VMobject(color=color, stroke_width=2)
    line.set_points_as_corners(points)
    return line
