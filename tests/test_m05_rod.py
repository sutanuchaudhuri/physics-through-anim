"""TDD spec for M5 -- Rod body."""

from __future__ import annotations

import numpy as np
import pytest

from physics_through_anim.physics.mechanics.rod import Rod

TDD = pytest.mark.xfail(reason="M5 not implemented (TDD spec)", strict=False)


def test_rod_defaults() -> None:
    r = Rod(length=2.0)
    assert r.massless is False
    assert r.length == 2.0


@TDD
def test_rod_point_at_endpoints() -> None:
    r = Rod(length=2.0, center=(0.0, 0.0), angle_deg=0.0)
    a = r.point_at(0.0)
    b = r.point_at(1.0)
    assert abs(float(np.linalg.norm(b - a)) - 2.0) < 1e-9
