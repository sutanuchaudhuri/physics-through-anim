import numpy as np

from physics_through_anim.physics.mechanics import (
    Assembly,
    Block,
    BodyDynamics,
    Floor,
    ForceKind,
    MotionState,
    RectangularMass,
)
from physics_through_anim.physics.mechanics.palette import COLOR_WEIGHT, FORCE_COLORS


def test_block_defaults_and_keypoints() -> None:
    block = Block(position=(1.0, 0.5), width=1.0, shape="rectangle")
    assert block.dynamics is BodyDynamics.DYNAMIC
    assert block.motion_state is MotionState.AT_REST
    assert block.display_height == 0.6  # 0.6 * width for a rectangle
    np.testing.assert_allclose(block.keypoint("CM"), [1.0, 0.5, 0.0])
    np.testing.assert_allclose(block.keypoint("bottom"), [1.0, 0.5 - 0.3, 0.0])
    np.testing.assert_allclose(block.keypoint("top"), [1.0, 0.5 + 0.3, 0.0])


def test_rectangular_mass_is_block_alias() -> None:
    assert RectangularMass is Block


def test_square_shape_forces_equal_sides() -> None:
    block = Block(width=0.8, shape="square")
    assert block.display_height == 0.8


def test_block_auto_declares_weight_at_cm() -> None:
    block = Block(show_weight=True)
    weights = [f for f in block.forces if f.kind is ForceKind.WEIGHT]
    assert len(weights) == 1
    assert weights[0].at == "CM"
    assert weights[0].label == "mg"
    assert weights[0].direction == "down"


def test_shift_moves_mobject_and_keypoints_together() -> None:
    block = Block(position=(0.0, 0.0))
    block.shift([2.0, -1.0])
    np.testing.assert_allclose(block.keypoint("CM"), [2.0, -1.0, 0.0])
    np.testing.assert_allclose(block.mobject.get_center(), [2.0, -1.0, 0.0], atol=1e-6)


def test_place_block_on_floor_rests_bottom_on_surface() -> None:
    floor = Floor(y=-2.0)
    block = Block(position=(1.5, 3.0), width=1.0)  # starts high above the floor
    scene = Assembly()
    scene.add(floor)
    scene.add(block, place_on=floor)
    # bottom of the block now sits exactly on the floor line
    np.testing.assert_allclose(block.keypoint("bottom")[1], -2.0, atol=1e-9)
    np.testing.assert_allclose(block.keypoint("CM")[0], 1.5)  # x unchanged
    np.testing.assert_allclose(block.keypoint("contact"), [1.5, -2.0, 0.0])


def test_assembly_namespaces_keypoints() -> None:
    floor = Floor()
    block = Block(name="crate")
    scene = Assembly()
    scene.add(floor)
    scene.add(block, place_on=floor)
    assert "crate.CM" in scene.keypoints
    assert "floor.surface" in scene.keypoints


def test_weight_colour_matches_palette() -> None:
    assert FORCE_COLORS[ForceKind.WEIGHT] == COLOR_WEIGHT
