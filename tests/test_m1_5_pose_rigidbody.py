"""Tests for Milestone M1.5 -- Pose2D, refs, loads, MassProperties, RigidBody2D.

M1.5 is IMPLEMENTED (no longer a scaffold): these are normal passing tests. See
plans/asset_library/M01_5_pose_rigidbody.md and M01_5_TESTPLAN.md.
"""

from __future__ import annotations

import math

import numpy as np

from physics_through_anim.physics.core.loads import (
    DistributedLoadSpec,
    ForceSpec,
    InteractionKind,
    LoadSpec,
    VectorScalePolicy,
    arrow_length,
)
from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.core.refs import PointRef, parse
from physics_through_anim.physics.mechanics.massprops import MassProperties
from physics_through_anim.physics.mechanics.rigidbody import BodyState2D, RigidBody2D


# --------------------------------------------------------------------------- #
# Structural: the public shape
# --------------------------------------------------------------------------- #
def test_vector_scale_policy_members() -> None:
    assert {p.value for p in VectorScalePolicy} == {
        "fixed",
        "proportional",
        "normalized",
        "clipped",
    }


def test_interaction_kind_unifies_gravity() -> None:
    assert InteractionKind.GRAVITY.value == "gravity"
    assert set(InteractionKind.__members__) >= {
        "GRAVITY",
        "NORMAL",
        "FRICTION",
        "APPLIED",
        "TENSION",
        "REACTION",
        "SPRING",
        "DAMPING",
    }


def test_dataclass_defaults() -> None:
    assert Pose2D().position == (0.0, 0.0)
    assert Pose2D().angle == 0.0
    assert MassProperties().mass == 1.0
    assert MassProperties().inertia_cm == 0.0


def test_forcespec_value_is_separate_from_length() -> None:
    f = ForceSpec(at="CM", label="mg", kind=InteractionKind.GRAVITY)
    assert isinstance(f, LoadSpec)
    assert f.value is None
    assert f.direction == "auto"


def test_distributed_load_spec_fields() -> None:
    d = DistributedLoadSpec(at="wall", label="p", over="wall.face")
    assert d.direction == "normal"
    assert d.intensity is None


# --------------------------------------------------------------------------- #
# Behavioural acceptance criteria
# --------------------------------------------------------------------------- #
def test_pose_world_point_rotates_then_translates() -> None:
    p = Pose2D(position=(2.0, 0.0), angle=math.pi / 2)
    np.testing.assert_allclose(p.world_point((1.0, 0.0)), [2.0, 1.0, 0.0], atol=1e-9)


def test_pose_world_vector_ignores_translation() -> None:
    p = Pose2D(position=(2.0, 0.0), angle=math.pi / 2)
    np.testing.assert_allclose(p.world_vector((1.0, 0.0)), [0.0, 1.0, 0.0], atol=1e-9)


def test_pose_compose_parent_child() -> None:
    parent = Pose2D(position=(1.0, 0.0), angle=math.pi / 2)
    child = Pose2D(position=(1.0, 0.0), angle=0.0)
    c = parent.compose(child)
    np.testing.assert_allclose(c.position, [1.0, 1.0], atol=1e-9)
    assert abs(c.angle - math.pi / 2) < 1e-9


def test_set_pose_is_absolute_no_drift() -> None:
    b = RigidBody2D(local_keypoints={"P": (1.0, 0.0)})
    b.set_pose(Pose2D(angle=math.pi / 2))
    b.set_pose(Pose2D(angle=math.pi / 2))
    assert abs(b.pose.angle - math.pi / 2) < 1e-9


def test_keypoint_returns_world_coords() -> None:
    b = RigidBody2D(local_keypoints={"P": (1.0, 0.0)})
    b.set_pose(Pose2D(position=(2.0, 0.0), angle=0.0))
    np.testing.assert_allclose(b.keypoint("P"), [3.0, 0.0, 0.0], atol=1e-9)


def test_refs_parse_roundtrips() -> None:
    r = parse("disk.P")
    assert isinstance(r, PointRef)
    assert (r.asset, r.key) == ("disk", "P")
    assert str(r) == "disk.P"


def test_massprops_parallel_axis() -> None:
    mp = MassProperties(mass=2.0, inertia_cm=3.0)
    assert abs(mp.inertia_about((1.0, 0.0)) - (3.0 + 2.0 * 1.0)) < 1e-9


def test_point_velocity_perpendicular_for_pure_rotation() -> None:
    b = RigidBody2D(local_keypoints={"CM": (0.0, 0.0), "P": (1.0, 0.0)})
    state = BodyState2D(velocity=(0.0, 0.0), omega=2.0)
    v = b.point_velocity("P", state)
    r = b.point_position("P", state) - b.point_position("CM", state)
    assert abs(float(np.dot(v[:2], r[:2]))) < 1e-9
    assert abs(float(np.linalg.norm(v[:2])) - 2.0) < 1e-9


def test_point_velocity_combined_motion() -> None:
    b = RigidBody2D(local_keypoints={"CM": (0.0, 0.0), "P": (1.0, 0.0)})
    state = BodyState2D(velocity=(3.0, 0.0), omega=2.0)
    np.testing.assert_allclose(b.point_velocity("P", state)[:2], [3.0, 2.0], atol=1e-9)


def test_point_acceleration_centripetal_plus_tangential() -> None:
    b = RigidBody2D(local_keypoints={"CM": (0.0, 0.0), "P": (1.0, 0.0)})
    state = BodyState2D(omega=2.0, alpha=3.0)  # a_G = 0
    # alpha x r = 3*(0,1) = (0,3); omega x (omega x r) = -4*(1,0) = (-4,0)
    np.testing.assert_allclose(b.point_acceleration("P", state)[:2], [-4.0, 3.0], atol=1e-9)


def test_inertia_about_offset_keypoint() -> None:
    b = RigidBody2D(
        mass_props=MassProperties(mass=2.0, inertia_cm=3.0),
        local_keypoints={"CM": (0.0, 0.0), "P": (1.0, 0.0)},
    )
    assert abs(b.inertia_about("P") - 5.0) < 1e-9


def test_arrow_length_fixed_ignores_value() -> None:
    assert arrow_length(2.0, VectorScalePolicy.FIXED) == arrow_length(9.0, VectorScalePolicy.FIXED)


def test_arrow_length_proportional_scales_with_value() -> None:
    assert arrow_length(3.0, VectorScalePolicy.PROPORTIONAL, base=1.0) == 3.0
