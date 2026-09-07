"""Collision / event overlays (Milestone M12).

The event *model* lives in ``core/events.py``; these are its render-free visuals:
an on-screen collision tally, an impulse arrow, and before/after velocity arrows.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from manim import WHITE, Arc, Arrow, MathTex, VGroup

from physics_through_anim.physics.core.events import Event, EventKind, EventSequence
from physics_through_anim.physics.mechanics.palette import COLOR_ANGULAR, COLOR_VELOCITY

COLOR_IMPULSE = "#F783AC"  # pink, distinct from the FBD/kinematic families


def _vec3(v, scale: float = 1.0) -> np.ndarray:
    a = np.atleast_1d(np.asarray(v, dtype=float))
    if a.shape[0] == 1:
        a = np.array([a[0], 0.0, 0.0])
    elif a.shape[0] == 2:
        a = np.array([a[0], a[1], 0.0])
    return a * scale


@dataclass
class EventCounter:
    """On-screen tally of collisions so far (symbol-only, SKILL Rule 9)."""

    seq: EventSequence | None = None
    kinds: tuple[EventKind, ...] = (EventKind.IMPACT,)

    def count_at(self, t: float) -> int:
        if self.seq is None:
            return 0
        return sum(1 for e in self.seq.events if e.kind in self.kinds and e.time <= t)

    def glyph(self, t: float, *, color: str = WHITE, font_size: float = 44) -> MathTex:
        """A ``n = k`` symbol where ``k`` is the count of matching events by time ``t``."""
        return MathTex(f"n = {self.count_at(t)}", color=color, font_size=font_size)


def collision(a: str, b: str, t: float, restitution: float = 1.0, impulse: float = 0.0) -> Event:
    """Build an IMPACT event between two participants (the law is supplied, not solved)."""
    return Event(time=t, kind=EventKind.IMPACT, participants=(a, b),
                 payload={"restitution": restitution, "impulse": impulse},
                 tag=f"e={restitution}")


def impulse_arrow(body, impulse: float, at: str = "CM", direction=(1.0, 0.0),
                  scale: float = 0.5) -> VGroup:
    """A ``J`` (impulse) arrow at ``at``; length proportional to ``|impulse|``."""
    anchor = _vec3(body.keypoint(at))
    d = _vec3(direction)
    d = d / (np.linalg.norm(d) or 1.0)
    tip = anchor + d * scale * abs(impulse)
    arrow = Arrow(anchor, tip, buff=0.0, color=COLOR_IMPULSE, stroke_width=6)
    label = MathTex("J", color=COLOR_IMPULSE).scale(0.7).next_to(arrow.get_end(), buff=0.1)
    return VGroup(arrow, label)


def velocity_before_after(body, v_before, v_after, at: str = "CM", scale: float = 0.5) -> VGroup:
    """Two velocity arrows at ``at``: the pre-impact (dim) and post-impact (bright)."""
    anchor = _vec3(body.keypoint(at))
    before = Arrow(anchor, anchor + _vec3(v_before, scale), buff=0.0,
                   color=COLOR_VELOCITY, stroke_width=4).set_opacity(0.45)
    after = Arrow(anchor, anchor + _vec3(v_after, scale), buff=0.0,
                  color=COLOR_VELOCITY, stroke_width=5)
    return VGroup(
        before, after,
        MathTex("v^-", color=COLOR_VELOCITY).scale(0.55).next_to(before.get_end(), buff=0.08),
        MathTex("v^+", color=COLOR_VELOCITY).scale(0.6).next_to(after.get_end(), buff=0.08),
    )


def angular_impulse_markers(point, impulse, cm, delta_v, delta_omega, *, j_scale: float = 0.5,
                            v_scale: float = 0.5, spin_radius: float = 0.5) -> VGroup:
    """Render an off-centre impulse: the ``J`` at ``point``, the CM ``dv``, the spin ``domega``.

    ``delta_v``/``delta_omega`` come from :func:`impulse_response`; this only draws
    them (impulse pink, velocity blue, spin arc teal, sense from the sign of omega).
    """
    p = _vec3(point)
    c = _vec3(cm)
    j = _vec3(impulse, j_scale)
    dv = _vec3(delta_v, v_scale)
    group = VGroup(
        Arrow(p, p + j, buff=0.0, color=COLOR_IMPULSE, stroke_width=6),
        MathTex("J", color=COLOR_IMPULSE).scale(0.7).next_to(p + j, buff=0.08),
    )
    if float(np.linalg.norm(dv)) > 1e-6:
        group.add(Arrow(c, c + dv, buff=0.0, color=COLOR_VELOCITY, stroke_width=5))
        group.add(MathTex(r"\Delta v", color=COLOR_VELOCITY).scale(0.6).next_to(c + dv, buff=0.08))
    if abs(delta_omega) > 1e-6:
        sweep = np.sign(delta_omega) * 2.2
        arc = Arc(radius=spin_radius, start_angle=0.4, angle=sweep, arc_center=c,
                  color=COLOR_ANGULAR, stroke_width=4).add_tip(tip_length=0.18)
        group.add(arc)
        spin_label = MathTex(r"\Delta\omega", color=COLOR_ANGULAR).scale(0.6)
        group.add(spin_label.next_to(c, np.array([0.0, 1.0, 0.0]), buff=spin_radius + 0.1))
    return group
