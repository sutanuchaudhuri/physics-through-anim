"""M2 non-penetration geometry: clearance, corner seat, projection, assembly guard."""

from __future__ import annotations

import numpy as np
import pytest

from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.mechanics.assembly import Assembly
from physics_through_anim.physics.mechanics.bodies import Block
from physics_through_anim.physics.mechanics.environment import Incline
from physics_through_anim.physics.mechanics.geometry import (
    Circle2D,
    Polygon2D,
    clearance,
    corner_seat,
    no_penetration_clamp,
    project_circle_out,
    signed_distance,
)
from physics_through_anim.physics.mechanics.supports import Floor, Wall


def test_signed_distance_positive_on_outward_side() -> None:
    floor = Floor(y=-2.0)
    assert signed_distance((0.0, 1.0), floor) > 0  # above the floor is free
    assert signed_distance((0.0, -3.0), floor) < 0  # below is inside the solid


def test_circle_clearance_and_touch() -> None:
    floor = Floor(y=0.0)
    assert clearance(Circle2D(center=(0.0, 1.0), radius=0.5), floor) == pytest.approx(0.5)
    assert clearance(Circle2D(center=(0.0, 0.5), radius=0.5), floor) == pytest.approx(0.0)


def test_polygon_clearance_is_min_over_vertices() -> None:
    floor = Floor(y=0.0)
    poly = Polygon2D(vertices=((-1.0, 0.2), (1.0, 0.2), (1.0, 1.0), (-1.0, 1.0)))
    assert clearance(poly, floor) == pytest.approx(0.2)


def test_corner_seat_is_tangent_to_both_walls() -> None:
    floor = Floor(y=-2.0)
    ramp = Incline(angle_deg=30.0, length=5.0, base=(1.0, -2.0))
    r = 0.5
    c = corner_seat(r, floor, ramp)
    assert clearance(Circle2D(center=(c[0], c[1]), radius=r), floor) == pytest.approx(0.0, abs=1e-9)
    assert clearance(Circle2D(center=(c[0], c[1]), radius=r), ramp) == pytest.approx(0.0, abs=1e-9)


def test_project_circle_out_restores_tangency() -> None:
    floor = Floor(y=0.0)
    c = project_circle_out((0.0, 0.2), 0.5, floor)  # penetrating (needs y = 0.5)
    np.testing.assert_allclose(c, [0.0, 0.5, 0.0], atol=1e-9)


def test_no_penetration_clamp_holds_pose_out_of_wall() -> None:
    floor = Floor(y=0.0)
    clamp = no_penetration_clamp(0.5, [floor])
    out = clamp(Pose2D(position=(0.0, -0.3)))
    assert out.position[1] == pytest.approx(0.5)


def test_assembly_rejects_a_body_that_pierces_a_wall() -> None:
    a = Assembly()
    a.add(Floor(y=0.0))
    sunk = Block(position=(0.0, -1.0), width=1.0)  # centre below the floor => pierces
    with pytest.raises(ValueError, match="impenetrable"):
        a.add(sunk)


def test_assembly_accepts_a_resting_block() -> None:
    a = Assembly()
    floor = Floor(y=-2.0)
    a.add(floor)
    block = Block(position=(0.0, 3.0), width=1.0)
    a.add(block, place_on=floor)  # seated to tangency, no penetration
    assert "block.contact" in a.keypoints


def test_seat_a_cylinder_on_an_incline_is_tangent_no_pierce() -> None:
    from physics_through_anim.physics.mechanics.circular import Cylinder
    from physics_through_anim.physics.mechanics.geometry import Circle2D

    a = Assembly()
    ramp = Incline(angle_deg=30.0, length=5.0, base=(-1.0, -2.0))
    cyl = Cylinder(radius=0.5, position=(1.0, 2.0))
    a.add(ramp)
    a.add(cyl, place_on=ramp)  # seats via the tangency constraint, not by hand
    shape = Circle2D(center=(cyl.keypoint("CM")[0], cyl.keypoint("CM")[1]), radius=0.5)
    assert clearance(shape, ramp) == pytest.approx(0.0, abs=1e-9)  # always in contact
    assert "contact" in cyl.keypoints


def test_seat_circle_on_surface_pushes_out_by_radius_along_normal() -> None:
    from physics_through_anim.physics.mechanics.geometry import seat_circle_on_surface

    ramp = Incline(angle_deg=30.0, length=5.0, base=(0.0, 0.0))
    centre, contact = seat_circle_on_surface(0.5, ramp, near=(2.0, 2.0))
    np.testing.assert_allclose(centre - contact, 0.5 * np.asarray(ramp.normal()), atol=1e-9)


def test_seat_a_block_on_an_incline_rotates_and_sits_flush() -> None:
    from physics_through_anim.physics.mechanics.geometry import body_shape

    a = Assembly()
    ramp = Incline(angle_deg=30.0, length=6.0, base=(-2.0, -2.0))
    block = Block(position=(1.0, 2.0), width=1.2)
    a.add(ramp)
    a.add(block, place_on=ramp)  # rotates the base parallel to the slope, seats flush
    assert clearance(body_shape(block), ramp) == pytest.approx(0.0, abs=1e-9)  # no pierce, flush
    edge = block.keypoint("right") - block.keypoint("left")
    edge = edge / np.linalg.norm(edge)
    assert abs(abs(float(edge @ np.asarray(ramp.tangent()))) - 1.0) < 1e-9  # base ∥ slope
    assert "contact" in block.keypoints


def test_wall_normals() -> None:
    assert signed_distance((1.0, 0.0), Wall(angle_deg=90.0, facing="right", center=(0.0, 0.0))) > 0
