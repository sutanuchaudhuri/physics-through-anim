"""Springs / dampers + constitutive laws (Milestone M10). Scaffold.

Geometry (``LinearSpring``) is separate from the force law (``HookeLaw``).
Extension/compression are derived signals, not enums.
"""

from __future__ import annotations

from dataclasses import dataclass

from physics_through_anim.physics.core.pose import Vec2


@dataclass
class LinearSpring:
    from_point: Vec2 = (0.0, 0.0)
    to_point: Vec2 = (1.0, 0.0)
    natural_length: float = 1.0
    coils: int = 8
    width: float = 0.25
    current_length: float = 1.0

    def deformation(self) -> float:
        """current_length - natural_length (>0 stretch, <0 compress)."""
        raise NotImplementedError("M10 LinearSpring.deformation")

    def extension(self) -> float:
        raise NotImplementedError("M10 LinearSpring.extension")

    def compression(self) -> float:
        raise NotImplementedError("M10 LinearSpring.compression")


Spring = LinearSpring


@dataclass
class Damper:
    from_point: Vec2 = (0.0, 0.0)
    to_point: Vec2 = (1.0, 0.0)


@dataclass
class TorsionSpring:
    at: Vec2 = (0.0, 0.0)
    rest_angle: float = 0.0


@dataclass(frozen=True)
class HookeLaw:
    k: float = 1.0

    def force(self, x: float) -> float:
        """F = -k x."""
        raise NotImplementedError("M10 HookeLaw.force")


@dataclass(frozen=True)
class LinearDamperLaw:
    c: float = 1.0

    def force(self, v: float) -> float:
        raise NotImplementedError("M10 LinearDamperLaw.force")
