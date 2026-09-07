"""M2 spec -- unified Wall family, contact semantics, conveyor, surfaces."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.mechanics.contact import (
    Contact,
    ContactFrame,
    ContactGeometry,
    ContactKinematics,
    ContactLifecycle,
    FixedWorldPoint,
    FrictionModel,
    MaterialPairing,
    SurfaceCoordinate,
)
from physics_through_anim.physics.mechanics.environment import Ceiling, Conveyor, Corner, Incline
from physics_through_anim.physics.mechanics.supports import Floor, Wall
from physics_through_anim.physics.mechanics.surfaces import InclineSurface


def test_contact_enums_split() -> None:
    assert {k.value for k in ContactKinematics} >= {"sticking", "sliding", "rolling_no_slip"}
    assert {f.value for f in FrictionModel} == {"frictionless", "coulomb", "custom"}
    assert {c.value for c in ContactLifecycle} == {"establishing", "active", "separating"}


def test_contact_defaults() -> None:
    c = Contact(body="block", surface="floor")
    assert c.geometry is ContactGeometry.POINT
    assert c.pairing is MaterialPairing.SAME
    assert c.lifecycle is ContactLifecycle.ACTIVE


# --- wall family is one primitive ----------------------------------------


def test_floor_and_ceiling_and_incline_are_walls() -> None:
    assert isinstance(Floor(), Wall)
    assert isinstance(Ceiling(), Wall)
    assert isinstance(Incline(), Wall)
    assert isinstance(Conveyor(), Wall)


def test_wall_normals_point_the_expected_way() -> None:
    np.testing.assert_allclose(Floor().normal(), [0.0, 1.0, 0.0], atol=1e-9)
    np.testing.assert_allclose(Ceiling().normal(), [0.0, -1.0, 0.0], atol=1e-9)
    right = Wall(angle_deg=90.0, facing="right").normal()
    np.testing.assert_allclose(right, [1.0, 0.0, 0.0], atol=1e-9)


def test_no_wall_has_an_fbd() -> None:
    for wall in (Floor(), Ceiling(), Incline(), Conveyor(), Wall()):
        assert wall.forces == []
        assert len(wall.fbd()) == 0


def test_incline_normal_is_unit_and_perp_to_slope() -> None:
    inc = Incline(angle_deg=30.0)
    n = inc.normal()
    assert abs(float(np.linalg.norm(n)) - 1.0) < 1e-9
    assert abs(float(np.dot(n, inc.tangent()))) < 1e-9


def test_incline_surface_endpoints() -> None:
    s = InclineSurface(a=(0.0, 0.0), b=(3.0, 0.0))
    np.testing.assert_allclose(s.point_at(0.0)[:2], [0.0, 0.0], atol=1e-9)
    np.testing.assert_allclose(s.point_at(1.0)[:2], [3.0, 0.0], atol=1e-9)


def test_incline_surface_at_endpoints_match_foot_and_apex() -> None:
    inc = Incline(angle_deg=30.0, length=4.0, base=(-1.0, -2.0))
    np.testing.assert_allclose(inc.surface_at(0.0), inc.keypoint("foot"))
    np.testing.assert_allclose(inc.surface_at(1.0), inc.keypoint("apex"))


def test_corner_renders_two_walls() -> None:
    corner = Corner(a=Floor(), b=Wall(angle_deg=90.0, center=(-5.0, 0.0)))
    assert len(corner.walls) == 2
    assert len(corner.mobject) == 2


def test_conveyor_motion_state() -> None:
    assert Conveyor(belt_speed=0.0).motion_state == "at_rest"
    assert Conveyor(belt_speed=2.0).motion_state == "moving"


# --- contact frame resolution --------------------------------------------


def test_fixed_world_point_locator() -> None:
    c = Contact(body="b", surface="floor", locator=FixedWorldPoint(point=(1.0, 2.0)))
    frame = c.frame_at()
    assert isinstance(frame, ContactFrame)
    np.testing.assert_allclose(frame.point, [1.0, 2.0, 0.0], atol=1e-9)


def test_surface_coordinate_locator_uses_surface_geometry() -> None:
    inc = Incline(angle_deg=30.0)
    loc = SurfaceCoordinate(surface=inc.surface(), s=0.5)
    frame = loc.locate()
    np.testing.assert_allclose(frame.point, inc.surface_at(0.5), atol=1e-9)
    assert abs(float(np.dot(frame.tangent, frame.normal))) < 1e-9

