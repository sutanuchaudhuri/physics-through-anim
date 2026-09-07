"""Tests for the point-of-interest annotation overlay."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.mechanics.bodies import Block
from physics_through_anim.physics.overlays.annotations import (
    callout,
    follow_keypoint,
    point_marker,
)


def test_point_marker_dot_at_point_with_label() -> None:
    marker = point_marker((1.0, 2.0), "P")
    assert np.allclose(marker.submobjects[0].get_center()[:2], (1.0, 2.0))
    assert len(marker.submobjects) == 2  # dot + label


def test_point_marker_without_label_is_dot_only() -> None:
    marker = point_marker((0.0, 0.0))
    assert len(marker.submobjects) == 1


def test_follow_keypoint_tracks_moving_body() -> None:
    body = Block(name="m")
    marker = point_marker(body.keypoint("CM"), "P")
    follow_keypoint(marker, body, "CM")
    body.shift((3.0, 1.0))
    marker.update()  # run the updater
    assert np.allclose(marker.submobjects[0].get_center()[:2], body.keypoint("CM")[:2])


def test_callout_has_text_and_leader() -> None:
    group = callout((0.0, 0.0), "Look at point P", leader=True)
    assert len(group.submobjects) == 2  # text + leader line
    plain = callout((0.0, 0.0), "no leader", leader=False)
    assert len(plain.submobjects) == 1
