"""Tests for declarative anchor-based layout (Region.anchor / columns / rows)."""

from __future__ import annotations

from enum import StrEnum

import numpy as np

from physics_through_anim.physics.render.layout import (
    Anchor,
    NamedPoints,
    Region,
    stage_region,
)


def _region() -> Region:
    return Region(-4.0, 4.0, -2.0, 2.0, "r")


def test_anchor_named_positions() -> None:
    r = _region()
    assert np.allclose(r.anchor(Anchor.CENTER), (0.0, 0.0, 0.0))
    assert np.allclose(r.anchor(Anchor.TOP_LEFT), (-4.0, 2.0, 0.0))
    assert np.allclose(r.anchor(Anchor.BOTTOM_RIGHT), (4.0, -2.0, 0.0))
    assert np.allclose(r.anchor(Anchor.BOTTOM), (0.0, -2.0, 0.0))


def test_anchor_offset_is_override() -> None:
    r = _region()
    assert np.allclose(r.anchor(Anchor.CENTER, offset=(1.0, -0.5)), (1.0, -0.5, 0.0))


def test_anchor_padding_insets() -> None:
    r = _region()
    assert np.allclose(r.anchor(Anchor.TOP_LEFT, pad=0.5), (-3.5, 1.5, 0.0))


def test_columns_split_evenly() -> None:
    left, right = _region().columns(2)
    assert np.isclose(left.width, 4.0) and np.isclose(right.width, 4.0)
    assert np.allclose(left.anchor(Anchor.CENTER), (-2.0, 0.0, 0.0))
    assert np.allclose(right.anchor(Anchor.CENTER), (2.0, 0.0, 0.0))


def test_columns_with_gap() -> None:
    cols = _region().columns(2, gap=1.0)
    assert np.isclose(cols[0].width, 3.5)  # (8 - 1) / 2
    assert cols[0].x_max < cols[1].x_min  # a real gap between them


def test_rows_top_first() -> None:
    top, bottom = _region().rows(2)
    assert top.anchor(Anchor.CENTER)[1] > bottom.anchor(Anchor.CENTER)[1]


def test_stage_region_columns_give_panels() -> None:
    left, right = stage_region().columns(2, gap=0.4)
    assert left.anchor(Anchor.CENTER)[0] < 0 < right.anchor(Anchor.CENTER)[0]


def test_grid_is_row_major() -> None:
    cells = _region().grid(2, 4)
    assert len(cells) == 8
    # first cell top-left, last cell bottom-right
    assert cells[0].anchor(Anchor.CENTER)[1] > cells[-1].anchor(Anchor.CENTER)[1]
    assert cells[0].anchor(Anchor.CENTER)[0] < cells[3].anchor(Anchor.CENTER)[0]


# --- NamedPoints: reference coordinates by id/enum -----------------------


def test_named_points_define_and_access_by_id() -> None:
    pts = NamedPoints().define(A=(-4.5, 1.2), B=(1.5, 1.2))
    assert np.allclose(pts["A"], (-4.5, 1.2))
    assert "B" in pts and pts.get("C") is None


def test_named_points_distance_and_vector_by_id() -> None:
    pts = NamedPoints().define(A=(0.0, 0.0), B=(3.0, 4.0))
    assert np.isclose(pts.distance("A", "B"), 5.0)  # translation distance by id
    assert np.allclose(pts.vector("A", "B"), (3.0, 4.0))
    assert np.allclose(pts.midpoint("A", "B"), (1.5, 2.0))


def test_named_points_accept_strenum_keys() -> None:
    class P(StrEnum):
        LEFT_END = "L"
        RIGHT_END = "R"

    pts = NamedPoints()
    pts.set(P.LEFT_END, (-2.0, 0.0))
    pts.set(P.RIGHT_END, (2.0, 0.0))
    assert np.allclose(pts[P.LEFT_END], (-2.0, 0.0))
    assert np.isclose(pts.distance(P.LEFT_END, P.RIGHT_END), 4.0)


def test_named_points_at_region_anchor() -> None:
    pts = NamedPoints()
    pts.at("corner", Region(-4.0, 4.0, -2.0, 2.0), Anchor.TOP_LEFT)
    assert np.allclose(pts["corner"], (-4.0, 2.0))


