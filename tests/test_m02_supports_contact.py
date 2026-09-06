"""TDD spec for M2 -- supports, contact semantics, conveyor."""

from __future__ import annotations

import pytest

from physics_through_anim.physics.mechanics.contact import (
    Contact,
    ContactGeometry,
    ContactKinematics,
    ContactLifecycle,
    FrictionModel,
    MaterialPairing,
)
from physics_through_anim.physics.mechanics.environment import Conveyor, Incline
from physics_through_anim.physics.mechanics.surfaces import InclineSurface

TDD = pytest.mark.xfail(reason="M2 not implemented (TDD spec)", strict=False)


def test_contact_enums_split() -> None:
    assert {k.value for k in ContactKinematics} >= {"sticking", "sliding", "rolling_no_slip"}
    assert {f.value for f in FrictionModel} == {"frictionless", "coulomb", "custom"}
    assert {c.value for c in ContactLifecycle} == {"establishing", "active", "separating"}


def test_contact_defaults() -> None:
    c = Contact(body="block", surface="floor")
    assert c.geometry is ContactGeometry.POINT
    assert c.pairing is MaterialPairing.SAME
    assert c.lifecycle is ContactLifecycle.ACTIVE


@TDD
def test_conveyor_motion_state() -> None:
    assert Conveyor(belt_speed=0.0).motion_state == "at_rest"
    assert Conveyor(belt_speed=2.0).motion_state == "moving"


@TDD
def test_incline_surface_endpoints() -> None:
    s = InclineSurface(a=(0.0, 0.0), b=(3.0, 0.0))
    import numpy as np

    np.testing.assert_allclose(s.point_at(0.0)[:2], [0.0, 0.0], atol=1e-9)


@TDD
def test_incline_normal_is_unit() -> None:
    import numpy as np

    n = Incline(angle_deg=30.0).normal()
    assert abs(float(np.linalg.norm(n)) - 1.0) < 1e-9
