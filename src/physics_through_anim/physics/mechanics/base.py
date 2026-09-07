"""Base class and force-declaration atom for mechanics assets.

An *asset* owns a manim ``VGroup`` (``asset.mobject``), a dict of named world
-space ``keypoints`` (CM, contact P, rope ends A/B, hinge H...), and a list of
declared ``ForceSpec``s that drive its free-body diagram. Geometry is built
once in ``__post_init__`` via the subclass ``build()``; ``shift`` moves both the
mobject and every keypoint together so placement stays consistent.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from manim import VGroup

from physics_through_anim.physics.mechanics.kinds import BodyDynamics, ForceKind


@dataclass(frozen=True)
class ForceSpec:
    """One declared force, drawn at a named keypoint by the FBD layer."""

    kind: ForceKind
    at: str  # keypoint name on the owning asset ("CM", "P", "A"...)
    label: str  # symbolic only, e.g. "mg", "N", "f_s", "T_A" (SKILL Rule 9)
    direction: tuple[float, float] | str = "auto"  # unit vector or keyword
    magnitude: float | None = None  # for relative arrow lengths; None = default


def _as_point(value) -> np.ndarray:
    """Coerce a 2- or 3-tuple/array into a 3D manim point."""
    arr = np.asarray(value, dtype=float)
    if arr.shape == (2,):
        return np.array([arr[0], arr[1], 0.0])
    return arr


@dataclass
class PhysicsAsset:
    """Base for every drawable mechanics asset."""

    name: str = "asset"
    label: str | None = None
    dynamics: BodyDynamics = BodyDynamics.DYNAMIC
    keypoints: dict[str, np.ndarray] = field(default_factory=dict, init=False)
    forces: list[ForceSpec] = field(default_factory=list, init=False)
    mobject: VGroup = field(default_factory=VGroup, init=False)
    _applied_angle: float = field(default=0.0, init=False)  # tracks apply_state rotation
    _state: object = field(default=None, init=False)  # last applied kinematic state

    def __post_init__(self) -> None:
        self.mobject = self.build()

    def build(self) -> VGroup:
        """Construct the mobject and populate ``self.keypoints``. Override."""
        raise NotImplementedError

    def set_keypoint(self, key: str, point) -> None:
        self.keypoints[key] = _as_point(point)

    def keypoint(self, key: str) -> np.ndarray:
        if key not in self.keypoints:
            raise KeyError(f"'{self.name}' has no keypoint '{key}'. Known: {list(self.keypoints)}")
        return self.keypoints[key]

    def add_force(
        self,
        kind: ForceKind,
        at: str,
        label: str,
        direction: tuple[float, float] | str = "auto",
        magnitude: float | None = None,
    ) -> ForceSpec:
        """Declare a force at a keypoint; returns the spec (also stored)."""
        spec = ForceSpec(kind=kind, at=at, label=label, direction=direction, magnitude=magnitude)
        self.forces.append(spec)
        return spec

    def shift(self, delta) -> PhysicsAsset:
        """Translate the mobject and every keypoint by ``delta`` (2D or 3D)."""
        vec = _as_point(delta)
        self.mobject.shift(vec)
        for key in self.keypoints:
            self.keypoints[key] = self.keypoints[key] + vec
        return self

    def rotate(self, angle: float, about=None) -> PhysicsAsset:
        """Rotate the mobject and every keypoint by ``angle`` about a pivot (default CM)."""
        pivot = _as_point(about) if about is not None else self.keypoints["CM"]
        self.mobject.rotate(angle, about_point=pivot)
        c, s = np.cos(angle), np.sin(angle)
        for key, point in self.keypoints.items():
            rel = point - pivot
            self.keypoints[key] = pivot + np.array([c * rel[0] - s * rel[1],
                                                    s * rel[0] + c * rel[1], 0.0])
        return self

    def apply_state(self, state) -> PhysicsAsset:
        """Move the asset to a supplied kinematic ``state`` (absolute pose, no drift).

        ``state`` is a ``RigidKinematicState`` (``.pose``) or an ``AssetState``
        (``.body``). Rotation is tracked so repeated updater calls never accumulate.
        """
        pose = getattr(state, "pose", None)
        if pose is None:
            pose = getattr(getattr(state, "body", None), "pose", None)
        if pose is None:
            return self
        self.rotate(pose.angle - self._applied_angle)
        self._applied_angle = pose.angle
        cm = self.keypoints["CM"]
        target = np.array([pose.position[0], pose.position[1], 0.0])
        self.shift(target - cm)
        self._state = state
        return self

    def fbd(self, include=None) -> VGroup:
        """Render this asset's declared forces as arrows (SKILL Rule 2 colours)."""
        from physics_through_anim.physics.mechanics.fbd import render_forces

        return render_forces(self, include=include)
