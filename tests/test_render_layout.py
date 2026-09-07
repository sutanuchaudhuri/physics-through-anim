"""Tests for the deterministic render layout regions (physics/render/layout)."""

from __future__ import annotations

import numpy as np
from manim import RIGHT, UP, Dot, Rectangle, Square

from physics_through_anim.physics.render.layout import (
    Layout,
    Region,
    avoid_overlap,
    standard_bands,
)


def test_region_geometry() -> None:
    r = Region(-2.0, 2.0, -1.0, 1.0)
    assert r.width == 4.0
    assert r.height == 2.0
    np.testing.assert_allclose(r.center, [0.0, 0.0, 0.0])


def test_region_contains() -> None:
    r = Region(-2.0, 2.0, -1.0, 1.0)
    assert r.contains(Square(side_length=0.5).move_to([0.0, 0.0, 0.0]))
    assert not r.contains(Square(side_length=3.0).move_to([0.0, 0.0, 0.0]))


def test_fit_scales_and_centres_oversized_mob() -> None:
    r = Region(-1.0, 1.0, -1.0, 1.0)  # 2 x 2
    m = Square(side_length=5.0)
    r.fit(m, padding=0.1)
    assert m.width <= 2.0 - 0.2 + 1e-6
    assert r.contains(m)  # now inside the region boundary
    np.testing.assert_allclose(m.get_center()[:2], [0.0, 0.0], atol=1e-6)


def test_standard_bands_do_not_overlap_vertically() -> None:
    b = standard_bands()
    assert b["header"].y_min > b["stage"].y_max  # header sits above the stage
    assert b["stage"].y_min >= b["equation"].y_max  # stage sits above the equation band


def test_place_puts_formula_in_equation_band() -> None:
    layout = Layout.standard()
    formula = Rectangle(width=2.0, height=0.4)
    layout.place(formula, "equation", align="center")
    assert layout.region("equation").contains(formula)


def test_avoid_overlap_picks_a_clear_side() -> None:
    anchor = Dot([0.0, 0.0, 0.0])
    obstacle = Rectangle(width=0.5, height=1.0).move_to([0.0, 0.6, 0.0])  # narrow, directly above
    label = Square(side_length=0.3)
    avoid_overlap(label, anchor, [obstacle], dirs=(UP, RIGHT))
    # UP overlaps the obstacle, so it must fall through to RIGHT.
    assert label.get_center()[0] > 0.1
