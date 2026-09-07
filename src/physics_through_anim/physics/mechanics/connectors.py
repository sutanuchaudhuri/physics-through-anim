"""Flexible physical links + pin/hinge glyphs (Milestone M4).

Connectors are drawable links between two named points: a ``Rope`` (and its
``Cable``/``MasslessLink`` kin) pulls each end toward the other and declares a
``TENSION`` force on a body; a ``Hinge``/``PinJoint`` marks a pinned point and
declares a ``REACTION``. Typed *constraints* (the semantic relationships) live in
``constraints.py``; these are the pictures + force declarations.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from manim import Arc, ArcBetweenPoints, Circle, Dot, Line, VGroup, VMobject

from physics_through_anim.physics.core.pose import Vec2
from physics_through_anim.physics.mechanics.base import PhysicsAsset, _as_point
from physics_through_anim.physics.mechanics.kinds import BodyDynamics, ForceKind
from physics_through_anim.physics.mechanics.palette import COLOR_REACTION, COLOR_TENSION


@dataclass
class Connector(PhysicsAsset):
    """Base for a link between two assembly keypoints (resolved at ``connect``)."""

    name: str = "connector"
    dynamics: BodyDynamics = BodyDynamics.STATIC
    from_ref: str = ""
    to_ref: str = ""


@dataclass
class Rope(Connector):
    """A rope: a line, a slack sag, or a taut segment between its two ends.

    With ``rest_length`` set, the rope has a *natural length* whose drawn shape is
    **not fixed**: when the ends are closer than ``rest_length`` it hangs **slack**
    (sags downward), and when stretched to/beyond it, it snaps **taut** (straight).
    """

    name: str = "rope"
    from_point: Vec2 = (0.0, 0.0)
    to_point: Vec2 = (0.0, -1.0)
    tension_label: str = "T"
    slips: bool = False
    sag: float = 0.0  # >0 draws a fixed slack arc between the ends
    rest_length: float | None = None  # natural length: slack if span < rest_length, else taut
    color: str = COLOR_TENSION
    stroke_width: float = 3.0
    _span: float = 0.0

    def build(self) -> VGroup:
        a, b = _as_point(self.from_point), _as_point(self.to_point)
        self._span = float(np.linalg.norm(b - a))
        if self.rest_length is not None and self._span < self.rest_length:
            link = self._sag_curve(a, b, self.rest_length - self._span)
        elif self.sag > 0:
            link = ArcBetweenPoints(a, b, angle=self.sag, color=self.color,
                                    stroke_width=self.stroke_width)
        else:
            link = Line(a, b, color=self.color, stroke_width=self.stroke_width)
        group = VGroup(link)
        self.set_keypoint("from", a[:2])
        self.set_keypoint("to", b[:2])
        self.set_keypoint("mid", ((a + b) / 2.0)[:2])
        if self.slips:
            group.add(self._slip_marks(a, b))
        return group

    def _sag_curve(self, a: np.ndarray, b: np.ndarray, slack: float) -> VMobject:
        """A downward-hanging curve whose droop grows with the ``slack`` amount."""
        d = float(np.linalg.norm(b - a))
        # parabola arc length L ~ d + 8 h^2 / (3 d)  ->  h = sqrt(3 d slack / 8)
        h = float(np.sqrt(max(3.0 * d * slack, 0.0)) / 8.0 ** 0.5) if d > 1e-6 else slack / 2.0
        low = (a + b) / 2.0 + np.array([0.0, -h, 0.0])
        curve = VMobject(color=self.color, stroke_width=self.stroke_width)
        curve.set_points_smoothly([a, low, b])
        return curve

    def is_taut(self) -> bool:
        """True unless a ``rest_length`` is set and the span is shorter than it."""
        return self.rest_length is None or self._span >= self.rest_length

    def _slip_marks(self, a: np.ndarray, b: np.ndarray) -> VGroup:
        """Short hash ticks near the wheel end to read as sliding contact."""
        t = b - a
        n = t / (np.linalg.norm(t) or 1.0)
        perp = np.array([-n[1], n[0], 0.0])
        marks = VGroup()
        for s in (0.12, 0.2, 0.28):
            p = a + s * (b - a)
            marks.add(Line(p - 0.1 * perp, p + 0.1 * perp, color=self.color, stroke_width=2))
        return marks

    def set_endpoints(self, a, b) -> None:
        """Move the rope's ends to world points ``a``/``b`` and redraw in place."""
        self.from_point = (float(a[0]), float(a[1]))
        self.to_point = (float(b[0]), float(b[1]))
        self.keypoints = {}
        rebuilt = self.build()
        self.mobject.remove(*self.mobject.submobjects)
        self.mobject.add(*rebuilt.submobjects)

    def tension_on(self, body, at: str, toward) -> None:
        """Declare a ``TENSION`` force on ``body`` at keypoint ``at`` toward a point."""
        anchor = body.keypoint(at)
        d = _as_point(toward) - anchor
        norm = float(np.linalg.norm(d)) or 1.0
        unit = d / norm
        body.add_force(ForceKind.TENSION, at=at, label=self.tension_label,
                       direction=(float(unit[0]), float(unit[1])))


