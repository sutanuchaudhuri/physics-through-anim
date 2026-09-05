"""Vendored rigid-body simulation over pymunk (replaces manim-physics).

Only the ``SpaceScene`` rigid-mechanics subset the lessons actually use is
reproduced here, so the project no longer depends on the unmaintained
``manim-physics==0.2.4`` (which pins ``shapely<2`` and an old Manim API, capping
Python at 3.11). ``pymunk`` alone supports current Python and Manim.

Behaviour mirrors ``manim_physics.rigid_mechanics`` 0.2.4: bodies are dynamic
pymunk bodies stepped once per frame, and each mobject is repositioned to match
its body. See SKILL.md Rule 10 for the usage gotchas this preserves
(``make_rigid_body`` before attaching visual-only markers; thin segment cushion
via stroke width; high-quality-only rendering because pymunk steps at frame dt).
"""

from __future__ import annotations

import numpy as np
import pymunk
from manim import (
    RIGHT,
    UP,
    Circle,
    Group,
    Line,
    Mobject,
    Polygon,
    Polygram,
    Rectangle,
    Scene,
    VGroup,
    VMobject,
    angle_between_vectors,
)

try:  # Manim >= 0.19 keeps the metaclass here...
    from manim.mobject.opengl.opengl_compatibility import ConvertToOpenGL
except ModuleNotFoundError:  # ...older layout as a fallback
    from manim.mobject.opengl_compatibility import ConvertToOpenGL

__all__ = ["Space", "SpaceScene", "get_shape", "get_angle"]


class Space(Mobject, metaclass=ConvertToOpenGL):
    """A non-visual mobject that owns the pymunk simulation space."""

    def __init__(self, gravity: tuple[float, float] = (0, -9.81), **kwargs):
        super().__init__(**kwargs)
        self.space = pymunk.Space()
        self.space.gravity = gravity
        self.space.sleep_time_threshold = 5


class SpaceScene(Scene):
    """Base scene for pymunk-driven rigid mechanics. Override ``GRAVITY``."""

    GRAVITY: tuple[float, float] = (0, -9.81)

    def __init__(self, renderer=None, **kwargs):
        self.space = Space(gravity=self.GRAVITY)
        super().__init__(renderer=renderer, **kwargs)

    def setup(self) -> None:
        self.add(self.space)
        self.space.add_updater(_step)

    def add_body(self, body: Mobject) -> None:
        if body.body != self.space.space.static_body:
            self.space.space.add(body.body)
        self.space.space.add(body.shape)

    def make_rigid_body(
        self,
        *mobs: Mobject,
        elasticity: float = 0.8,
        density: float = 1,
        friction: float = 0.8,
    ) -> None:
        """Make each mobject move under gravity and collisions."""
        for mob in mobs:
            if isinstance(mob, VGroup):
                return self.make_rigid_body(*mob)
            if not hasattr(mob, "body"):
                for p in mob.family_members_with_points():
                    self.add(p)
                    p.body = pymunk.Body()
                    p.body.position = p.get_x(), p.get_y()
                    get_angle(p)
                    if not hasattr(p, "angle"):
                        p.angle = 0
                    p.body.angle = p.angle
                    get_shape(p)
                    p.shape.density = density
                    p.shape.elasticity = elasticity
                    p.shape.friction = friction
                    p.spacescene = self
                    self.add_body(p)
                    p.add_updater(_simulate)
            elif mob.body.is_sleeping:
                mob.body.activate()

    def make_static_body(
        self, *mobs: Mobject, elasticity: float = 1, friction: float = 0.8
    ) -> None:
        """Make each mobject a fixed obstacle rigid bodies can collide with."""
        for mob in mobs:
            if isinstance(mob, (VGroup, Group)):
                return self.make_static_body(*mob)
            mob.body = self.space.space.static_body
            get_shape(mob)
            mob.shape.elasticity = elasticity
            mob.shape.friction = friction
            self.add_body(mob)

    def stop_rigidity(self, *mobs: Mobject) -> None:
        for mob in mobs:
            if isinstance(mob, (VGroup, Group)):
                self.stop_rigidity(*mob)
            if hasattr(mob, "body"):
                mob.body.sleep()


def _step(space: Space, dt: float) -> None:
    space.space.step(dt)


def _simulate(b: Mobject) -> None:
    x, y = b.body.position
    b.move_to(x * RIGHT + y * UP)
    b.rotate(b.body.angle - b.angle)
    b.angle = b.body.angle


def get_shape(mob: VMobject) -> None:
    """Attach a pymunk shape derived from the mobject's geometry."""
    if isinstance(mob, Circle):
        mob.shape = pymunk.Circle(body=mob.body, radius=mob.radius)
    elif isinstance(mob, Line):
        mob.shape = pymunk.Segment(
            mob.body,
            (mob.get_start()[0], mob.get_start()[1]),
            (mob.get_end()[0], mob.get_end()[1]),
            mob.stroke_width - 3.95,
        )
    elif issubclass(type(mob), Rectangle):
        width = np.linalg.norm(mob.get_vertices()[1] - mob.get_vertices()[0])
        height = np.linalg.norm(mob.get_vertices()[2] - mob.get_vertices()[1])
        mob.shape = pymunk.Poly.create_box(mob.body, (width, height))
    elif issubclass(type(mob), Polygram):
        vertices = [(a, b) for a, b, c in mob.get_vertices() - mob.get_center()]
        mob.shape = pymunk.Poly(mob.body, vertices)
    else:
        mob.shape = pymunk.Poly.create_box(mob.body, (mob.width, mob.height))


def get_angle(mob: VMobject) -> None:
    """Record the mobject's initial orientation for the simulate updater."""
    if issubclass(type(mob), Polygon):
        vec1 = mob.get_vertices()[0] - mob.get_vertices()[1]
        vec2 = type(mob)().get_vertices()[0] - type(mob)().get_vertices()[1]
        mob.angle = angle_between_vectors(vec1, vec2)
    elif isinstance(mob, Line):
        mob.angle = mob.get_angle()
