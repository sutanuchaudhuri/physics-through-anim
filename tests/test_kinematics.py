"""M1.6 kinematics: transforms, frames, point kinematics, ICR, rolling, bindings."""

from __future__ import annotations

import math

import numpy as np

from physics_through_anim.physics.core.frames import Frame2D
from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.core.state import RigidKinematicState
from physics_through_anim.physics.core.transforms import Transform2D
from physics_through_anim.physics.kinematics import (
    InstantaneousCenterState,
    PathPoseBinding,
    PointAttachmentBinding,
    RelativePoseBinding,
    RigidPoseBinding,
    RollingKinematicRelation,
    RollingPoseBinding,
    point_acceleration,
    point_velocity,
    velocity_at,
)
from physics_through_anim.physics.mechanics.massprops import MassProperties
from physics_through_anim.physics.mechanics.rigidbody import RigidBody2D


def _body(**keypoints) -> RigidBody2D:
    kp = {"CM": (0.0, 0.0), "P": (1.0, 0.0)}
    kp.update(keypoints)
    return RigidBody2D(mass_props=MassProperties(mass=1.0, inertia_cm=0.5), local_keypoints=kp)


# --- transforms -----------------------------------------------------------


def test_transform_point_translates_and_rotates() -> None:
    t = Transform2D.from_pose(Pose2D(position=(2.0, 0.0), angle=math.pi / 2))
    np.testing.assert_allclose(t.transform_point((1.0, 0.0)), [2.0, 1.0, 0.0], atol=1e-9)


def test_transform_vector_rotates_only() -> None:
    t = Transform2D.from_pose(Pose2D(position=(5.0, 7.0), angle=math.pi / 2))
    np.testing.assert_allclose(t.transform_vector((1.0, 0.0)), [0.0, 1.0, 0.0], atol=1e-9)


def test_translation_compose_rotation_equals_from_pose() -> None:
    # from_pose = rotate about origin, then translate: T @ R.
    composed = Transform2D.translation(3.0, -1.0).compose(Transform2D.rotation(0.6))
    direct = Transform2D.from_pose(Pose2D(position=(3.0, -1.0), angle=0.6))
    np.testing.assert_allclose(composed.m, direct.m, atol=1e-9)


def test_inverse_round_trips() -> None:
    t = Transform2D.from_pose(Pose2D(position=(1.0, 2.0), angle=0.9))
    back = t.inverse().compose(t)
    np.testing.assert_allclose(back.m, np.eye(3), atol=1e-9)


# --- point kinematics -----------------------------------------------------


def test_point_velocity_is_perpendicular_for_pure_rotation() -> None:
    body = _body()
    body.set_pose(Pose2D())
    state = RigidKinematicState(pose=Pose2D(), velocity=(0.0, 0.0), omega=2.0)
    v = point_velocity(body, "P", state)
    r = np.array([1.0, 0.0, 0.0])
    assert abs(float(np.dot(v, r))) < 1e-9  # v ⟂ (P - CM)
    np.testing.assert_allclose(v, [0.0, 2.0, 0.0], atol=1e-9)


def test_point_acceleration_matches_formula() -> None:
    body = _body()
    state = RigidKinematicState(pose=Pose2D(), omega=2.0, alpha=3.0)
    a = point_acceleration(body, "P", state)
    # a = alpha x r + omega x (omega x r) = (0,3) + (-4,0)
    np.testing.assert_allclose(a, [-4.0, 3.0, 0.0], atol=1e-9)


def test_instantaneous_center_velocity() -> None:
    icr = InstantaneousCenterState(point=(0.0, 0.0), omega=2.0)
    v = velocity_at(icr, (3.0, 0.0))
    assert abs(np.linalg.norm(v) - 6.0) < 1e-9  # |v| = omega * IP
    assert abs(float(np.dot(v, [3.0, 0.0, 0.0]))) < 1e-9  # v ⟂ IP


def test_rolling_relation_delta_theta() -> None:
    rel = RollingKinematicRelation(radius=2.0, direction=1)
    assert abs(rel.pose_from_arc(2.0).angle + 1.0) < 1e-9


# --- frames ---------------------------------------------------------------


def test_frame_round_trips_point_and_vector() -> None:
    frame = Frame2D(pose=Pose2D(position=(3.0, -2.0), angle=0.7))
    p_local = (1.5, 0.5)
    world = frame.to_world_point(p_local)
    back = frame.to_local_point((world[0], world[1]))
    np.testing.assert_allclose(back, [*p_local, 0.0], atol=1e-9)
    v_local = (1.0, 0.0)
    v_world = frame.to_world_vector(v_local)
    # a vector ignores the frame origin translation
    back_v = frame.to_local_vector((v_world[0], v_world[1]))
    np.testing.assert_allclose(back_v, [*v_local, 0.0], atol=1e-9)


# --- bindings -------------------------------------------------------------


def test_point_attachment_moves_child_to_parent_keypoint() -> None:
    parent = _body(A=(0.5, 0.0))
    parent.set_pose(Pose2D(position=(4.0, 1.0)))
    child = _body(hook=(-0.5, 0.0))
    PointAttachmentBinding(child, parent, parent_point="A", child_point="hook").apply()
    np.testing.assert_allclose(child.keypoint("hook"), parent.keypoint("A"), atol=1e-9)


def test_relative_pose_binding_keeps_constant_offset_when_parent_moves() -> None:
    parent = _body()
    child = _body()
    binding = RelativePoseBinding(child, parent, relative_pose=Pose2D(position=(2.0, 0.0)))
    parent.set_pose(Pose2D(position=(1.0, 1.0)))
    binding.apply()
    np.testing.assert_allclose(child.pose.position, (3.0, 1.0), atol=1e-9)
    parent.set_pose(Pose2D(position=(5.0, 1.0), angle=math.pi / 2))
    binding.apply()  # re-resolve: child follows parent (scene-graph propagation)
    np.testing.assert_allclose(child.pose.position, (5.0, 3.0), atol=1e-9)


def test_path_pose_binding_places_body_with_tangent_angle() -> None:
    class _Circle:
        def point_at(self, s: float):
            return (math.cos(s), math.sin(s))

        def tangent_angle(self, s: float) -> float:
            return s + math.pi / 2

    body = _body()
    PathPoseBinding(body, _Circle(), s=math.pi / 2).apply()
    np.testing.assert_allclose(body.pose.position, (0.0, 1.0), atol=1e-9)
    assert abs(body.pose.angle - math.pi) < 1e-9


def test_eight_acceptance_examples_apply_without_error() -> None:
    parent = _body()
    child = _body()
    surface = RollingKinematicRelation(radius=1.0)

    class _State:
        entities = {"b": RigidKinematicState(pose=Pose2D(position=(2.0, 0.0)))}

    class _Path:
        def point_at(self, s):
            return (s, 0.0)

        def tangent_angle(self, s):
            return 0.0

    bindings = [
        (RigidPoseBinding(child, entity="b"), _State()),
        (RelativePoseBinding(child, parent, Pose2D(position=(1.0, 0.0))), None),
        (PointAttachmentBinding(child, parent, "CM", "CM"), None),
        (PathPoseBinding(child, _Path(), s=1.0), None),
        (RollingPoseBinding(child, surface, s=0.5), None),
    ]
    for binding, state in bindings:
        binding.apply(state) if state is not None else binding.apply()
    assert child.pose is not None
