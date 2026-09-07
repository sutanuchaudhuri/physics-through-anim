"""Distributed-mass bodies / chains (Milestone M11).

A ``DistributedBody`` has a material coordinate ``s in [0, 1]`` and an evolving
shape supplied by a scene ``path(s) -> world`` (solver-free: the time evolution
comes from a trajectory/updater, not from inside the asset). ``Chain`` renders
that shape ``CONTINUOUS`` or ``LINKED``; ``ElasticString``/``MassiveSpring``/
``FlexibleRod`` share the same architecture. Shape travels in the generic
``SystemState`` via ``AssetState.shape``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

import numpy as np
from manim import GRAY, ORANGE, YELLOW, Dot, Line, Mobject, VGroup, VMobject

from physics_through_anim.physics.mechanics.base import PhysicsAsset


class ChainRender(StrEnum):
    CONTINUOUS = "continuous"
    LINKED = "linked"


@dataclass(frozen=True)
class ChainShapeState:
    """Material coord s in [0, 1] -> world point, carried in AssetState.shape."""

    path: Callable[[float], np.ndarray] | None = None


def _v3(p) -> np.ndarray:
    a = np.asarray(p, dtype=float)
    return a if a.shape[0] == 3 else np.array([a[0], a[1], 0.0])


PathFn = Callable[[float], np.ndarray]
SkinBuilder = Callable[[PathFn], Mobject]


@dataclass
class DistributedBody(PhysicsAsset):
    """Base for any body with a material coordinate + an evolving shape."""

    name: str = "distributed"
    render: ChainRender = ChainRender.CONTINUOUS
    mass: float = 1.0
    length: float = 3.0
    n_links: int = 20
    path: Callable[[float], np.ndarray] | None = None
    material_markers: tuple[float, ...] = ()
    color: str = GRAY
    stroke_width: float = 4.0
    # A garment/skin drawn ON TOP of the skeleton line. ``skin_builder(path) ->
    # Mobject`` (supplied by the render layer) keeps mechanics render-free; the
    # skeleton stays the physical vector, the skin is cosmetic and can be faded.
    skin_builder: Callable[[Callable[[float], np.ndarray]], Mobject] | None = None
    skin: Mobject | None = None

    @property
    def linear_density(self) -> float:
        return self.mass / self.length if self.length else 0.0

    def _path(self) -> Callable[[float], np.ndarray]:
        if self.path is not None:
            return self.path
        start = np.array([-self.length / 2.0, 0.0, 0.0])
        end = np.array([self.length / 2.0, 0.0, 0.0])
        return lambda s: start + s * (end - start)

    def _sample(self, n: int) -> list[np.ndarray]:
        p = self._path()
        return [_v3(p(float(s))) for s in np.linspace(0.0, 1.0, n)]

    def _draw(self) -> VGroup:
        if self.render is ChainRender.CONTINUOUS:
            curve = VMobject(color=self.color, stroke_width=self.stroke_width)
            curve.set_points_smoothly(self._sample(max(self.n_links + 1, 2)))
            return VGroup(curve)
        nodes = self._sample(self.n_links + 1)
        return VGroup(*[
            Line(nodes[i], nodes[i + 1], color=self.color, stroke_width=6)
            for i in range(self.n_links)
        ])

    def _set_keypoints(self) -> None:
        p = self._path()
        self.set_keypoint("A", _v3(p(0.0))[:2])
        self.set_keypoint("B", _v3(p(1.0))[:2])
        cm = np.mean(self._sample(max(self.n_links + 1, 2)), axis=0)
        self.set_keypoint("CM", cm[:2])
        for s in self.material_markers:
            self.set_keypoint(f"mark@{s}", _v3(p(float(s)))[:2])

    def build(self) -> VGroup:
        group = self._draw()
        self._set_keypoints()
        self._build_skin()
        return group

    def _build_skin(self) -> None:
        """(Re)build the cosmetic garment from ``skin_builder`` if one is set."""
        if self.skin_builder is None:
            return
        rebuilt = self.skin_builder(self._path())
        if self.skin is not None and hasattr(self.skin, "become"):
            self.skin.become(rebuilt)
        else:
            self.skin = rebuilt

    def set_path(self, new_path: Callable[[float], np.ndarray]) -> DistributedBody:
        """Rebuild the shape from a new ``path`` (used each frame for motion)."""
        self.path = new_path
        self.mobject.become(self._draw())
        self._set_keypoints()
        self._build_skin()
        return self

    def attach_skin(self, skin_builder: SkinBuilder) -> Mobject:
        """Attach a garment builder and build it now; returns the skin mobject."""
        self.skin_builder = skin_builder
        self._build_skin()
        return self.skin

    def com(self) -> np.ndarray:
        """Mass-weighted centre of mass of the current shape (uniform density)."""
        return self.keypoint("CM")

    def material_marker(self, s: float) -> Dot:
        """A visible tag on one material piece (which piece is which)."""
        return Dot(_v3(self._path()(float(s))), color=YELLOW, radius=0.07)

    def portion(self, s0: float, s1: float, color: str = ORANGE, n: int = 24) -> VMobject:
        """A sub-curve between material coords ``s0`` and ``s1`` (e.g. supported vs free)."""
        p = self._path()
        pts = [_v3(p(s0 + (s1 - s0) * i / n)) for i in range(n + 1)]
        sub = VMobject(color=color, stroke_width=6)
        sub.set_points_smoothly(pts)
        return sub


@dataclass
class Chain(DistributedBody):
    """A distributed-mass chain: links or a continuous strand along a material coord."""

    name: str = "chain"
    label: str = "chain"


@dataclass
class ElasticString(DistributedBody):
    """A stretchy string/cable with give (distributed mass)."""

    name: str = "string"
    natural_length: float = 1.0


@dataclass
class MassiveSpring(DistributedBody):
    """A spring WITH mass (unlike M10's ideal ``LinearSpring``)."""

    name: str = "massive_spring"
    natural_length: float = 1.0


@dataclass
class FlexibleRod(DistributedBody):
    """A bendable rod (distributed mass)."""

    name: str = "flex_rod"
