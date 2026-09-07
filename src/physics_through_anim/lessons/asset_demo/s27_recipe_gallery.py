"""Scene 27 -- M15 recipe gallery: textbook compositions render from generic assets.

Each thumbnail is a ``Recipe``'s assembly (built from generic assets by a single
recipe call) scaled into a cell. The full 20-family regression sweep is exercised
by ``tests/test_m15_recipes.py``; this is the visual health check for a
representative subset -- the four architecture probes plus common families.
"""

from __future__ import annotations

from manim import DOWN, WHITE, FadeIn, Text, VGroup

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.recipes.catalogue import (
    atwood,
    block_on_floor,
    chain_over_edge,
    cylinder_at_table_edge,
    disk_on_incline,
    galperin,
    kepler_orbit,
    physical_pendulum,
)
from physics_through_anim.physics.render.layout import Anchor, Region, stage_region

GALLERY = [
    ("translation", block_on_floor),
    ("rolling", disk_on_incline),
    ("pulley", atwood),
    ("hinge", physical_pendulum),
    ("edge (probe A)", cylinder_at_table_edge),
    ("distributed (C)", chain_over_edge),
    ("repeated collision (D)", galperin),
    ("orbit (probe B)", kepler_orbit),
]


class RecipeGallery(AssetDemoScene):
    """A grid of recipe thumbnails -- each a one-call composition of generic assets."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("27", "The recipe gallery", "textbook scenes in one call each")
        self.play(FadeIn(header))

        # A 2x4 thumbnail grid straight from the stage region -- no magic numbers.
        cells = VGroup()
        for cell, (name, recipe_fn) in zip(
                stage_region(ground_y=-2.3, top=2.2).grid(2, 4, gap=0.3), GALLERY, strict=False):
            thumb_box = Region(cell.x_min, cell.x_max, cell.y_min + 0.45, cell.y_max, cell.name)
            frame = thumb_box.as_rect(color="#495057", stroke_width=1.5)
            thumb = thumb_box.fit(recipe_fn().assembly.mobject.copy(), padding=0.22)
            label = Text(name, font_size=16, color=WHITE).move_to(
                cell.anchor(Anchor.BOTTOM, offset=(0.0, 0.12)))
            cells.add(VGroup(frame, thumb, label))

        self.play(*[FadeIn(c) for c in cells], run_time=1.5)
        cap = Text("one call each -> a full Assembly + timeline + trajectories",
                   font_size=20, color=WHITE).to_edge(DOWN, buff=0.25)
        self.play(FadeIn(cap))
        self.wait(0.6)
        self.finish_with_narration()
