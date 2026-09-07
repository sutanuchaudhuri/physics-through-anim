"""Orbital explanation overlays (Milestone M13).

Drawn from the orbit geometry + a live planet position: the Sun->planet radius
vector, a Kepler-II swept-area sector, and the central gravity arrow (always
pointing at the force centre).
"""

from __future__ import annotations

import numpy as np
from manim import Arrow as _Arrow
from manim import MathTex, Polygon, VGroup

from physics_through_anim.physics.mechanics.palette import COLOR_GRAVITY, COLOR_VELOCITY


def _v3(p) -> np.ndarray:
    a = np.asarray(p, dtype=float)
    return a if a.shape[0] == 3 else np.array([a[0], a[1], 0.0])


def radius_vector(center, body, *, color: str = COLOR_VELOCITY) -> VGroup:
    """The Sun->planet radius arrow ``r`` (center point -> ``body.keypoint('CM')``)."""
    c = _v3(center)
    p = _v3(body.keypoint("CM"))
    arrow = _Arrow(c, p, buff=0.0, color=color, stroke_width=4)
    label = MathTex("r", color=color).scale(0.6).next_to(arrow.get_center(), buff=0.1)
    return VGroup(arrow, label)


def swept_area(orbit, theta0: float, theta1: float, *, color: str = "#FFD43B",
               opacity: float = 0.5, n: int = 24) -> Polygon:
    """A shaded focus sector between true anomalies ``theta0..theta1`` (Kepler II)."""
    focus = orbit._focus3()
    arc = [orbit.point_at(theta0 + (theta1 - theta0) * i / n) for i in range(n + 1)]
    return Polygon(focus, *arc, color=color, fill_color=color, fill_opacity=opacity,
                   stroke_width=2)


def central_force_arrow(body, toward_point, *, scale: float = 1.0,
                        color: str = COLOR_GRAVITY) -> VGroup:
    """Gravity arrow at the planet CM pointing at the force centre ``toward_point``."""
    p = _v3(body.keypoint("CM"))
    d = _v3(toward_point) - p
    n = float(np.linalg.norm(d))
    unit = d / n if n > 1e-9 else np.array([1.0, 0.0, 0.0])
    arrow = _Arrow(p, p + unit * scale, buff=0.0, color=color, stroke_width=5)
    label = MathTex("F_g", color=color).scale(0.6).next_to(arrow.get_end(), buff=0.1)
    return VGroup(arrow, label)
