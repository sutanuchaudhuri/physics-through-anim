"""Point-of-interest markers + callouts (developer annotation overlay).

Mark a special point on a body -- **static** (a fixed world point) or **dynamic**
(a body keypoint tracked every frame) -- with a label and an optional "Look at
point P" callout. Every returned ``VGroup`` fades in/out normally, so the
developer scripts exactly when a point of interest appears and disappears.
"""

from __future__ import annotations

import numpy as np
from manim import UP, WHITE, YELLOW, Dot, Line, MathTex, Text, VGroup


def _v3(p, scale: float = 1.0) -> np.ndarray:
    a = np.asarray(p, dtype=float)
    if a.shape[0] == 2:
        a = np.array([a[0], a[1], 0.0])
    return a * scale


def point_marker(point, label: str | None = None, *, color: str = YELLOW, radius: float = 0.08,
                 label_direction=UP, label_buff: float = 0.14) -> VGroup:
    """A labelled dot at a point of interest (e.g. ``point_marker(P, "P")``)."""
    dot = Dot(_v3(point), color=color, radius=radius)
    group = VGroup(dot)
    if label:
        tex = MathTex(label, color=color).scale(0.65).next_to(dot, label_direction, buff=label_buff)
        group.add(tex)
    return group


def follow_keypoint(marker: VGroup, body, key: str, *, label_direction=UP,
                    label_buff: float = 0.14) -> VGroup:
    """Bind a ``point_marker`` to a moving ``body.keypoint(key)`` so it tracks it live."""
    def _update(m):
        target = _v3(body.keypoint(key))
        m.submobjects[0].move_to(target)
        if len(m.submobjects) > 1:
            m.submobjects[1].next_to(m.submobjects[0], label_direction, buff=label_buff)

    marker.add_updater(_update)
    return marker


def callout(point, text: str, *, offset=(1.5, 0.9), color: str = WHITE, font_size: float = 22,
            leader: bool = True, leader_color: str = YELLOW) -> VGroup:
    """A text callout (e.g. ``"Look at point P"``) with an optional leader to the point."""
    p = _v3(point)
    label = Text(text, font_size=font_size, color=color).move_to(p + _v3(offset))
    group = VGroup(label)
    if leader:
        d = label.get_center() - p
        n = d / (np.linalg.norm(d) or 1.0)
        line = Line(p + n * 0.18, label.get_center() - n * 0.12,
                    color=leader_color, stroke_width=2).set_opacity(0.75)
        group.add(line)
    return group