@dataclass
class Cable(Rope):
    """A rope with give (elastic cable) -- same picture, distinct semantics."""

    name: str = "cable"


@dataclass
class SlackString(Rope):
    """A string with a natural ``rest_length`` that hangs slack or snaps taut.

    Its drawn length is not fixed: closer ends sag more, stretching to
    ``rest_length`` pulls it straight. Set ``rest_length`` to enable the behaviour.
    """

    name: str = "string"
    rest_length: float | None = 2.0


def _tangent_points(p, center, radius: float) -> list[np.ndarray]:
    """The two points where lines from external ``p`` touch the circle (right angle)."""
    p2 = np.asarray(p, dtype=float)[:2]
    c2 = np.asarray(center, dtype=float)[:2]
    d_vec = p2 - c2
    d = float(np.linalg.norm(d_vec))
    if d <= radius:
        return []
    theta = np.arccos(radius / d)
    base = np.arctan2(d_vec[1], d_vec[0])
    return [
        np.array([c2[0] + radius * np.cos(base + s * theta),
                  c2[1] + radius * np.sin(base + s * theta), 0.0])
        for s in (1.0, -1.0)
    ]


def _outer_tangent(p, center, radius: float, away_from) -> np.ndarray:
    """The tangent point farthest from ``away_from`` (so the rope hugs the far side)."""
    pts = _tangent_points(p, center, radius)
    if not pts:
        c2 = np.asarray(center, dtype=float)[:2]
        return np.array([c2[0] + radius, c2[1], 0.0])
    aw = np.asarray(away_from, dtype=float)[:2]
    return max(pts, key=lambda t: float(np.linalg.norm(t[:2] - aw)))


