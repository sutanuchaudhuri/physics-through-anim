"""M6 asset integration -- apply_state + trajectory-driven Assembly + Particle."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.core.state import RigidKinematicState, SystemState
from physics_through_anim.physics.core.trajectory import AnalyticTrajectory
from physics_through_anim.physics.mechanics import Assembly, Block, Disk, Particle


def test_apply_state_moves_cm_to_pose_position() -> None:
    block = Block(position=(0.0, 0.0), width=1.0)
    block.apply_state(RigidKinematicState(pose=Pose2D(position=(3.0, -1.0))))
    np.testing.assert_allclose(block.keypoint("CM")[:2], [3.0, -1.0], atol=1e-9)


def test_apply_state_rotation_moves_keypoints_about_cm() -> None:
    block = Block(position=(0.0, 0.0), width=2.0, height=2.0)
    right0 = block.keypoint("right").copy()
    block.apply_state(RigidKinematicState(pose=Pose2D(position=(0.0, 0.0), angle=np.pi / 2)))
    # the +x 'right' keypoint rotates to +y
    expected = np.array([0.0, np.linalg.norm(right0[:2]), 0.0])
    np.testing.assert_allclose(block.keypoint("right"), expected, atol=1e-9)


def test_apply_state_is_drift_free_across_repeats() -> None:
    disk = Disk(radius=0.5, position=(0.0, 0.0))
    for _ in range(5):
        disk.apply_state(RigidKinematicState(pose=Pose2D(position=(1.0, 2.0), angle=0.4)))
    np.testing.assert_allclose(disk.keypoint("CM")[:2], [1.0, 2.0], atol=1e-9)


def test_particle_is_a_point_body() -> None:
    p = Particle(position=(1.0, 1.0))
    np.testing.assert_allclose(p.keypoint("CM")[:2], [1.0, 1.0])
    assert p.forces == []  # no weight by default


def test_assembly_semantic_queries() -> None:
    a = Assembly()
    a.add(Block(name="crate", position=(0.0, 0.0), width=0.8))
    a.add(Disk(name="wheel", radius=0.4, position=(2.0, 0.0)))
    assert a.body("crate").name == "crate"
    assert len(a.assets(Disk)) == 1
    assert any(f.label == "mg" for f in a.forces_on("crate"))


def test_apply_states_and_trajectory_math() -> None:
    a = Assembly()
    a.add(Particle(name="ball", position=(0.0, 0.0)))

    def parabola(t: float) -> SystemState:
        x, y = 1.0 * t, 3.0 * t - 0.5 * 9.8 * t * t
        return SystemState(entities={"ball": RigidKinematicState(pose=Pose2D(position=(x, y)))})

    # apply the state at t=2 directly (what animate_trajectory does each frame)
    a.apply_states(parabola(2.0).entities)
    expected = parabola(2.0).entities["ball"].pose.position
    np.testing.assert_allclose(a.body("ball").keypoint("CM")[:2], expected, atol=1e-9)
    assert isinstance(AnalyticTrajectory(parabola).state_at(1.0), SystemState)
