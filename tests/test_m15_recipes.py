"""TDD spec for M15 -- recipe catalogue."""

from __future__ import annotations

import pytest

from physics_through_anim.physics.recipes.base import Recipe

TDD = pytest.mark.xfail(reason="M15 not implemented (TDD spec)", strict=False)


def test_recipe_holds_specs() -> None:
    r = Recipe(moments={"apoapsis": 4.0})
    assert r.moments["apoapsis"] == 4.0
    assert isinstance(r.overlays, dict)


@TDD
def test_recipe_named_resolves() -> None:
    Recipe().named("disk")
