"""Cosmetic masks: a visual skin for a point mass (render engine only).

A **mask** is the *cosmetic* picture of a body -- an image, sprite, SVG, a Manim
mobject, or a raw matrix -- that stands in for what the physics treats as a
**point mass at its centre of mass**. A boat drifting, a human running, a stone
thrown: physically each is a point mass located at a CM with force/velocity
vectors and lever arms; their drawing (hull, runner, pebble) is only a skin.

Two hard separations the render engine enforces (documented in
``plans/asset_library/RENDER_MASK.md``):

1. **Geometry is cosmetic; the CM is physical.** The physics never reads a mask's
   shape -- it uses the CM (a point) plus the physically meaningful vectors and
   lever arms. A mask may even be fully transparent (``opacity=0``): the body is
   still a point mass, the picture is just hidden.
2. **Mask rotation is cosmetic; vector/lever-arm rotation is physical.** Spinning
   a stone's sprite is decoration. What determines the torque is the *lever arm*
   ``r`` (CM -> point of application) and the *force vector* ``F`` rotating --
   those are drawn by the kinematics/overlay layers, not by the mask.

The mask therefore only ever *follows* a supplied ``Pose2D`` (the CM pose). It
carries no physics and nothing depends on ``render``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import cos, sin
from pathlib import Path
from typing import Any

import numpy as np
from manim import ImageMobject, Mobject, VMobject

from physics_through_anim.physics.core.pose import Pose2D, Vec2


def _to_mobject(source: Any) -> Mobject:
    """Coerce a mobject / image path / matrix into a cosmetic Manim mobject."""
    if isinstance(source, Mobject):
        return source
    if isinstance(source, (str, Path)):
        return ImageMobject(str(source))
    return ImageMobject(np.asarray(source))  # a raw matrix -> greyscale/RGBA image


def _apply_opacity(mob: Mobject, opacity: float) -> None:
    if hasattr(mob, "set_opacity"):
        mob.set_opacity(opacity)


def _rot(v: Vec2, theta: float) -> np.ndarray:
    c, s = cos(theta), sin(theta)
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1], 0.0])


@dataclass
class Mask:
    """A cosmetic visual skin bound to a point mass at its CM.

    ``source`` is a Manim ``Mobject``, an image path, or a numpy matrix. The mask
    tracks the CM pose via :meth:`place`; ``cosmetic_rotation`` decides whether the
    picture spins with the pose (decoration) or stays upright while the physical
    vectors/lever arms (drawn elsewhere) carry the meaningful rotation.
    """

    source: Any
    cm_local: Vec2 = (0.0, 0.0)  # CM offset from the mask centre, in mask-local coords
    scale: float = 1.0
    opacity: float = 1.0
    cosmetic_rotation: bool = True
    mobject: Mobject = field(init=False)
    _angle: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        mob = _to_mobject(self.source)
        if self.scale != 1.0:
            mob.scale(self.scale)
        _apply_opacity(mob, self.opacity)
        self.mobject = mob

    @classmethod
    def from_matrix(cls, matrix, **kwargs) -> Mask:
        """A mask from a raw 2-D/3-D array (rendered as an image)."""
        return cls(source=np.asarray(matrix), **kwargs)

    @classmethod
    def transparent(cls, source: Any, **kwargs) -> Mask:
        """An invisible mask: the body stays a point mass; the skin is hidden."""
        kwargs.setdefault("opacity", 0.0)
        return cls(source=source, **kwargs)

    def place(self, pose: Pose2D) -> Mobject:
        """Follow the CM ``pose``: seat the CM at ``pose.position``.

        Rotation is applied only when ``cosmetic_rotation`` is set; either way the
        CM (not the mask centre) is the anchor, so the point-mass invariant holds.
        """
        theta = pose.angle if self.cosmetic_rotation else 0.0
        self.mobject.rotate(theta - self._angle, about_point=self.mobject.get_center())
        self._angle = theta
        cm_world = self.mobject.get_center() + _rot(self.cm_local, theta)
        target = np.array([pose.position[0], pose.position[1], 0.0])
        self.mobject.shift(target - cm_world)
        return self.mobject


def _v3(p) -> np.ndarray:
    a = np.asarray(p, dtype=float)
    return a if a.shape[0] == 3 else np.array([a[0], a[1], 0.0])


def garment_along_path(path, *, width: float = 0.35, n: int = 60, color: Any = "#74C0FC",
                       opacity: float = 0.4, stroke_width: float = 0.0) -> VMobject:
    """A closed, semi-transparent ribbon that hugs ``path(s)`` (s in [0, 1]).

    Built by offsetting the sampled path by ``±width/2`` along its local normal; the
    result is a filled *garment* meant to be drawn on top of a skeleton line and
    faded to reveal it.
    """
    pts = [_v3(path(i / n)) for i in range(n + 1)]
    top, bot = [], []
    for i, p in enumerate(pts):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        tangent = b - a
        length = float(np.linalg.norm(tangent))
        normal = np.array([-tangent[1], tangent[0], 0.0]) / length if length > 1e-9 \
            else np.array([0.0, 1.0, 0.0])
        top.append(p + normal * width / 2.0)
        bot.append(p - normal * width / 2.0)
    outline = [*top, *bot[::-1], top[0]]
    ribbon = VMobject(stroke_width=stroke_width)
    ribbon.set_points_as_corners(outline)
    ribbon.set_fill(color=color, opacity=opacity)
    ribbon.set_stroke(color=color, width=stroke_width, opacity=min(1.0, opacity + 0.3))
    return ribbon


@dataclass
class PathMask:
    """A transparent garment that follows a distributed body's path (its skeleton).

    Renders on top of the skeleton line; fade its opacity (or ``FadeOut``) to reveal
    the underlying vector. ``as_builder`` yields the plain callable a mechanics
    ``DistributedBody`` stores as ``skin_builder`` -- so ``mechanics`` never imports
    ``render``.
    """

    width: float = 0.35
    color: Any = "#74C0FC"
    opacity: float = 0.4
    n: int = 60
    stroke_width: float = 0.0
    mobject: VMobject | None = field(default=None, init=False)

    def build(self, path) -> VMobject:
        """Build the garment for ``path`` and remember it."""
        self.mobject = garment_along_path(
            path, width=self.width, n=self.n, color=self.color,
            opacity=self.opacity, stroke_width=self.stroke_width)
        return self.mobject

    def follow(self, path) -> VMobject:
        """Reshape the existing garment to a new ``path`` (in place)."""
        rebuilt = garment_along_path(
            path, width=self.width, n=self.n, color=self.color,
            opacity=self.opacity, stroke_width=self.stroke_width)
        if self.mobject is None:
            self.mobject = rebuilt
        else:
            self.mobject.become(rebuilt)
        return self.mobject

    def as_builder(self):
        """A ``path -> Mobject`` callable for ``DistributedBody.skin_builder``."""
        return lambda path: garment_along_path(
            path, width=self.width, n=self.n, color=self.color,
            opacity=self.opacity, stroke_width=self.stroke_width)
