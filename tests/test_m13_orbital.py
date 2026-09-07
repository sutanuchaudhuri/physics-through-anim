"""Tests for M13 -- orbital / central-force geometry + Kepler timing."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.mechanics.kinds import ForceKind
from physics_through_anim.physics.mechanics.orbital import (
    CentralBody,
    KeplerEllipseTrajectory,
    OrbitPath,
    toward,
)
from physics_through_anim.physics.mechanics.palette import COLOR_GRAVITY, FORCE_COLORS


def test_orbit_defaults() -> None:
    o = OrbitPath(a=3.0, e=0.5, focus=(-1.5, 0.0))
    assert o.a == 3.0 and o.e == 0.5
    assert CentralBody(label="M").label == "M"


def test_apsides_at_correct_distances_from_focus() -> None:
    o = OrbitPath(a=3.0, e=0.5, focus=(0.0, 0.0))
    focus = np.array([0.0, 0.0])
    assert np.isclose(np.linalg.norm(o.periapsis()[:2] - focus), 3.0 * (1 - 0.5))
    assert np.isclose(np.linalg.norm(o.apoapsis()[:2] - focus), 3.0 * (1 + 0.5))


def test_point_at_periapsis_and_apoapsis() -> None:
    o = OrbitPath(a=3.0, e=0.5, focus=(0.0, 0.0))
    np.testing.assert_allclose(o.point_at(0.0), o.periapsis(), atol=1e-9)
    np.testing.assert_allclose(o.point_at(np.pi), o.apoapsis(), atol=1e-9)


def test_orbit_keypoints_registered() -> None:
    o = OrbitPath(a=3.0, e=0.5, focus=(-1.5, 0.0))
    assert np.allclose(o.keypoint("focus")[:2], (-1.5, 0.0))
    # Two foci are 2*a*e apart along the major axis.
    sep = np.linalg.norm(o.keypoint("focus")[:2] - o.keypoint("other_focus")[:2])
    assert np.isclose(sep, 2 * 3.0 * 0.5)


def test_toward_direction() -> None:
    d = toward((1.0, 0.0))((0.0, 0.0))
    assert np.allclose(d, (1.0, 0.0))
    d2 = toward((0.0, 0.0))((3.0, 4.0))  # unit(sun - planet)
    assert np.allclose(d2, (-0.6, -0.8))


def test_gravity_colour_distinct_from_weight() -> None:
    from manim import ManimColor
    g = ManimColor(FORCE_COLORS[ForceKind.GRAVITY]).to_hex()
    assert g == ManimColor(COLOR_GRAVITY).to_hex()
    assert g != ManimColor(FORCE_COLORS[ForceKind.WEIGHT]).to_hex()


def _sector_area(orbit, theta0, theta1, n=200):
    focus = orbit._focus3()[:2]
    pts = [orbit.point_at(theta0 + (theta1 - theta0) * i / n)[:2] for i in range(n + 1)]
    area = 0.0
    for p, q in zip(pts[:-1], pts[1:], strict=True):
        u, v = p - focus, q - focus
        area += 0.5 * abs(u[0] * v[1] - u[1] * v[0])
    return area


def test_kepler_equal_areas_in_equal_times() -> None:
    # Kepler II: the focus-sector area swept in a fixed dt is the same near peri and apo.
    orbit = OrbitPath(a=3.0, e=0.5, focus=(0.0, 0.0))
    traj = KeplerEllipseTrajectory(orbit=orbit, period=8.0)
    dt = 0.4

    def theta_at(t):
        return traj.state_at(t).observables["theta"]

    # near periapsis (t~0) vs near apoapsis (t~period/2)
    area_peri = _sector_area(orbit, theta_at(0.0), theta_at(dt))
    area_apo = _sector_area(orbit, theta_at(4.0), theta_at(4.0 + dt))
    assert np.isclose(area_peri, area_apo, rtol=0.05)


def test_kepler_periapsis_at_t0() -> None:
    orbit = OrbitPath(a=3.0, e=0.5, focus=(0.0, 0.0))
    traj = KeplerEllipseTrajectory(orbit=orbit, period=8.0)
    pos = traj.state_at(0.0).entities["m"].pose.position
    np.testing.assert_allclose(pos, orbit.periapsis()[:2], atol=1e-6)

