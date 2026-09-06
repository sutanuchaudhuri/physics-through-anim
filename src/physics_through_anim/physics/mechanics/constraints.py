"""Typed constraints (Milestones M4/M7). Scaffold.

Inspectable dataclasses, never ``Constraint(kind=..., data=dict)``.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PinConstraint:
    participants: tuple[str, ...] = ()
    at: str = ""
    active: bool = True


@dataclass
class FixedPointConstraint:
    participants: tuple[str, ...] = ()
    point: str = ""
    active: bool = True


@dataclass
class DistanceConstraint:
    participants: tuple[str, ...] = ()
    distance: float = 1.0
    active: bool = True


@dataclass
class RopeLengthConstraint:
    participants: tuple[str, ...] = ()
    length: float = 1.0
    active: bool = True


@dataclass
class RollingConstraint:
    participants: tuple[str, ...] = ()
    radius: float = 1.0
    active: bool = True


@dataclass
class PathConstraint:
    participants: tuple[str, ...] = ()
    path: str = ""
    active: bool = True


@dataclass
class SlotConstraint:
    participants: tuple[str, ...] = ()
    slot: str = ""
    active: bool = True


@dataclass
class FixedAxleConstraint:
    participants: tuple[str, ...] = ()
    at: str = ""
    to: str = ""
    active: bool = True


@dataclass
class ContactLockConstraint:
    """Activated by a perfectly inelastic impact (drops a DOF; bodies not merged)."""

    participants: tuple[str, ...] = ()
    gap: float = 0.0
    active: bool = True
