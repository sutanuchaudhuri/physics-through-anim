"""TDD spec for M3 -- rolling/rotation bodies."""

from __future__ import annotations

import numpy as np
import pytest

from physics_through_anim.physics.mechanics.circular import (
    CircularBody,
    Cylinder,
    Disk,
    Hoop,
    Pulley,
    Ring,
    Sphere2D,
)

TDD = pytest.mark.xfail(reason="M3 not implemented (TDD spec)", strict=False)


def test_inertia_factors() -> None:
    assert Disk().inertia_factor == 0.5
    assert Ring().inertia_factor == 1.0
    assert Sphere2D().inertia_factor == 0.4
    assert Hoop is Ring
    assert Cylinder().show_cross_section is True


def test_pulley_rope_angles() -> None:
    assert Pulley().rope_angles == {"A": 30.0, "B": 60.0}


@TDD
def test_rim_at_cardinal_points() -> None:
    d = CircularBody(radius=1.0)
    np.testing.assert_allclose(d.rim_at(0.0)[:2], [1.0, 0.0], atol=1e-9)
    np.testing.assert_allclose(d.rim_at(np.pi / 2)[:2], [0.0, 1.0], atol=1e-9)