@dataclass
class RopeOverPulley(Connector):
    """A rope that wraps a pulley: two straight tangents + an arc on the rim.

    Given the two external anchors ``from_point``/``to_point`` and a ``pulley``
    (or ``center``/``radius``), it derives the two tangent **contact points**, the
    **wrap arc** riding the rim between them, and (for ``turns > 1``) a spindle
    wrap. Nothing is hand-placed.
    """

    name: str = "rope"
    pulley: object = None
    center: Vec2 = (0.0, 0.0)
    radius: float = 0.6
    from_point: Vec2 = (0.0, 0.0)
    to_point: Vec2 = (0.0, -1.0)
    tension_label: str = "T"
    turns: float = 1.0
    color: str = COLOR_TENSION
    stroke_width: float = 3.0
    _wrap_angle: float = 0.0

    def _circle(self) -> tuple[np.ndarray, float]:
        if self.pulley is not None:
            c = self.pulley.keypoint("axle")[:2] if hasattr(self.pulley, "keypoint") \
                else np.asarray(self.pulley.center, dtype=float)
            return np.array([c[0], c[1], 0.0]), float(self.pulley.radius)
        c = np.asarray(self.center, dtype=float)
        return np.array([c[0], c[1], 0.0]), float(self.radius)

    def build(self) -> VGroup:
        c, r = self._circle()
        a = _as_point(self.from_point)
        b = _as_point(self.to_point)
        t_a = _outer_tangent(a, c, r, b)
        t_b = _outer_tangent(b, c, r, a)
        start = float(np.arctan2(t_a[1] - c[1], t_a[0] - c[0]))
        end = float(np.arctan2(t_b[1] - c[1], t_b[0] - c[0]))
        delta = self._outer_delta(c, r, start, end, a, b)
        self._wrap_angle = abs(delta) + 2.0 * np.pi * max(self.turns - 1.0, 0.0)

        group = VGroup(
            Line(a, t_a, color=self.color, stroke_width=self.stroke_width),
            Arc(radius=r, start_angle=start, angle=delta, arc_center=c,
                color=self.color, stroke_width=self.stroke_width),
            Line(t_b, b, color=self.color, stroke_width=self.stroke_width),
        )
        for i in range(int(self.turns) - 1):  # spindle: extra stacked loops
            group.add(Circle(radius=r + 0.03 * (i + 1), arc_center=c,
                             color=self.color, stroke_width=self.stroke_width))
        self.set_keypoint("from", a[:2])
        self.set_keypoint("to", b[:2])
        self.set_keypoint("contact_a", t_a[:2])
        self.set_keypoint("contact_b", t_b[:2])
        mid = c + r * np.array([np.cos(start + delta / 2.0), np.sin(start + delta / 2.0), 0.0])
        self.set_keypoint("arc_mid", mid[:2])
        return group

    def _outer_delta(self, c, r, start, end, a, b) -> float:
        """Signed arc from start to end that bulges away from the anchors."""
        ccw = (end - start) % (2.0 * np.pi)  # positive CCW sweep
        cw = ccw - 2.0 * np.pi  # negative CW sweep (the complement)
        centroid = (np.asarray(a, dtype=float)[:2] + np.asarray(b, dtype=float)[:2]) / 2.0

        def bulge(delta):
            m = c[:2] + r * np.array([np.cos(start + delta / 2.0), np.sin(start + delta / 2.0)])
            return float(np.linalg.norm(m - centroid))

        return ccw if bulge(ccw) >= bulge(cw) else cw

    def wrap_angle(self) -> float:
        """Total subtended wrap (rad), including full turns for a spindle."""
        return self._wrap_angle

    def set_endpoints(self, a, b) -> None:
        """Move the two external anchors and redraw the wrap in place."""
        self.from_point = (float(a[0]), float(a[1]))
        self.to_point = (float(b[0]), float(b[1]))
        self.keypoints = {}
        rebuilt = self.build()
        self.mobject.remove(*self.mobject.submobjects)
        self.mobject.add(*rebuilt.submobjects)

    def tension_on(self, body, at: str, toward) -> None:
        """Declare a ``TENSION`` force on ``body`` at ``at`` toward a point."""
        anchor = body.keypoint(at)
        d = _as_point(toward) - anchor
        norm = float(np.linalg.norm(d)) or 1.0
        unit = d / norm
        body.add_force(ForceKind.TENSION, at=at, label=self.tension_label,
                       direction=(float(unit[0]), float(unit[1])))



@dataclass
class MasslessLink(Rope):
    """An ideal rigid massless link (a rod-like tension/compression member)."""

    name: str = "link"


@dataclass
class Hinge(Connector):
    """A pin that fixes a point -- a SEPARATE asset from the wall it pins to."""

    name: str = "hinge"
    at: Vec2 = (0.0, 0.0)
    pins: str = ""
    to: str = ""
    color: str = COLOR_REACTION

    def build(self) -> VGroup:
        p = _as_point(self.at)
        group = VGroup(
            Circle(radius=0.12, color=self.color, stroke_width=3).move_to(p),
            Dot(p, color=self.color, radius=0.05),
        )
        self.set_keypoint("H", p[:2])
        return group

    def reaction_on(self, body, at: str = "A", label: str = "R") -> None:
        """Declare the hinge's (unknown-direction) ``REACTION`` on ``body`` at ``at``."""
        body.add_force(ForceKind.REACTION, at=at, label=label, direction="auto")


@dataclass
class PinJoint(Connector):
    """Semantic 'A pinned to B at a point': declares the Newton-3rd reaction pair."""

    name: str = "pin"
    at: Vec2 = (0.0, 0.0)
    a_ref: str = ""
    b_ref: str = ""
    color: str = COLOR_REACTION

    def build(self) -> VGroup:
        p = _as_point(self.at)
        group = VGroup(Dot(p, color=self.color, radius=0.06))
        self.set_keypoint("H", p[:2])
        return group

