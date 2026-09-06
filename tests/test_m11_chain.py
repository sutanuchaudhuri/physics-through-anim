"""TDD spec for M11 -- chains / distributed bodies."""

from __future__ import annotations

import pytest

from physics_through_anim.physics.mechanics.chain import Chain, ChainRender, ChainShapeState

TDD = pytest.mark.xfail(reason="M11 not implemented (TDD spec)", strict=False)


def test_chain_render_and_defaults() -> None:
    assert {r.value for r in ChainRender} == {"continuous", "linked"}
    assert Chain(length=3.0).render is ChainRender.CONTINUOUS
    assert ChainShapeState().path is None


@TDD
def test_chain_com() -> None:
    Chain(length=3.0, path=lambda s: __import__("numpy").array([s, 0.0, 0.0])).com()
