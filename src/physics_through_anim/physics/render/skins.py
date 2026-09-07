"""Skins: build a body's *picture* from a shape signature (render engine only).

A rolling body's physics is a disk; its picture can be anything. ``radial_polygon``
turns an **input vector** of per-vertex radii into a silhouette, and ``rock_skin``
uses a seeded radial profile to make a reproducible jagged rock. Both return a
plain Manim mobject that a ``CircularBody`` accepts as its ``skin`` (so
``mechanics`` never imports ``render``). Extend by passing your own vector, your
own mobject/image, or subclassing the body.
"""

from __future__ import annotations

from collections.abc import Sequence
from math import cos, pi, sin

import numpy as np
from manim import ManimColor, Polygon

ROCK_COLOR = ManimColor("#8a8078")


def radial_polygon(radii: Sequence[float], *, radius: float = 1.0, **poly_kwargs) -> Polygon:
    """A closed silhouette from an input vector of per-vertex radii (0..1-ish)."""
    n = len(radii)
    if n < 3:
        raise ValueError("radial_polygon needs at least 3 radii.")
    points = []
    for i, r in enumerate(radii):
        ang = 2.0 * pi * i / n
        points.append([radius * r * cos(ang), radius * r * sin(ang), 0.0])
    return Polygon(*points, **poly_kwargs)


def rock_skin(
    *,
    radius: float = 0.6,
    sides: int = 9,
    jitter: float = 0.18,
    seed: int = 0,
    color=ROCK_COLOR,
    fill_opacity: float = 1.0,
    stroke_width: float = 2.0,
) -> Polygon:
    """A reproducible jagged rock silhouette (a ``radial_polygon`` with noisy radii)."""
    rng = np.random.default_rng(seed)
    radii = 1.0 + jitter * (rng.random(sides) * 2.0 - 1.0)
    return radial_polygon(
        radii,
        radius=radius,
        color=color,
        fill_color=color,
        fill_opacity=fill_opacity,
        stroke_width=stroke_width,
    )
