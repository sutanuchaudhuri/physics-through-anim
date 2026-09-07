"""Textbook compositions that return a Recipe (per-domain subpackages) from generic assets."""

from physics_through_anim.physics.recipes.base import Recipe
from physics_through_anim.physics.recipes.catalogue import (
    FAMILIES,
    atwood,
    chain_over_edge,
    cylinder_at_table_edge,
    galperin,
    kepler_orbit,
    mass_spring,
)

__all__ = [
    "FAMILIES",
    "Recipe",
    "atwood",
    "chain_over_edge",
    "cylinder_at_table_edge",
    "galperin",
    "kepler_orbit",
    "mass_spring",
]
