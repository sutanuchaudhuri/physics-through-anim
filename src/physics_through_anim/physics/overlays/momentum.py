"""Momentum + centre-of-mass overlays (Milestone M9) — from supplied state."""

from __future__ import annotations

import numpy as np
from manim import Arrow as _Arrow
from manim import Dot, MathTex, VGroup

from physics_through_anim.physics.mechanics.palette import COLOR_VELOCITY


def _vec3(v, scale: float = 1.0) -> np.ndarray:
    a = np.asarray(v, dtype=float)
    if a.shape[0] == 2:
        a = np.array([a[0], a[1], 0.0])
    return a * scale


def momentum_vector(body, scale: float = 1.0) -> VGroup:
    """``p = m v`` arrow at CM; length proportional to ``mass * |velocity|``."""
    anchor = _vec3(body.keypoint("CM"))
    p = _vec3(body._state.velocity, scale * float(body.mass))
    arrow = _Arrow(anchor, anchor + p, buff=0.0, color=COLOR_VELOCITY, stroke_width=5)
    label = MathTex("p", color=COLOR_VELOCITY).scale(0.7).next_to(arrow.get_end(), buff=0.1)
    return VGroup(arrow, label)


def system_com_marker(bodies) -> Dot:
    """Dot at the mass-weighted mean of each body's CM keypoint."""
    total = sum(float(b.mass) for b in bodies)
    com = sum(float(b.mass) * _vec3(b.keypoint("CM")) for b in bodies) / total
    return Dot(com, color="#FAB005", radius=0.09)
