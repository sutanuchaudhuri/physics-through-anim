"""Render Mask: a cosmetic skin that follows a point-mass CM pose."""

from __future__ import annotations

import math

import numpy as np
from manim import Square

from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.render import Mask


def test_mask_wraps_a_mobject() -> None:
    mask = Mask(source=Square(side_length=1.0))
    assert mask.mobject is not None


def test_place_seats_cm_at_pose_position() -> None:
    mask = Mask(source=Square(side_length=1.0))
    mask.place(Pose2D(position=(2.0, -1.0)))
    np.testing.assert_allclose(mask.mobject.get_center()[:2], [2.0, -1.0], atol=1e-9)


def test_place_is_drift_free_across_repeated_calls() -> None:
    mask = Mask(source=Square(side_length=1.0))
    for _ in range(5):
        mask.place(Pose2D(position=(1.5, 0.5), angle=0.3))
    np.testing.assert_allclose(mask.mobject.get_center()[:2], [1.5, 0.5], atol=1e-9)


def test_cosmetic_rotation_off_keeps_mask_upright() -> None:
    mask = Mask(source=Square(side_length=1.0), cosmetic_rotation=False)
    mask.place(Pose2D(position=(0.0, 0.0), angle=math.pi / 2))
    assert mask._angle == 0.0  # picture never spins; only the vectors/lever arms do


def test_cm_local_offset_anchors_the_offset_point() -> None:
    # CM sits at the right edge of the square; placing at origin puts that edge at origin.
    mask = Mask(source=Square(side_length=2.0), cm_local=(1.0, 0.0))
    mask.place(Pose2D(position=(0.0, 0.0)))
    np.testing.assert_allclose(mask.mobject.get_center()[:2], [-1.0, 0.0], atol=1e-9)


def test_transparent_mask_is_a_point_mass_with_hidden_skin() -> None:
    mask = Mask.transparent(source=Square(side_length=1.0))
    assert mask.opacity == 0.0
    mask.place(Pose2D(position=(3.0, 0.0)))
    np.testing.assert_allclose(mask.mobject.get_center()[:2], [3.0, 0.0], atol=1e-9)


def test_from_matrix_builds_an_image_mask() -> None:
    mask = Mask.from_matrix(np.zeros((4, 4)))
    assert hasattr(mask.mobject, "get_center")
