"""M5 spec -- Rod body."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.mechanics.kinds import ForceKind
from physics_through_anim.physics.mechanics.rod import Rod


def test_rod_defaults() -> None:
    r = Rod(length=2.0)
    assert r.massless is False
    assert r.length == 2.0


def test_rod_point_at_endpoints() -> None:
    r = Rod(length=2.0, center=(0.0, 0.0), angle_deg=0.0)
    a = r.point_at(0.0)
    b = r.point_at(1.0)
    assert abs(float(np.linalg.norm(b - a)) - 2.0) < 1e-9


def test_rod_keypoints_A_B_CM() -> None:
    r = Rod(length=2.0, center=(1.0, 0.5), angle_deg=90.0)
    np.testing.assert_allclose(r.keypoint("CM"), [1.0, 0.5, 0.0])
    np.testing.assert_allclose(r.keypoint("A"), [1.0, -0.5, 0.0], atol=1e-9)
    np.testing.assert_allclose(r.keypoint("B"), [1.0, 1.5, 0.0], atol=1e-9)


def test_massless_rod_omits_weight() -> None:
    weighted = [f for f in Rod().forces if f.kind is ForceKind.WEIGHT]
    massless = [f for f in Rod(massless=True).forces if f.kind is ForceKind.WEIGHT]
    assert len(weighted) == 1
    assert massless == []

