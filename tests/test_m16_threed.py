"""TDD spec for M16 -- 3D rigid-body / top / gyroscope."""

from __future__ import annotations

import pytest

from physics_through_anim.physics.mechanics3d.bodies3d import Gyroscope, Top

TDD = pytest.mark.xfail(reason="M16 not implemented (TDD spec)", strict=False)


def test_top_defaults() -> None:
    t = Top(tilt_deg=20.0, spin_omega=20.0, precession_omega=1.5)
    assert t.pivot == (0.0, 0.0, 0.0)
    assert Gyroscope().gimbal is True


@TDD
def test_top_as_trajectory() -> None:
    Top().as_trajectory(period=8.0)
