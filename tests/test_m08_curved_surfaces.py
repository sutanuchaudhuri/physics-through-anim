"""M8 spec -- curved surfaces / table / edge."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.mechanics.surfaces_curved import (
    CircularTrack,
    ConcaveSurface,
    ConvexSurface,
    Peg,
    Rail,
    Slot,
    Table,
    separation_imminent,
)


def test_curved_surface_catalogue_exists() -> None:
    assert CircularTrack(radius=2.0).radius == 2.0
    assert ConvexSurface().radius == 2.0
    assert ConcaveSurface().radius == 2.0
    assert Table(right=1.0).right == 1.0
    assert Peg().radius == 0.06
    assert Slot().gap == 0.2
    assert isinstance(Rail(), object)


def test_circular_track_geometry() -> None:
    track = CircularTrack(center=(0.0, 0.0), radius=2.0, arc=(0.0, 2.0 * np.pi))
    assert abs(track.curvature_at(0.5) - 0.5) < 1e-6  # 1/R
    p = track.point_at(0.0)  # angle 0 -> (R, 0)
    np.testing.assert_allclose(p, [2.0, 0.0, 0.0], atol=1e-9)
    # normal at angle 0 points outward along +x
    np.testing.assert_allclose(track.normal_at(0.0), [1.0, 0.0, 0.0], atol=1e-9)


def test_convex_points_out_concave_points_in() -> None:
    convex = ConvexSurface(center=(0.0, 0.0), radius=1.0)
    concave = ConcaveSurface(center=(0.0, 0.0), radius=1.0)
    # at angle 0 the outward radial is +x
    np.testing.assert_allclose(convex.normal_at(0.0), [1.0, 0.0, 0.0], atol=1e-9)
    np.testing.assert_allclose(concave.normal_at(0.0), [-1.0, 0.0, 0.0], atol=1e-9)


def test_table_edge_and_sharp_edge() -> None:
    table = Table(top_y=0.5, right=1.0)
    edge = table.edge()
    np.testing.assert_allclose(edge.point(), [1.0, 0.5, 0.0])
    np.testing.assert_allclose(edge.keypoint("E"), [1.0, 0.5, 0.0])
    np.testing.assert_allclose(table.keypoint("edge"), [1.0, 0.5, 0.0])


def test_table_top_surface_endpoints() -> None:
    table = Table(top_y=0.5, left=-3.0, right=1.0)
    surf = table.top_surface()
    np.testing.assert_allclose(surf.point_at(0.0)[:2], [-3.0, 0.5], atol=1e-9)
    np.testing.assert_allclose(surf.point_at(1.0)[:2], [1.0, 0.5], atol=1e-9)


def test_rail_is_flat_and_slot_yields_a_constraint() -> None:
    rail = Rail(a=(0.0, 0.0), b=(2.0, 0.0))
    assert rail.curvature_at(0.5) == 0.0
    assert Slot(participants=("bead", "slot")).guide_constraint().slot == "slot"


def test_separation_imminent_at_zero_normal() -> None:
    assert separation_imminent(0.0) is True
    assert separation_imminent(-0.1) is True
    assert separation_imminent(1.0) is False

