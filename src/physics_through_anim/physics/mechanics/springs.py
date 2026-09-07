"""Springs / dampers + constitutive laws (Milestone M10).

Geometry (``LinearSpring``, ``Damper``, ``TorsionSpring``) is kept separate from
the force law (``HookeLaw``, ``LinearDamperLaw``, ``TorsionalHookeLaw``).
Evaluating ``F = -k x`` is a *local constitutive law* an asset may do; it is not
integrating the equations of motion. Extension/compression are derived signals
(``deformation()``), not enums, so M9 ``GraphBinding`` can plot them.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from manim import VGroup, VMobject

from physics_through_anim.physics.core.pose import Vec2
from physics_through_anim.physics.mechanics.base import PhysicsAsset, _as_point
from physics_through_anim.physics.mechanics.connectors import Connector
from physics_through_anim.physics.mechanics.kinds import ForceKind
from physics_through_anim.physics.mechanics.palette import COLOR_DAMPING, COLOR_SPRING


def _unit(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    return v / n if n > 1e-9 else np.array([1.0, 0.0, 0.0])


@dataclass
class LinearSpring(Connector):
    """A massless coil between two points; draws a zigzag that stretches/compresses."""

    name: str = "spring"
    from_point: Vec2 = (0.0, 0.0)
    to_point: Vec2 = (1.0, 0.0)
    natural_length: float = 1.0
    coils: int = 8
    width: float = 0.25
    force_label: str = "F_s"
    color: str = COLOR_SPRING
    stroke_width: float = 3.0
    k: float | None = None  # stiffness (optional; used for combination labels)
    current_length: float = field(default=0.0, init=False)

    def build(self) -> VGroup:
        a, b = _as_point(self.from_point), _as_point(self.to_point)
        coil = self._coil(a, b)
        self.set_keypoint("A", a[:2])
        self.set_keypoint("B", b[:2])
        self.set_keypoint("mid", ((a + b) / 2.0)[:2])
        return VGroup(coil)

    def _coil(self, a: np.ndarray, b: np.ndarray) -> VMobject:
        axis = b - a
        self.current_length = float(np.linalg.norm(axis))
        u = _unit(axis)
        perp = np.array([-u[1], u[0], 0.0])
        lead = 0.15  # straight lead-in fraction at each end
        start, end = a + axis * lead, b - axis * lead
        points = [a, start]
        n = max(1, self.coils) * 2
        for i in range(1, n):
            frac = i / n
            side = self.width * (1.0 if i % 2 == 1 else -1.0)
            points.append(start + (end - start) * frac + perp * side)
        points.extend([end, b])
        coil = VMobject(color=self.color, stroke_width=self.stroke_width)
        coil.set_points_as_corners(points)
        return coil

    def set_endpoints(self, a, b) -> LinearSpring:
        """Redraw the coil between new endpoints (updates ``current_length``)."""
        pa, pb = _as_point(a), _as_point(b)
        self.from_point, self.to_point = tuple(pa[:2]), tuple(pb[:2])
        self.mobject.become(VGroup(self._coil(pa, pb)))
        self.set_keypoint("A", pa[:2])
        self.set_keypoint("B", pb[:2])
        self.set_keypoint("mid", ((pa + pb) / 2.0)[:2])
        return self

    def deformation(self) -> float:
        """``current_length - natural_length`` (>0 stretch, =0 natural, <0 compress)."""
        return self.current_length - self.natural_length

    def extension(self) -> float:
        return max(0.0, self.deformation())

    def compression(self) -> float:
        return max(0.0, -self.deformation())

    def spring_force_on(self, body: PhysicsAsset, at: str, k_val: float | None = None):
        """Declare the restoring ``F_s`` on ``body`` at keypoint ``at`` (direction only).

        Points toward the natural configuration: inward when stretched, outward when
        compressed. Magnitude (if any) is a label decision, not a physical solve.
        """
        a, b = self.keypoint("A"), self.keypoint("B")
        toward_a = _unit(a - b)  # inward for the body at end B
        direction = toward_a if self.deformation() >= 0 else -toward_a
        return body.add_force(ForceKind.SPRING, at=at, label=self.force_label,
                              direction=(float(direction[0]), float(direction[1])),
                              magnitude=k_val)


Spring = LinearSpring


@dataclass
class SpringGroup(Connector):
    """A bank of springs between one pair of endpoints: ``series`` or ``parallel``.

    Both outer ends (and every series junction) render an explicit connector so a
    viewer can see where the bank attaches. Effective stiffness is a local fact:
    ``1/k = Σ 1/k_i`` (series) or ``k = Σ k_i`` (parallel).
    """

    name: str = "springs"
    from_point: Vec2 = (0.0, 0.0)
    to_point: Vec2 = (2.0, 0.0)
    members: list = field(default_factory=list)
    arrangement: str = "series"  # "series" | "parallel"
    offset: float = 0.35  # parallel perpendicular spacing
    color: str = COLOR_SPRING
    stroke_width: float = 3.0
    current_length: float = field(default=0.0, init=False)
    natural_length: float = field(default=0.0, init=False)
    k_eff: float | None = field(default=None, init=False)

    def build(self) -> VGroup:
        from manim import Dot, Line, Square

        a, b = _as_point(self.from_point), _as_point(self.to_point)
        axis = b - a
        self.current_length = float(np.linalg.norm(axis))
        u = _unit(axis)
        perp = np.array([-u[1], u[0], 0.0])
        ks = [m.k for m in self.members]
        group = VGroup()

        if self.arrangement == "parallel":
            self.k_eff = sum(ks) if all(k is not None for k in ks) else None
            self.natural_length = self.members[0].natural_length if self.members else 0.0
            n = len(self.members)
            for i, m in enumerate(self.members):
                off = perp * self.offset * (i - (n - 1) / 2.0)
                m.set_endpoints((a + off)[:2], (b + off)[:2])
                group.add(m.mobject)
                group.add(Line(a, a + off, color=self.color, stroke_width=self.stroke_width))
                group.add(Line(b, b + off, color=self.color, stroke_width=self.stroke_width))
        else:  # series
            self.k_eff = 1.0 / sum(1.0 / k for k in ks) if all(ks) else None
            self.natural_length = sum(m.natural_length for m in self.members)
            weights = [m.natural_length for m in self.members] or [1.0]
            total = sum(weights)
            p = a.copy()
            for i, m in enumerate(self.members):
                q = p + axis * (weights[i] / total)
                m.set_endpoints(p[:2], q[:2])
                group.add(m.mobject)
                if i < len(self.members) - 1:
                    group.add(Dot(q, color=self.color, radius=0.06))  # junction connector
                p = q

        for end in (a, b):  # square end connectors
            sq = Square(side_length=0.12, color=self.color, stroke_width=self.stroke_width)
            group.add(sq.move_to(end))
        self.set_keypoint("A", a[:2])
        self.set_keypoint("B", b[:2])
        self.set_keypoint("mid", ((a + b) / 2.0)[:2])
        return group

    def deformation(self) -> float:
        return self.current_length - self.natural_length


def series_springs(members, from_point=(0.0, 0.0), to_point=(2.0, 0.0), **kw) -> SpringGroup:
    """A collinear end-to-end bank; ``1/k_eff = Σ 1/k_i``."""
    return SpringGroup(members=list(members), arrangement="series",
                       from_point=from_point, to_point=to_point, **kw)


def parallel_springs(members, from_point=(0.0, 0.0), to_point=(2.0, 0.0), **kw) -> SpringGroup:
    """A stacked bank sharing both endpoints; ``k_eff = Σ k_i``."""
    return SpringGroup(members=list(members), arrangement="parallel",
                       from_point=from_point, to_point=to_point, **kw)


@dataclass
class Damper(Connector):
    """A dashpot glyph (piston in a cylinder) whose force opposes relative velocity."""

    name: str = "damper"
    from_point: Vec2 = (0.0, 0.0)
    to_point: Vec2 = (1.0, 0.0)
    width: float = 0.22
    force_label: str = "F_c"
    color: str = COLOR_DAMPING
    stroke_width: float = 3.0

    def build(self) -> VGroup:
        from manim import Line

        a, b = _as_point(self.from_point), _as_point(self.to_point)
        u = _unit(b - a)
        perp = np.array([-u[1], u[0], 0.0]) * self.width
        mid = (a + b) / 2.0
        cyl_back = mid - u * self.width
        sw = self.stroke_width
        group = VGroup(
            Line(a, cyl_back, color=self.color, stroke_width=sw),
            Line(cyl_back - perp, cyl_back + perp, color=self.color, stroke_width=sw),
            Line(mid + perp, mid - perp, color=self.color, stroke_width=sw),
            Line(mid, b, color=self.color, stroke_width=sw),
        )
        self.set_keypoint("A", a[:2])
        self.set_keypoint("B", b[:2])
        return group

    def damping_force_on(self, body: PhysicsAsset, at: str, v_rel):
        """Declare ``F_c`` on ``body`` opposing the supplied relative velocity ``v_rel``."""
        d = -_unit(_as_point(v_rel))
        return body.add_force(ForceKind.DAMPING, at=at, label=self.force_label,
                              direction=(float(d[0]), float(d[1])))


@dataclass
class TorsionSpring(Connector):
    """A spiral glyph that supplies a restoring torque about a pivot ``H``."""

    name: str = "torsion"
    at: Vec2 = (0.0, 0.0)
    rest_angle: float = 0.0
    turns: float = 2.0
    radius: float = 0.4
    color: str = COLOR_SPRING
    stroke_width: float = 3.0

    def build(self) -> VGroup:
        center = _as_point(self.at)
        thetas = np.linspace(0.0, self.turns * 2.0 * np.pi, 80)
        rs = np.linspace(0.05, self.radius, thetas.size)
        pts = [center + np.array([r * np.cos(t), r * np.sin(t), 0.0])
               for r, t in zip(rs, thetas, strict=True)]
        spiral = VMobject(color=self.color, stroke_width=self.stroke_width)
        spiral.set_points_smoothly(pts)
        self.set_keypoint("H", center[:2])
        return VGroup(spiral)

    def torque_hint(self, body_ref: str = "") -> VMobject:
        """A restoring-torque arc indicator (``COLOR_SPRING``) at the pivot."""
        from manim import Arc

        return Arc(radius=self.radius + 0.15, start_angle=0.0, angle=np.pi * 0.9,
                   arc_center=_as_point(self.at), color=self.color,
                   stroke_width=self.stroke_width)


@dataclass(frozen=True)
class HookeLaw:
    """Linear elastic law ``F = -k x``."""

    k: float = 1.0

    def force(self, x: float) -> float:
        return -self.k * x


@dataclass(frozen=True)
class LinearDamperLaw:
    """Viscous damping ``F = -c v``."""

    c: float = 1.0

    def force(self, v: float) -> float:
        return -self.c * v


@dataclass(frozen=True)
class TorsionalHookeLaw:
    """Angular elastic law ``tau = -kappa theta``."""

    kappa: float = 1.0

    def torque(self, theta: float) -> float:
        return -self.kappa * theta
