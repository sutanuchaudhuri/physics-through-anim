"""Contact as a semantic relation (Milestone M2). Scaffold.

A contact is a relationship, not a drawable. Its three orthogonal aspects are
separate enums; the geometric location comes from a ``ContactLocator``.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


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


class ContactLocator(Protocol):
    """Resolves the geometric contact frame from the system state."""

    def locate(self, system_state) -> object: ...


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

    def frame_at(self, system_state) -> object:
        raise NotImplementedError("M2 Contact.frame_at")
