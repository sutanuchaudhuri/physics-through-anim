"""Contact glyphs (Milestone M2).

The ``Contact`` relation carries no mobject; these helpers render its visuals
from a resolved ``ContactFrame``: a dot at the point and a tangent/normal frame.
"""

from __future__ import annotations

import numpy as np
from manim import WHITE, YELLOW, Arrow, Dot, VGroup

from physics_through_anim.physics.mechanics.contact import ContactFrame


def _vec3(v, scale: float = 1.0) -> np.ndarray:
    a = np.asarray(v, dtype=float)
    if a.shape[0] == 2:
        a = np.array([a[0], a[1], 0.0])
    return a * scale


def contact_marker(frame: ContactFrame, *, color: str = WHITE, radius: float = 0.06) -> Dot:
    """A dot at the contact point."""
    return Dot(_vec3(frame.point), color=color, radius=radius)


def contact_frame(frame: ContactFrame, *, scale: float = 0.9, color: str = YELLOW) -> VGroup:
    """Tangent (along surface) and normal (out of surface) arrows at the point."""
    p = _vec3(frame.point)
    t = _vec3(frame.tangent, scale)
    n = _vec3(frame.normal, scale)
    return VGroup(
        Arrow(p, p + t, buff=0, color=color, stroke_width=4),
        Arrow(p, p + n, buff=0, color=color, stroke_width=4),
    )
