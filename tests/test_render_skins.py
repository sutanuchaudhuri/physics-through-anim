"""Render skins: rock/silhouette from a shape-signature input vector."""

from __future__ import annotations

import numpy as np
import pytest

from physics_through_anim.physics.render import radial_polygon, rock_skin


def test_radial_polygon_vertex_count_and_radius() -> None:
    poly = radial_polygon([1.0, 1.0, 1.0, 1.0], radius=2.0)
    verts = poly.get_vertices()
    assert len(verts) == 4
    # first vertex at angle 0 -> (radius, 0)
    np.testing.assert_allclose(verts[0][:2], [2.0, 0.0], atol=1e-9)


def test_radial_polygon_needs_three_radii() -> None:
    with pytest.raises(ValueError, match="at least 3"):
        radial_polygon([1.0, 1.0])


def test_rock_skin_is_reproducible_for_a_seed() -> None:
    a = rock_skin(radius=0.6, sides=9, seed=3)
    b = rock_skin(radius=0.6, sides=9, seed=3)
    np.testing.assert_allclose(a.get_vertices(), b.get_vertices(), atol=1e-12)


def test_rock_skin_fits_within_the_radius_envelope() -> None:
    rock = rock_skin(radius=0.6, sides=12, jitter=0.2, seed=1)
    radii = np.linalg.norm(rock.get_vertices()[:, :2], axis=1)
    assert radii.max() <= 0.6 * 1.2 + 1e-9  # within (1 + jitter) * radius
