"""Tests for M15 -- recipe catalogue + regression gallery."""

from __future__ import annotations

import pytest

from physics_through_anim.physics.recipes.base import Recipe
from physics_through_anim.physics.recipes.catalogue import (
    FAMILIES,
    chain_over_edge,
    cylinder_at_table_edge,
    galperin,
    kepler_orbit,
)


def test_recipe_holds_specs() -> None:
    r = Recipe(moments={"apoapsis": 4.0})
    assert r.moments["apoapsis"] == 4.0
    assert isinstance(r.overlays, dict)


def test_recipe_named_resolves_body_and_moment() -> None:
    r = kepler_orbit()
    assert r.named("sun") is r.assembly.body("sun")
    assert r.named("periapsis") == 0.0
    with pytest.raises(KeyError):
        r.named("nope")


def test_kepler_recipe_has_planet_and_trajectory() -> None:
    r = kepler_orbit(e=0.6, period=10.0)
    assert r.assembly.body("m") is not None
    assert "m" in r.trajectories
    assert r.moments["apoapsis"] == 5.0


def test_table_edge_recipe_has_contact_then_separation() -> None:  # PROBE A
    r = cylinder_at_table_edge()
    tags = [e.tag for e in r.events.events]
    assert "edge_contact" in tags and "separation" in tags


def test_chain_recipe_has_chain_and_edge_anchor() -> None:  # PROBE C
    r = chain_over_edge()
    chain = r.assembly.body("chain")
    assert chain.com() is not None  # a distributed body with a defined COM
    assert "edge" in r.camera_anchors


def test_galperin_recipe_impacts_grow() -> None:  # PROBE D
    r = galperin()
    assert r.events.count >= 3
    assert all(e.kind.value == "impact" for e in r.events.events)


@pytest.mark.parametrize("family", sorted(FAMILIES))
def test_every_family_constructs(family: str) -> None:
    recipe = FAMILIES[family]()  # the regression sweep: build one per family
    assert isinstance(recipe, Recipe)
    assert recipe.assembly is not None

