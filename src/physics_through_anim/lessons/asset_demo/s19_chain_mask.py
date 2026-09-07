"""Scene 19 -- a garment mask over the chain skeleton, faded to reveal the vector.

The chain's physics is a line vector (the skeleton). A ``PathMask`` builds a
transparent garment that hugs that path and rides on top of it. As the chain
moves the garment tracks the skeleton; then the garment fades out, revealing the
bare vector underneath -- mask as costume, skeleton as physics.
"""

from __future__ import annotations

import numpy as np
from manim import DOWN, WHITE, FadeIn, FadeOut, Text, ValueTracker

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.mechanics import Chain, ChainRender
from physics_through_anim.physics.render import PathMask

LENGTH = 5.0


class ChainGarmentMask(AssetDemoScene):
    """Transparent garment over the skeleton line; drape, then fade to the vector."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("19", "Mask over the skeleton", "garment vs vector")
        self.play(FadeIn(header))

        # A draping catenary-ish path: material s in [0,1] across a sagging span.
        def path_for(sag: float):
            def path(s: float) -> np.ndarray:
                x = -LENGTH / 2.0 + s * LENGTH
                y = -sag * (1.0 - (2.0 * s - 1.0) ** 2)  # 0 at ends, -sag at middle
                return np.array([x, y + 0.6, 0.0])
            return path

        mask = PathMask(width=0.5, color="#74C0FC", opacity=0.4, n=80)
        chain = Chain(name="chain", mass=2.0, length=LENGTH, render=ChainRender.CONTINUOUS,
                      path=path_for(1.4), skin_builder=mask.as_builder())

        # Skeleton first, garment ON TOP.
        self.add(chain.mobject, chain.skin)
        skel_label = Text("skeleton = the line vector (physics)", font_size=22, color=WHITE)
        skel_label.to_edge(DOWN, buff=0.75)
        garment_label = Text("mask = transparent garment on top (cosmetic)",
                             font_size=22, color="#74C0FC").to_edge(DOWN, buff=0.4)
        self.play(FadeIn(chain.mobject), FadeIn(skel_label))
        self.play(FadeIn(chain.skin), FadeIn(garment_label))

        # The garment tracks the skeleton as the drape changes.
        sag = ValueTracker(1.4)

        def redrape(_m):
            chain.set_path(path_for(sag.get_value()))

        chain.mobject.add_updater(redrape)
        self.play(sag.animate.set_value(0.4), run_time=2.0)
        self.play(sag.animate.set_value(1.6), run_time=2.0)
        chain.mobject.clear_updaters()

        # Fade the garment out -> the bare vector skeleton remains.
        reveal = Text("fade the mask -> the skeleton vector remains",
                      font_size=22, color=WHITE).to_edge(DOWN, buff=0.4)
        self.play(FadeOut(chain.skin), FadeOut(garment_label), FadeIn(reveal))
        self.wait(0.5)
        self.finish_with_narration()
