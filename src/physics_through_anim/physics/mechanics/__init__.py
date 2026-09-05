"""Composable 2D mechanics assets (Milestone 1).

See plans/physics_asset_library.md. Public API is curated here so scenes import
from ``physics_through_anim.physics.mechanics``.
"""

from physics_through_anim.physics.mechanics.assembly import Assembly
from physics_through_anim.physics.mechanics.base import ForceSpec, PhysicsAsset
from physics_through_anim.physics.mechanics.bodies import Block, RectangularMass
from physics_through_anim.physics.mechanics.kinds import (
    BodyDynamics,
    ContactPersistence,
    ContactRegime,
    ForceKind,
    MotionState,
    Phase,
)
from physics_through_anim.physics.mechanics.supports import Floor, Support

__all__ = [
    "Assembly",
    "Block",
    "BodyDynamics",
    "ContactPersistence",
    "ContactRegime",
    "Floor",
    "ForceKind",
    "ForceSpec",
    "MotionState",
    "Phase",
    "PhysicsAsset",
    "RectangularMass",
    "Support",
]
