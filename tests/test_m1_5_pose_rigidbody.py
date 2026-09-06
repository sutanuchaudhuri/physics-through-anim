"""TDD spec for Milestone M1.5 -- Pose2D, refs, loads, MassProperties, RigidBody2D.

Plan:      plans/asset_library/M01_5_pose_rigidbody.md
Test plan: plans/asset_library/M01_5_TESTPLAN.md

Two kinds of test live here:

* **Structural** (no marker) -- assert the scaffold's *shape*: enums, dataclass
  fields, defaults. These pass now and guard the public surface.
* **Behavioural** (``@pytest.mark.xfail``) -- assert the *acceptance criteria*
  from the plan. They are RED until M1.5 is implemented; each one flips to XPASS
  as you fill in the corresponding method, at which point you delete its marker.

Run the red->green loop with::

    uv run pytest tests/test_m1_5_pose_rigidbody.py --runxfail -q   # see real failures
    # implement the method, then re-run until green; drop the xfail marker.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

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

TDD = pytest.mark.xfail(reason="M1.5 not implemented yet (TDD spec)", strict=False)


# --------------------------------------------------------------------------- #
# Structural: the scaffold's public shape (green now)
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
    assert isinstance(f, LoadSpec)  # ForceSpec is a LoadSpec
    assert f.value is None  # physical value, distinct from arrow length
    assert f.direction == "auto"


def test_distributed_load_spec_fields() -> None:
    d = DistributedLoadSpec(at="wall", label="p", over="wall.face")
    assert d.direction == "normal"
    assert d.intensity is None


# --------------------------------------------------------------------------- #
# Behavioural acceptance criteria (RED until implemented)
# --------------------------------------------------------------------------- #
@TDD
def test_pose_world_point_rotates_then_translates() -> None:
    # rotate local (1,0) by 90 deg about origin -> (0,1), then translate (2,0).
    p = Pose2D(position=(2.0, 0.0), angle=math.pi / 2)
    np.testing.assert_allclose(p.world_point((1.0, 0.0)), [2.0, 1.0, 0.0], atol=1e-9)


@TDD
def test_pose_world_vector_ignores_translation() -> None:
    p = Pose2D(position=(2.0, 0.0), angle=math.pi / 2)
    np.testing.assert_allclose(p.world_vector((1.0, 0.0)), [0.0, 1.0, 0.0], atol=1e-9)


@TDD
def test_pose_compose_parent_child() -> None:
    parent = Pose2D(position=(1.0, 0.0), angle=math.pi / 2)
    child = Pose2D(position=(1.0, 0.0), angle=0.0)
    c = parent.compose(child)
    np.testing.assert_allclose(c.position, [1.0, 1.0], atol=1e-9)
    assert abs(c.angle - math.pi / 2) < 1e-9


@TDD
def test_set_pose_is_absolute_no_drift() -> None:
    b = RigidBody2D(local_keypoints={"P": (1.0, 0.0)})
    b.set_pose(Pose2D(angle=math.pi / 2))
    b.set_pose(Pose2D(angle=math.pi / 2))  # applying the same absolute pose twice
    assert abs(b.pose.angle - math.pi / 2) < 1e-9  # stays at theta, not 2*theta


@TDD
def test_keypoint_returns_world_coords() -> None:
    b = RigidBody2D(local_keypoints={"P": (1.0, 0.0)})
    b.set_pose(Pose2D(position=(2.0, 0.0), angle=0.0))
    np.testing.assert_allclose(b.keypoint("P"), [3.0, 0.0, 0.0], atol=1e-9)


@TDD
def test_refs_parse_roundtrips() -> None:
    r = parse("disk.P")
    assert isinstance(r, PointRef)
    assert (r.asset, r.key) == ("disk", "P")
    assert str(r) == "disk.P"


@TDD
def test_massprops_parallel_axis() -> None:
    mp = MassProperties(mass=2.0, inertia_cm=3.0)
    assert abs(mp.inertia_about((1.0, 0.0)) - (3.0 + 2.0 * 1.0)) < 1e-9


@TDD
def test_point_velocity_perpendicular_for_pure_rotation() -> None:
    b = RigidBody2D(local_keypoints={"CM": (0.0, 0.0), "P": (1.0, 0.0)})
    state = BodyState2D(velocity=(0.0, 0.0), omega=2.0)
    v = b.point_velocity("P", state)
    r = b.point_position("P", state) - b.point_position("CM", state)
    assert abs(float(np.dot(v[:2], r[:2]))) < 1e-9  # v _|_ (P - CM)
    assert abs(float(np.linalg.norm(v[:2])) - 2.0) < 1e-9  # |v| = omega * R


@TDD
def test_point_velocity_combined_motion() -> None:
    b = RigidBody2D(local_keypoints={"CM": (0.0, 0.0), "P": (1.0, 0.0)})
    state = BodyState2D(velocity=(3.0, 0.0), omega=2.0)  # v_G + omega x r
    np.testing.assert_allclose(b.point_velocity("P", state)[:2], [3.0, 2.0], atol=1e-9)


@TDD
def test_arrow_length_fixed_ignores_value() -> None:
    assert arrow_length(2.0, VectorScalePolicy.FIXED) == arrow_length(
        9.0, VectorScalePolicy.FIXED
    )
