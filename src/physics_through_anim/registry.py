from __future__ import annotations

from dataclasses import dataclass

from physics_through_anim.lessons.foundations import (
    SHM,
    CircularMotion,
    Energy,
    FluidMechanics,
    Kinematics,
    Momentum,
    NewtonsLaws,
    OrbitalMechanics,
    RotationalMotion,
    Vectors,
)


@dataclass(frozen=True)
class Topic:
    title: str
    scene_name: str
    narration: str
    scene_class: type


TOPICS: dict[str, Topic] = {
    "vectors": Topic("Vectors", "Vectors", "Direction and magnitude.", Vectors),
    "kinematics": Topic(
        "Kinematics", "Kinematics", "Position, velocity, and acceleration.", Kinematics
    ),
    "newtons_laws": Topic("Newton's Laws", "NewtonsLaws", "Forces change motion.", NewtonsLaws),
    "circular_motion": Topic(
        "Circular Motion", "CircularMotion", "Acceleration can turn motion.", CircularMotion
    ),
    "momentum": Topic(
        "Conservation of Momentum",
        "Momentum",
        "Motion is transferred in an isolated system.",
        Momentum,
    ),
    "energy": Topic(
        "Conservation of Energy", "Energy", "Track what changes and what stays.", Energy
    ),
    "rotational_motion": Topic(
        "Rotational Motion",
        "RotationalMotion",
        "Torque creates angular acceleration.",
        RotationalMotion,
    ),
    "orbital_mechanics": Topic(
        "Orbital Mechanics", "OrbitalMechanics", "Falling around a planet.", OrbitalMechanics
    ),
    "shm": Topic("Simple Harmonic Motion", "SHM", "A restoring force creates a rhythm.", SHM),
    "fluid_mechanics": Topic(
        "Fluid Mechanics", "FluidMechanics", "Pressure, flow, and continuity.", FluidMechanics
    ),
}
