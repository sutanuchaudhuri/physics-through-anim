"""Solver-supplied state (Milestones M1.6 + M6). Scaffold.

``RigidKinematicState`` is the canonical per-entity state; ``BodyState2D`` is a
back-compat alias. ``SystemState`` is domain-generic (entities + fields +
observables) so it drives mechanics and fluids alike.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from physics_through_anim.physics.core.pose import Pose2D, Vec2


class InterpolationPolicy(StrEnum):
    """How a quantity is interpolated between trajectory samples."""

    LINEAR = "linear"
    ANGLE_UNWRAP = "angle_unwrap"  # avoid the 2*pi wrap
    STEP_LEFT = "step_left"
    STEP_RIGHT = "step_right"
    NONE = "none"


@dataclass(frozen=True)
class RigidKinematicState:
    """Per-entity kinematic state; any field may be omitted (partial state)."""

    pose: Pose2D = Pose2D()
    velocity: Vec2 | None = None
    acceleration: Vec2 | None = None
    omega: float | None = None
    alpha: float | None = None


# Back-compat alias (the M1.5 mechanics.rigidbody.BodyState2D unifies onto this at M6).
BodyState2D = RigidKinematicState


@dataclass(frozen=True)
class AssetState:
    """Per-asset state: a body kinematic state plus optional evolving shape (chains)."""

    body: RigidKinematicState | None = None
    shape: object | None = None


@dataclass(frozen=True)
class SystemState:
    """One consistent state for the whole system at a time t."""

    entities: Mapping = field(default_factory=dict)
    fields: Mapping = field(default_factory=dict)
    observables: Mapping = field(default_factory=dict)


@dataclass(frozen=True)
class StateSnapshot:
    """A declarative freeze-frame teaching request."""

    t: float = 0.0
    phase: str = "before"
    show: tuple[str, ...] = ("body",)
    label: str | None = None
