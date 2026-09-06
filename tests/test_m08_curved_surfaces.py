"""TDD spec for M8 -- curved surfaces / table / edge."""

from __future__ import annotations

import pytest

from physics_through_anim.physics.mechanics.surfaces_curved import (
    CircularTrack,
    ConcaveSurface,
    ConvexSurface,
    Peg,
    Rail,
    SharpEdge,
    Slot,
    Table,
)

TDD = pytest.mark.xfail(reason="M8 not implemented (TDD spec)", strict=False)


def test_curved_surface_catalogue_exists() -> None:
    assert CircularTrack(radius=2.0).radius == 2.0
    assert ConvexSurface().radius == 2.0
    assert ConcaveSurface().radius == 2.0
    assert Table(right=1.0).right == 1.0
    assert Peg().radius == 0.06
    assert Slot().gap == 0.2
    assert isinstance(Rail(), object)


@TDD
def test_circular_track_curvature() -> None:
    assert abs(CircularTrack(radius=2.0).curvature_at(0.5) - 0.5) < 1e-6


@TDD
def test_table_edge_and_sharp_edge() -> None:
    Table().edge()
    SharpEdge(at=(1.0, 0.5)).point()
