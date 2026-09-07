"""Generic, domain-neutral kinematics: rigid-body/point velocity & acceleration, instantaneous
centre, the declared rolling relation, and the pose/attachment/path bindings that drive every
asset. Reuse the transformation mathematics; never reuse a physics solution implicitly.
"""

from physics_through_anim.physics.kinematics.bindings import (
    PathPoseBinding,
    PointAttachmentBinding,
    Posable,
    RelativePoseBinding,
    RigidPoseBinding,
    RollingPoseBinding,
)
from physics_through_anim.physics.kinematics.instantaneous_center import (
    InstantaneousCenterState,
    velocity_at,
)
from physics_through_anim.physics.kinematics.point import relative_position, relative_velocity
from physics_through_anim.physics.kinematics.rigid_body import (
    point_acceleration,
    point_position,
    point_velocity,
)
from physics_through_anim.physics.kinematics.rolling import RollingKinematicRelation

__all__ = [
    "InstantaneousCenterState",
    "PathPoseBinding",
    "PointAttachmentBinding",
    "Posable",
    "RelativePoseBinding",
    "RigidPoseBinding",
    "RollingKinematicRelation",
    "RollingPoseBinding",
    "point_acceleration",
    "point_position",
    "point_velocity",
    "relative_position",
    "relative_velocity",
    "velocity_at",
]

