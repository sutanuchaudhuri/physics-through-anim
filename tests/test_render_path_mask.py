"""Tests for the path garment mask (render) + chain skin wiring."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.mechanics.chain import Chain
from physics_through_anim.physics.render.mask import PathMask, garment_along_path


def _line_path(s):
    return np.array([s, 0.0, 0.0])


def test_garment_is_transparent_closed_ribbon() -> None:
    ribbon = garment_along_path(_line_path, width=0.4, opacity=0.4, n=20)
    assert ribbon.get_num_points() > 0
    assert 0.0 < ribbon.get_fill_opacity() < 1.0  # semi-transparent garment


def test_path_mask_build_and_follow_reshape() -> None:
    mask = PathMask(width=0.4, opacity=0.35, n=20)
    mask.build(_line_path)
    before = mask.mobject.get_center().copy()
    mask.follow(lambda s: np.array([0.0, 2.0 * s, 0.0]))  # now vertical
    assert not np.allclose(mask.mobject.get_center(), before)  # reshaped in place


def test_chain_skin_builder_builds_and_tracks_path() -> None:
    mask = PathMask(width=0.3, opacity=0.4)
    chain = Chain(path=_line_path, skin_builder=mask.as_builder())
    assert chain.skin is not None  # garment built on top of the skeleton
    assert len(chain.mobject.submobjects) == 1  # skeleton stays a single vector
    skin0 = chain.skin.get_center().copy()
    chain.set_path(lambda s: np.array([0.0, 3.0 * s, 0.0]))
    assert not np.allclose(chain.skin.get_center(), skin0)  # skin follows the skeleton


def test_attach_skin_after_construction() -> None:
    chain = Chain(path=_line_path)
    assert chain.skin is None
    chain.attach_skin(PathMask().as_builder())
    assert chain.skin is not None
