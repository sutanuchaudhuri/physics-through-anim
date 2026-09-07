"""Framework-level rolling animation helper (Milestone M3).

``roll_group`` translates + spins a body over a horizontal distance at ``v = omega
R`` with no drift (``Delta theta = -Delta s / R``), rebuilding from a base copy
each frame so the asset layer never imports a lesson's ``common.py``.
"""

from __future__ import annotations

import numpy as np
from manim import ValueTracker


def roll_group(
    scene, body, distance: float, *, run_time: float = 3.0, rightward: bool = True
) -> None:
    """Roll ``body`` (a round asset with ``.radius``/``.mobject``) along the ground."""
    radius = float(body.radius)
    cm0 = np.array(body.keypoint("CM"), dtype=float)
    base = body.mobject.copy()
    direction = 1.0 if rightward else -1.0
    s = ValueTracker(0.0)

    def update(mob):
        travelled = direction * s.get_value()
        angle = -direction * s.get_value() / radius  # rolling relation: Delta theta = -Delta s / R
        mob.become(base.copy())
        mob.rotate(angle, about_point=cm0)
        mob.shift([travelled, 0.0, 0.0])
        body.keypoints["CM"] = cm0 + np.array([travelled, 0.0, 0.0])
        body.keypoints["contact"] = body.keypoints["CM"] - np.array([0.0, radius, 0.0])

    body.mobject.add_updater(update)
    scene.play(s.animate.set_value(distance), run_time=run_time)
    body.mobject.clear_updaters()


def roll_along_surface(
    scene, body, wall, distance: float, *, run_time: float = 3.0, down: bool = True
) -> None:
    """Roll ``body`` along ``wall``'s surface, staying seated (always in contact).

    The centre is parametrised along the surface *tangent* at a fixed offset ``R``
    from the surface, so the body can never pierce or leave the wall -- the
    no-penetration/contact constraint is baked into the motion, not re-checked.
    Rolling obeys ``Delta theta = -Delta s / R`` along the slope.
    """
    radius = float(body.radius)
    normal = np.asarray(wall.normal(), dtype=float)
    tangent = np.asarray(wall.tangent(), dtype=float)
    if (down and tangent[1] > 0) or (not down and tangent[1] < 0):
        tangent = -tangent  # orient the tangent along the requested travel direction
    cm0 = np.array(body.keypoint("CM"), dtype=float)
    base = body.mobject.copy()
    s = ValueTracker(0.0)

    def update(mob):
        travelled = s.get_value()
        angle = -travelled / radius  # rolling without slip along the tangent
        centre = cm0 + travelled * tangent
        mob.become(base.copy())
        mob.rotate(angle, about_point=cm0)
        mob.shift(centre - cm0)
        body.keypoints["CM"] = centre
        body.keypoints["contact"] = centre - radius * normal

    body.mobject.add_updater(update)
    scene.play(s.animate.set_value(distance), run_time=run_time)
    body.mobject.clear_updaters()

