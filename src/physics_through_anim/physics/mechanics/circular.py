"""Round rolling/rotation bodies (Milestone M3).

``CircularBody`` and its presets (``Disk``, ``Ring``/``Hoop``, ``Sphere2D``,
``Cylinder``) are drawable rigid bodies whose point kinematics reuse the generic
Rule 5 rolling-velocity field. Any of them accepts an optional ``skin`` mobject
-- a rock, wheel, barrel, or image -- so the *picture* is decoupled from the
disk *physics* (see ``plans/asset_library/RENDER_MASK.md`` /
``M03_rolling_rotation.md``). ``Pulley`` is a spinnable wheel with named rim
tangent points for ropes (M4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from math import cos, sin

import numpy as np
from manim import BLUE, GRAY, YELLOW, Circle, Dot, Line, Mobject, VGroup

from physics_through_anim.physics.mechanics.base import PhysicsAsset
from physics_through_anim.physics.mechanics.constraints import FixedAxleConstraint
from physics_through_anim.physics.mechanics.kinds import BodyDynamics, ForceKind, MotionState
from physics_through_anim.physics.mechanics.supports import Support

Vec2 = tuple[float, float]


@dataclass
class CircularBody(PhysicsAsset):
    """A round rigid body that can roll; ``skin`` overrides its picture."""

    name: str = "disk"
    mass: float = 1.0
    position: Vec2 = (0.0, 0.0)
    radius: float = 0.6
    inertia_factor: float = 0.5  # I = factor * m * R^2  (0.5 disk, 1.0 hoop, 0.4 sphere)
    color: str | None = None
    fill_opacity: float = 0.25
    motion_state: MotionState = MotionState.AT_REST
    omega: float = 0.0
    show_cm: bool = True
    show_weight: bool = True
    show_spoke: bool = True
    label: str | None = "m"
    skin: Mobject | None = None  # any mobject (rock/wheel/image); rides the rolling pose
    dynamics: BodyDynamics = BodyDynamics.DYNAMIC

    def build(self) -> VGroup:
        cx, cy = self.position
        color = self.color or BLUE
        circle = Circle(radius=self.radius, color=color, fill_color=color,
                        fill_opacity=self.fill_opacity, stroke_width=5).move_to([cx, cy, 0.0])
        group = VGroup(circle)
        if self.skin is not None:
            self.skin.set(width=2.0 * self.radius).move_to([cx, cy, 0.0])
            circle.set_opacity(0.0)  # keep the disk as an invisible physics guide
            group.add(self.skin)
        if self.show_spoke:
            group.add(Line([cx, cy, 0.0], [cx + self.radius, cy, 0.0],
                           color=YELLOW, stroke_width=4))
        self.set_keypoint("CM", [cx, cy])
        self.set_keypoint("top", [cx, cy + self.radius])
        self.set_keypoint("bottom", [cx, cy - self.radius])
        self.set_keypoint("left", [cx - self.radius, cy])
        self.set_keypoint("right", [cx + self.radius, cy])
        if self.show_cm:
            group.add(Dot([cx, cy, 0.0], color=YELLOW, radius=0.06))
        if self.show_weight:
            self.add_force(ForceKind.WEIGHT, at="CM", label="mg", direction="down")
        return group

    def rim_at(self, theta: float) -> np.ndarray:
        """Rim point at angle ``theta`` -> ``CM + R (cos, sin)``."""
        cm = self.keypoint("CM")
        return cm + self.radius * np.array([cos(theta), sin(theta), 0.0])

    def contact_point(self) -> np.ndarray:
        """The rolling contact ``P`` (set when placed), else the bottom rim."""
        return self.keypoints.get("contact", self.keypoint("bottom"))

    def point_velocity(self, point, v_cm: float) -> np.ndarray:
        """Rolling velocity field: ``omega x (point - P)`` (Rule 5, perp to P->point)."""
        p = np.asarray(point, dtype=float)
        r = p - self.contact_point()
        omega = v_cm / self.radius
        return omega * np.array([-r[1], r[0], 0.0])


@dataclass
class Disk(CircularBody):
    inertia_factor: float = 0.5


@dataclass
class Ring(CircularBody):
    name: str = "ring"
    inertia_factor: float = 1.0
    fill_opacity: float = 0.0


Hoop = Ring


@dataclass
class Sphere2D(CircularBody):
    name: str = "sphere"
    inertia_factor: float = 0.4


@dataclass
class Cylinder(CircularBody):
    name: str = "cylinder"
    show_cross_section: bool = True

    def build(self) -> VGroup:
        group = super().build()
        if self.show_cross_section:
            cx, cy = self.position
            hatch = VGroup()
            for dx in np.linspace(-self.radius * 0.7, self.radius * 0.7, 5):
                half = float(np.sqrt(max(self.radius**2 - dx**2, 0.0))) * 0.9
                hatch.add(Line([cx + dx, cy - half, 0.0], [cx + dx, cy + half, 0.0],
                               color=self.color or BLUE, stroke_width=1.5))
            group.add(hatch)
        return group


@dataclass
class Pulley(PhysicsAsset):
    """A spinnable wheel with named rim tangent points where ropes leave (M4)."""

    name: str = "pulley"
    center: Vec2 = (0.0, 2.0)
    radius: float = 0.5
    rotates: bool = True
    rope_angles: dict[str, float] = field(default_factory=lambda: {"A": 30.0, "B": 60.0})
    color: str = GRAY
    dynamics: BodyDynamics = BodyDynamics.STATIC

    def build(self) -> VGroup:
        cx, cy = self.center
        group = VGroup(
            Circle(radius=self.radius, color=self.color, stroke_width=5).move_to([cx, cy, 0.0]),
            Dot([cx, cy, 0.0], color=YELLOW, radius=0.05),
        )
        self.set_keypoint("axle", [cx, cy])
        for name in self.rope_angles:
            self.set_keypoint(name, self.rim_point(name))
        return group

    def rim_point(self, name: str) -> np.ndarray:
        theta = np.radians(self.rope_angles[name])
        cx, cy = self.center
        return np.array([cx + self.radius * cos(theta), cy + self.radius * sin(theta), 0.0])


class PulleyMount(StrEnum):
    """How a pulley axle is fixed to a mounting point (e.g. an incline apex)."""

    ON_SUPPORT = "on_support"  # flavour 1: axle held off the point by an immovable bracket
    AT_POINT = "at_point"  # flavour 2: axle coincides with the point


@dataclass
class PulleyBracket(Support):
    """An immovable bracket: a hatched pad at ``base`` and a post up to the ``axle``."""

    name: str = "bracket"
    base: Vec2 = (0.0, 0.0)
    axle: Vec2 = (0.0, 1.0)
    color: str = GRAY
    stroke_width: float = 5.0

    def build(self) -> VGroup:
        base = np.array([self.base[0], self.base[1], 0.0])
        axle = np.array([self.axle[0], self.axle[1], 0.0])
        d = axle - base
        n = float(np.linalg.norm(d))
        u = d / n if n > 1e-9 else np.array([0.0, 1.0, 0.0])
        perp = np.array([-u[1], u[0], 0.0])
        group = VGroup(Line(base, axle, color=self.color, stroke_width=self.stroke_width))
        group.add(Line(base - perp * 0.28, base + perp * 0.28,
                       color=self.color, stroke_width=self.stroke_width))
        group.add(VGroup(*[
            Line(base + perp * x, base + perp * x - u * 0.18 - perp * 0.12,
                 color=self.color, stroke_width=2)
            for x in np.linspace(-0.24, 0.24, 5)
        ]))
        self.set_keypoint("base", base[:2])
        self.set_keypoint("axle", axle[:2])
        return group


@dataclass
class MountedPulley:
    """A pulley plus its (optional) immovable bracket and its fixed-axle constraint."""

    pulley: Pulley
    bracket: PulleyBracket | None
    axle: FixedAxleConstraint


def mount_pulley(point, radius: float = 0.5, flavour: PulleyMount = PulleyMount.ON_SUPPORT,
                 normal: Vec2 = (0.0, 1.0), standoff: float = 0.6, name: str = "pulley",
                 **pulley_kw) -> MountedPulley:
    """Mount a pulley at ``point``: on an immovable bracket (flavour 1) or axle-on-point (2)."""
    p = np.asarray(point, dtype=float)[:2]
    nrm = np.asarray(normal, dtype=float)[:2]
    ln = float(np.linalg.norm(nrm))
    nrm = nrm / ln if ln > 1e-9 else np.array([0.0, 1.0])
    if flavour == PulleyMount.AT_POINT:
        center, bracket = p, None
    else:
        center = p + nrm * standoff
        bracket = PulleyBracket(base=(float(p[0]), float(p[1])),
                                axle=(float(center[0]), float(center[1])))
    pulley = Pulley(name=name, center=(float(center[0]), float(center[1])),
                    radius=radius, **pulley_kw)
    axle = FixedAxleConstraint(participants=(name,), at="axle", to="mount")
    return MountedPulley(pulley=pulley, bracket=bracket, axle=axle)
