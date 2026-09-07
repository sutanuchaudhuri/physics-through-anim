"""M3 spec -- rolling/rotation bodies, rock skin, rolling velocity field."""

from __future__ import annotations

import numpy as np
from manim import Square

from physics_through_anim.physics.mechanics.assembly import Assembly
from physics_through_anim.physics.mechanics.circular import (
    CircularBody,
    Cylinder,
    Disk,
    Hoop,
    Pulley,
    Ring,
    Sphere2D,
)
from physics_through_anim.physics.mechanics.kinds import ForceKind
from physics_through_anim.physics.mechanics.supports import Floor


def test_inertia_factors() -> None:
    assert Disk().inertia_factor == 0.5
    assert Ring().inertia_factor == 1.0
    assert Sphere2D().inertia_factor == 0.4
    assert Hoop is Ring
    assert Cylinder().show_cross_section is True


def test_pulley_rope_angles_and_rim_points() -> None:
    p = Pulley(center=(0.0, 2.0), radius=0.5)
    assert p.rope_angles == {"A": 30.0, "B": 60.0}
    np.testing.assert_allclose(p.keypoint("axle"), [0.0, 2.0, 0.0])
    a = p.rim_point("A")
    assert abs(np.linalg.norm(a - np.array([0.0, 2.0, 0.0])) - 0.5) < 1e-9


def test_rim_at_cardinal_points() -> None:
    d = CircularBody(radius=1.0, position=(0.0, 0.0))
    np.testing.assert_allclose(d.rim_at(0.0)[:2], [1.0, 0.0], atol=1e-9)
    np.testing.assert_allclose(d.rim_at(np.pi / 2)[:2], [0.0, 1.0], atol=1e-9)


def test_rolling_velocity_is_perpendicular_to_contact_line() -> None:
    d = Disk(radius=1.0, position=(0.0, 1.0))  # bottom (contact) at y = 0
    top = d.rim_at(np.pi / 2)  # the top rim point
    v = d.point_velocity(top, v_cm=2.0)
    r = top - d.contact_point()
    assert abs(float(np.dot(v, r))) < 1e-9  # Rule 5: v perp to (point - P)
    assert np.linalg.norm(v) > 0


def test_contact_registered_after_place_on_floor() -> None:
    a = Assembly()
    floor = Floor(y=-2.0)
    disk = Disk(radius=0.6, position=(0.0, 3.0))
    a.add(floor)
    a.add(disk, place_on=floor)
    np.testing.assert_allclose(disk.keypoint("bottom")[1], -2.0, atol=1e-9)
    assert "contact" in disk.keypoints


def test_weight_auto_declared_at_cm() -> None:
    d = Disk()
    weights = [f for f in d.forces if f.kind is ForceKind.WEIGHT]
    assert len(weights) == 1
    assert weights[0].at == "CM"


def test_skin_rides_the_body() -> None:
    disk = Disk(radius=0.6, skin=Square(side_length=1.0), show_spoke=False)
    assert disk.skin in disk.mobject.submobjects  # the rock/skin is part of the picture

