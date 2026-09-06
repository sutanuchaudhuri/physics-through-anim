"""Loads + interactions (Milestone M1.5).

Plan: plans/asset_library/M01_5_pose_rigidbody.md (loads live in core, shared by
mechanics and fluids). Separates a load's *physical* value from the *arrow length*
the renderer draws (``VectorScalePolicy``), and unifies weight/gravity under one
``InteractionKind``.

Status: SCAFFOLD (M1.5). ``arrow_length`` is unimplemented; see the test plan.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum

from physics_through_anim.physics.core.refs import PointRef, QuantityRef, SurfaceRef

Vec2 = tuple[float, float]


class VectorScalePolicy(StrEnum):
    """How the renderer turns a physical value into an arrow length."""

    FIXED = "fixed"  # every arrow the same length regardless of value
    PROPORTIONAL = "proportional"
    NORMALIZED = "normalized"
    CLIPPED = "clipped"


class InteractionKind(StrEnum):
    """The physical interaction a load represents (WEIGHT is just GRAVITY)."""

    GRAVITY = "gravity"
    NORMAL = "normal"
    FRICTION = "friction"
    APPLIED = "applied"
    TENSION = "tension"
    REACTION = "reaction"
    SPRING = "spring"
    DAMPING = "damping"


@dataclass(frozen=True)
class LoadSpec:
    """Base for anything the FBD / torque diagram draws."""

    at: PointRef | str = ""
    label: str = ""  # symbolic only (SKILL Rule 9)
    source: str | None = None  # provenance, e.g. "contact:disk.floor"


@dataclass(frozen=True)
class ForceSpec(LoadSpec):
    """A force. ``value`` is the physical magnitude (N), NOT the arrow length."""

    kind: InteractionKind = InteractionKind.APPLIED
    direction: Vec2 | str = "auto"
    value: QuantityRef | float | None = None


@dataclass(frozen=True)
class TorqueSpec(LoadSpec):
    """A torque; ``sense`` is +1 for ccw, -1 for cw."""

    kind: InteractionKind = InteractionKind.APPLIED
    sense: int = 1
    value: QuantityRef | float | None = None


@dataclass(frozen=True)
class ImpulseSpec(LoadSpec):
    """An impulse applied at a point."""

    direction: Vec2 | str = "auto"
    value: QuantityRef | float | None = None


@dataclass(frozen=True)
class DistributedLoadSpec(LoadSpec):
    """A load distributed along a surface (pressure, hydrostatic, etc.)."""

    over: SurfaceRef | str = ""
    intensity: QuantityRef | Callable | None = None  # w(s) per unit length
    direction: Vec2 | str = "normal"


def arrow_length(
    value: QuantityRef | float | None,
    policy: VectorScalePolicy,
    *,
    base: float = 1.0,
) -> float:
    """Arrow length for a load's ``value`` under ``policy``.

    ``FIXED`` returns ``base`` regardless of ``value`` (physics != length).
    """
    raise NotImplementedError("M1.5 loads.arrow_length")
