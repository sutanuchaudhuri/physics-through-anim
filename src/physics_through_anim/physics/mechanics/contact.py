"""Contact as a semantic relation (Milestone M2).

A contact is a relationship, not a drawable (its dot/tangent/normal glyphs live
in ``overlays/contact.py``). Its three orthogonal aspects are separate enums, and
its geometric location comes from a ``ContactLocator`` -- separating *where* the
contact is (geometry) from *which material occupies it* (pairing/kinematics).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol

import numpy as np

from physics_through_anim.physics.core.pose import Vec2


class ContactGeometry(StrEnum):
    POINT = "point"
    PATCH = "patch"
    LINE = "line"


class MaterialPairing(StrEnum):
    SAME = "same"
    CHANGING = "changing"


class ContactKinematics(StrEnum):
    STICKING = "sticking"
    SLIDING = "sliding"
    ROLLING_NO_SLIP = "rolling_no_slip"
    ROLLING_WITH_SLIP = "rolling_with_slip"


class FrictionModel(StrEnum):
    FRICTIONLESS = "frictionless"
    COULOMB = "coulomb"
    CUSTOM = "custom"


class ContactLifecycle(StrEnum):
    ESTABLISHING = "establishing"
    ACTIVE = "active"
    SEPARATING = "separating"


@dataclass(frozen=True)
class ContactFrame:
    """The resolved contact geometry: a point plus unit tangent/normal."""

    point: np.ndarray
    tangent: np.ndarray
    normal: np.ndarray


class ContactLocator(Protocol):
    """Resolves the geometric contact frame from the system state."""

    def locate(self, system_state) -> ContactFrame: ...


def _frame(point: Vec2, tangent: Vec2 = (1.0, 0.0), normal: Vec2 = (0.0, 1.0)) -> ContactFrame:
    return ContactFrame(
        point=np.array([point[0], point[1], 0.0]),
        tangent=np.array([tangent[0], tangent[1], 0.0]),
        normal=np.array([normal[0], normal[1], 0.0]),
    )


@dataclass(frozen=True)
class FixedWorldPoint:
    """A contact pinned to a fixed world point (e.g. a resting patch centre)."""

    point: Vec2 = (0.0, 0.0)
    tangent: Vec2 = (1.0, 0.0)
    normal: Vec2 = (0.0, 1.0)

    def locate(self, system_state=None) -> ContactFrame:
        return _frame(self.point, self.tangent, self.normal)


@dataclass(frozen=True)
class SurfaceCoordinate:
    """A contact at parameter ``s`` on a surface (``s`` may vary with time)."""

    surface: object  # a Surface (point_at/tangent_at/normal_at)
    s: float | Callable[[object], float] = 0.0

    def locate(self, system_state=None) -> ContactFrame:
        s = self.s(system_state) if callable(self.s) else self.s
        p = self.surface.point_at(s)
        t = self.surface.tangent_at(s)
        n = self.surface.normal_at(s)
        return ContactFrame(point=p, tangent=t, normal=n)


@dataclass(frozen=True)
class BodyKeypoint:
    """A contact riding a body keypoint, resolved from the system state."""

    body: object  # exposes keypoint(key)
    key: str = "P"
    tangent: Vec2 = (1.0, 0.0)
    normal: Vec2 = (0.0, 1.0)

    def locate(self, system_state=None) -> ContactFrame:
        p = self.body.keypoint(self.key)
        return _frame((float(p[0]), float(p[1])), self.tangent, self.normal)


@dataclass
class Contact:
    """A body-touches-surface relationship (no mobject)."""

    body: str = ""
    surface: str = ""
    locator: ContactLocator | None = None
    kinematics: ContactKinematics = ContactKinematics.STICKING
    friction: FrictionModel = FrictionModel.COULOMB
    lifecycle: ContactLifecycle = ContactLifecycle.ACTIVE
    geometry: ContactGeometry = ContactGeometry.POINT
    pairing: MaterialPairing = MaterialPairing.SAME
    mu: float = 0.0
    tangent: Vec2 | None = field(default=None)
    normal: Vec2 | None = field(default=None)

    def frame_at(self, system_state=None) -> ContactFrame:
        """The resolved contact frame (point/tangent/normal) from the locator."""
        if self.locator is None:
            raise ValueError("Contact has no locator; cannot resolve a frame.")
        return self.locator.locate(system_state)

    def transition_to(self, lifecycle: ContactLifecycle) -> Contact:
        """Move through the contact lifecycle (ESTABLISHING -> ACTIVE -> SEPARATING)."""
        self.lifecycle = lifecycle
        return self

    def on_separation(self, body=None, *, normal_label: str = "N") -> Contact:
        """Mark the contact separating (N -> 0); drop the normal force from ``body``'s FBD."""
        self.lifecycle = ContactLifecycle.SEPARATING
        if body is not None:
            body.forces = [f for f in body.forces if f.label != normal_label]
        return self

