"""Tests for pulley mounting flavours (framework addition to M4/M10)."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.mechanics import (
    Incline,
    PulleyMount,
    mount_pulley,
)


def test_flavour2_axle_coincides_with_point() -> None:
    m = mount_pulley((1.0, 2.0), radius=0.4, flavour=PulleyMount.AT_POINT)
    assert np.allclose(m.pulley.center, (1.0, 2.0))
    assert m.bracket is None
    assert m.axle.participants == ("pulley",)


def test_flavour1_axle_offset_on_immovable_bracket() -> None:
    m = mount_pulley((0.0, 0.0), radius=0.4, flavour=PulleyMount.ON_SUPPORT,
                     normal=(0.0, 1.0), standoff=0.6)
    assert np.allclose(m.pulley.center, (0.0, 0.6))  # axle held off the point
    assert m.bracket is not None
    assert np.allclose(m.bracket.keypoint("base")[:2], (0.0, 0.0))
    assert np.allclose(m.bracket.keypoint("axle")[:2], (0.0, 0.6))
    assert m.axle.active is True


def test_incline_mount_flavour2_at_apex() -> None:
    incline = Incline(angle_deg=30.0, length=4.0, base=(-1.0, -2.0))
    apex = incline.surface_at(1.0)
    m = incline.mount_pulley(radius=0.3, flavour="at_point")
    assert np.allclose(m.pulley.center, apex[:2])
    assert m.bracket is None


def test_incline_mount_flavour1_offset_along_normal() -> None:
    incline = Incline(angle_deg=30.0, length=4.0, base=(-1.0, -2.0))
    apex = incline.surface_at(1.0)
    theta = np.radians(30.0)
    normal = np.array([-np.sin(theta), np.cos(theta)])
    m = incline.mount_pulley(radius=0.3, flavour="on_support", standoff=0.5)
    assert np.allclose(m.pulley.center, apex[:2] + 0.5 * normal)
    assert m.bracket is not None
