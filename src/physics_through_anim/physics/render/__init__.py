"""Renderers that turn declarative specs (assets, overlays, recipes) into Manim
mobjects/scenes. Nothing else depends on render.
"""

from physics_through_anim.physics.render.layout import (
    Layout,
    Region,
    avoid_overlap,
    standard_bands,
)
from physics_through_anim.physics.render.mask import Mask, PathMask, garment_along_path
from physics_through_anim.physics.render.skins import radial_polygon, rock_skin

__all__ = [
    "Layout",
    "Mask",
    "PathMask",
    "Region",
    "avoid_overlap",
    "garment_along_path",
    "radial_polygon",
    "rock_skin",
    "standard_bands",
]
