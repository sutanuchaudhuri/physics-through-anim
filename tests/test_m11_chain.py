"""Tests for M11 -- chains / distributed bodies."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.mechanics.chain import (
    Chain,
    ChainRender,
    ChainShapeState,
)


def _line_path(s):
    return np.array([s, 0.0, 0.0])


def test_chain_render_and_defaults() -> None:
    assert {r.value for r in ChainRender} == {"continuous", "linked"}
    assert Chain(length=3.0).render is ChainRender.CONTINUOUS
    assert ChainShapeState().path is None


def test_linear_density_defaults_to_mass_over_length() -> None:
    assert np.isclose(Chain(mass=6.0, length=3.0).linear_density, 2.0)


def test_endpoints_and_com() -> None:
    chain = Chain(path=_line_path, n_links=20)
    assert np.allclose(chain.keypoint("A")[:2], (0.0, 0.0))
    assert np.allclose(chain.keypoint("B")[:2], (1.0, 0.0))
    assert np.allclose(chain.com()[:2], (0.5, 0.0), atol=1e-6)  # mean of uniform samples


def test_continuous_is_one_vmobject_linked_has_n_links() -> None:
    cont = Chain(render=ChainRender.CONTINUOUS, path=_line_path)
    assert len(cont.mobject.submobjects) == 1
    linked = Chain(render=ChainRender.LINKED, n_links=12, path=_line_path)
    assert len(linked.mobject.submobjects) == 12


def test_material_markers_register_keypoints() -> None:
    chain = Chain(path=_line_path, material_markers=(0.0, 0.5, 1.0))
    assert np.allclose(chain.keypoint("mark@0.5")[:2], (0.5, 0.0))
    assert np.allclose(chain.keypoint("mark@1.0")[:2], (1.0, 0.0))


def test_set_path_moves_endpoints_and_com() -> None:
    chain = Chain(path=_line_path)
    chain.set_path(lambda s: np.array([0.0, 2.0 * s, 0.0]))  # now vertical, length 2
    assert np.allclose(chain.keypoint("A")[:2], (0.0, 0.0))
    assert np.allclose(chain.keypoint("B")[:2], (0.0, 2.0))
    assert np.allclose(chain.com()[:2], (0.0, 1.0), atol=1e-6)


def test_portion_ends_at_material_coords() -> None:
    chain = Chain(path=_line_path)
    sub = chain.portion(0.25, 0.75)
    pts = sub.points
    assert np.allclose(pts[0][:2], (0.25, 0.0), atol=1e-6)
    assert np.allclose(pts[-1][:2], (0.75, 0.0), atol=1e-6)
