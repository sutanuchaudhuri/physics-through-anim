"""Render declared forces into free-body-diagram arrows.

Turns each ``ForceSpec`` on an asset into a coloured arrow anchored at the
named keypoint, using the ``FORCE_COLORS`` map (SKILL Rule 2). Directions may be
an explicit unit vector or a keyword ("down", "up", "left", "right").
"""

from __future__ import annotations

import numpy as np
from manim import DOWN, LEFT, RIGHT, UP, Arrow, MathTex, VGroup

from physics_through_anim.physics.mechanics.palette import FORCE_COLORS

_DEFAULT_LENGTH = 0.9
_MIN_LENGTH = 0.4
_MAX_LENGTH = 1.6
_MAGNITUDE_SCALE = 0.28  # world-units per unit magnitude when magnitude is given

_KEYWORD_DIRS = {
    "down": np.array([0.0, -1.0, 0.0]),
    "up": np.array([0.0, 1.0, 0.0]),
    "left": np.array([-1.0, 0.0, 0.0]),
    "right": np.array([1.0, 0.0, 0.0]),
}

_LABEL_SIDE = {"down": DOWN, "up": UP, "left": LEFT, "right": RIGHT}


def _resolve_direction(direction) -> np.ndarray:
    """Return a unit 3D direction for a keyword or explicit vector."""
    if isinstance(direction, str):
        if direction in _KEYWORD_DIRS:
            return _KEYWORD_DIRS[direction]
        # "auto" (or unknown) falls back to "down" -- the common weight case.
        return _KEYWORD_DIRS["down"]
    arr = np.asarray(direction, dtype=float)
    if arr.shape == (2,):
        arr = np.array([arr[0], arr[1], 0.0])
    norm = np.linalg.norm(arr)
    return arr / norm if norm else _KEYWORD_DIRS["down"]


def _arrow_length(magnitude: float | None) -> float:
    if magnitude is None:
        return _DEFAULT_LENGTH
    return float(np.clip(magnitude * _MAGNITUDE_SCALE, _MIN_LENGTH, _MAX_LENGTH))


def render_forces(asset, include=None) -> VGroup:
    """Build a VGroup of arrows for ``asset``'s declared forces."""
    group = VGroup()
    for spec in asset.forces:
        if include is not None and spec.kind not in include:
            continue
        anchor = asset.keypoint(spec.at)
        direction = _resolve_direction(spec.direction)
        end = anchor + direction * _arrow_length(spec.magnitude)
        color = FORCE_COLORS[spec.kind]
        arrow = Arrow(anchor, end, buff=0, color=color, stroke_width=6)
        label = MathTex(spec.label, color=color)
        side = _LABEL_SIDE.get(spec.direction if isinstance(spec.direction, str) else "", UP)
        label.next_to(arrow, side, buff=0.12)
        group.add(VGroup(arrow, label))
    return group
