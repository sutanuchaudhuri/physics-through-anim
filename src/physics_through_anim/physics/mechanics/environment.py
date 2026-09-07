"""Static environment presets over the ``Wall`` primitive (Milestone M2).

``Ceiling`` and ``Incline`` are named angles of the one oriented-boundary
primitive (``supports.Wall``); ``Corner`` composes two walls; ``Conveyor`` is a
``Floor`` whose surface moves. None of them ever owns a force -- a wall has no
FBD; it only supplies a reaction to the touching body.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import cos, radians, sin

import numpy as np
from manim import GRAY, Line, Polygon, VGroup

from physics_through_anim.physics.core.pose import Vec2
from physics_through_anim.physics.mechanics.kinds import MotionState
from physics_through_anim.physics.mechanics.supports import GROUND_Y, Floor, Wall
from physics_through_anim.physics.mechanics.surfaces import InclineSurface


@dataclass
class Ceiling(Wall):
    """A horizontal ceiling (normal down); anchors ropes/hinges (M4)."""

    name: str = "ceiling"
    angle_deg: float = 0.0
    facing: str = "down"
    y: float = 3.0
    half_width: float = 5.5
    hatch: bool = True
    color: str = GRAY

    def __post_init__(self) -> None:
        self.center = (0.0, self.y)
        self.length = 2.0 * self.half_width
        super().__post_init__()

    def anchor(self, x: float) -> np.ndarray:
        return np.array([x, self.y, 0.0])


@dataclass
class Incline(Wall):
    """A ramp: the ``angle_deg`` wall preset seated on the floor at ``base``."""

    name: str = "incline"
    angle_deg: float = 30.0
    length: float = 5.0
    mu: float = 0.0
    base: Vec2 = (-2.0, GROUND_Y)
    on_floor: bool = True
    hatch: bool = True
    color: str = GRAY

    def __post_init__(self) -> None:
        d = np.array([cos(radians(self.angle_deg)), sin(radians(self.angle_deg)), 0.0])
        foot = np.array([self.base[0], self.base[1], 0.0])
        self.center = tuple((foot + 0.5 * self.length * d)[:2])
        super().__post_init__()

    def build(self) -> VGroup:
        theta = radians(self.angle_deg)
        d = np.array([cos(theta), sin(theta), 0.0])
        foot = np.array([self.base[0], self.base[1], 0.0])
        apex = foot + self.length * d
        group = VGroup()
        if self.on_floor:
            corner = np.array([apex[0], foot[1], 0.0])
            group.add(Polygon(foot, apex, corner, color=self.color, stroke_width=4,
                              fill_color=self.color, fill_opacity=0.15))
        group.add(Line(foot, apex, color=self.color, stroke_width=6))
        self.set_keypoint("foot", foot[:2])
        self.set_keypoint("apex", apex[:2])
        self.set_keypoint("surface_mid", (foot + 0.5 * self.length * d)[:2])
        self.set_keypoint("start", foot[:2])
        self.set_keypoint("end", apex[:2])
        return group

    def surface_at(self, s: float) -> np.ndarray:
        d = np.array([cos(radians(self.angle_deg)), sin(radians(self.angle_deg)), 0.0])
        foot = np.array([self.base[0], self.base[1], 0.0])
        return foot + s * self.length * d

    def slope_down(self) -> np.ndarray:
        """Unit vector pointing down the slope (for gravity components)."""
        theta = radians(self.angle_deg)
        return np.array([cos(theta), -sin(theta), 0.0])

    def surface(self, name: str = "incline") -> InclineSurface:
        foot = self.surface_at(0.0)
        apex = self.surface_at(1.0)
        return InclineSurface(a=(foot[0], foot[1]), b=(apex[0], apex[1]),
                              angle=radians(self.angle_deg))

    def mount_pulley(self, radius: float = 0.5, flavour="on_support",
                     standoff: float = 0.6, **kw):
        """Mount a pulley at the apex: on an immovable bracket (flavour 1) or on the top (2)."""
        from physics_through_anim.physics.mechanics.circular import PulleyMount
        from physics_through_anim.physics.mechanics.circular import mount_pulley as _mount

        theta = radians(self.angle_deg)
        apex = self.surface_at(1.0)
        normal = (-sin(theta), cos(theta))  # outward incline normal
        flav = PulleyMount(flavour) if isinstance(flavour, str) else flavour
        return _mount(apex[:2], radius=radius, flavour=flav, normal=normal,
                      standoff=standoff, **kw)


@dataclass
class Corner:
    """Two walls meeting -- a composite relation, not a new primitive."""

    a: Wall = field(default_factory=lambda: Floor())
    b: Wall = field(default_factory=lambda: Wall(angle_deg=90.0, center=(-5.0, 0.0)))

    @property
    def mobject(self) -> VGroup:
        return VGroup(self.a.mobject, self.b.mobject)

    @property
    def walls(self) -> tuple[Wall, Wall]:
        return (self.a, self.b)


@dataclass
class Conveyor(Floor):
    """A ``Floor`` (horizontal wall) whose surface moves; frozen at ``belt_speed=0``."""

    name: str = "conveyor"
    belt_speed: float = 0.0
    direction: int = 1
    mu: float = 0.4
    chevrons: int = 10
    _chevrons: VGroup = field(default_factory=VGroup, init=False)

    @property
    def motion_state(self) -> MotionState:
        return MotionState.MOVING if self.belt_speed > 0 else MotionState.AT_REST

    def build(self) -> VGroup:
        group = super().build()
        marks = VGroup()
        xs = np.linspace(-self.half_width + 0.3, self.half_width - 0.3, self.chevrons)
        for x in xs:
            marks.add(
                Line([x - 0.12, self.y + 0.12, 0], [x, self.y, 0], color=self.color, stroke_width=3)
            )
            marks.add(
                Line([x, self.y, 0], [x - 0.12, self.y - 0.12, 0], color=self.color, stroke_width=3)
            )
        self._chevrons = marks
        group.add(marks)
        return group

    def animate(self, scene, run_time: float = 3.0) -> None:
        """Scroll the belt chevrons; a no-op when the belt is frozen."""
        if self.motion_state == MotionState.AT_REST:
            scene.wait(run_time)
            return
        span = 2 * self.half_width
        wrap = span / self.chevrons
        travelled = 0.0

        def scroller(mob, dt):
            nonlocal travelled
            step = self.direction * self.belt_speed * dt
            travelled += step
            mob.shift([step, 0.0, 0.0])
            if abs(travelled) > wrap:
                mob.shift([-np.sign(step) * wrap, 0.0, 0.0])
                travelled = 0.0

        self._chevrons.add_updater(scroller)
        scene.wait(run_time)
        self._chevrons.clear_updaters()

