"""Scene 07 -- M5 asset gallery: one small render per catalogue family (QA).

A grid of the M1-M5 assets, each labelled -- the visual "one small render per
family" check that the whole catalogue builds and looks right.
"""

from __future__ import annotations

from manim import DOWN, FadeIn, Text, VGroup

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.mechanics import (
    Block,
    Cylinder,
    Disk,
    Hinge,
    Incline,
    Pulley,
    Ring,
    Rod,
    Rope,
)


class AssetGallery(AssetDemoScene):
    """A labelled grid of every asset family (M1-M5)."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("07", "Asset gallery", "one render per family")
        self.play(FadeIn(header))

        families = [
            ("Block", Block(width=1.0)),
            ("Disk", Disk(radius=0.5)),
            ("Ring", Ring(radius=0.5)),
            ("Cylinder", Cylinder(radius=0.5)),
            ("Rod", Rod(length=1.2, angle_deg=25.0)),
            ("Incline", Incline(angle_deg=28.0, length=1.6, base=(-0.8, -0.6), on_floor=True)),
            ("Pulley", Pulley(center=(0.0, 0.0), radius=0.5)),
            ("Rope", Rope(from_point=(-0.1, 0.6), to_point=(0.1, -0.6), slips=True)),
            ("Hinge", Hinge(at=(0.0, 0.0))),
        ]

        tiles = VGroup()
        for name, asset in families:
            asset.mobject.scale(0.7)
            label = Text(name, font_size=20)
            tiles.add(VGroup(asset.mobject, label).arrange(DOWN, buff=0.25))
        tiles.arrange_in_grid(rows=3, cols=3, buff=0.7)
        tiles.scale_to_fit_height(4.8).move_to([0.0, -0.3, 0.0])

        self.play(FadeIn(tiles))
        self.wait(0.6)
        self.finish_with_narration()
