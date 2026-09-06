"""TDD spec for M13 -- orbital / central-force geometry."""

from __future__ import annotations

import numpy as np
import pytest

from physics_through_anim.physics.mechanics.orbital import CentralBody, OrbitPath, toward

TDD = pytest.mark.xfail(reason="M13 not implemented (TDD spec)", strict=False)


def test_orbit_defaults() -> None:
    o = OrbitPath(a=3.0, e=0.5, focus=(-1.5, 0.0))
    assert o.a == 3.0 and o.e == 0.5
    assert CentralBody(label="M").label == "M"


@TDD
def test_orbit_point_at_periapsis() -> None:
    o = OrbitPath(a=3.0, e=0.5, focus=(0.0, 0.0))
    np.testing.assert_allclose(o.point_at(0.0), o.periapsis(), atol=1e-9)


@TDD
def test_toward_direction() -> None:
    toward((1.0, 0.0))
