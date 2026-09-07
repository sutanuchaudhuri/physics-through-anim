"""Scene 18 -- M11 flagship (probe C): a chain slides over a table edge.

The chain is a distributed body with a material coordinate. Each frame a supplied
path splits it into a part resting on the table and a part hanging past the sharp
edge, with the split point sliding as the chain pours off. Overlays read straight
off the shape: the mass-weighted COM marker drifts, the supported portion (green)
shrinks while the free portion (orange) grows, and material tags show which piece
of chain is which. No solver -- the shape comes from the path; the asset just
renders it.
"""

from __future__ import annotations

import numpy as np
from manim import DOWN, GREEN, ORANGE, WHITE, YELLOW, Dot, FadeIn, Text, ValueTracker

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.mechanics import Assembly, Chain, ChainRender, Floor, Table

GROUND_Y = -2.6
EDGE_X = 1.2
TOP_Y = 0.6
LENGTH = 3.2


class ChainOverEdge(AssetDemoScene):
    """A chain pours over the table's sharp edge; COM + portions track the shape."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("18", "Chain over a table edge", "distributed mass, probe C")
        self.play(FadeIn(header))

        a = Assembly()
        floor = Floor(y=GROUND_Y, half_width=6.0)
        table = Table(top_y=TOP_Y, left=-3.4, right=EDGE_X, leg_bottom=GROUND_Y)
        a.add(floor)
        a.add(table)
        edge = table.edge()

        # A supplied path: material s in [0,1] from the table tail to the hanging head.
        def path_for(split: float):
            def path(s: float) -> np.ndarray:
                if s <= split:
                    return np.array([EDGE_X - (split - s) * LENGTH, TOP_Y, 0.0])
                return np.array([EDGE_X, TOP_Y - (s - split) * LENGTH, 0.0])
            return path

        chain = Chain(name="chain", mass=2.0, length=LENGTH, render=ChainRender.CONTINUOUS,
                      material_markers=(0.0, 0.5, 1.0), path=path_for(0.72))
        self.add(chain.mobject)

        split0 = 0.72
        com_dot = Dot(chain.com(), color=YELLOW, radius=0.09)
        supported = chain.portion(0.0, split0, color=GREEN)
        free = chain.portion(split0, 1.0, color=ORANGE)
        marks = [Dot(chain.keypoint(f"mark@{s}"), color=WHITE, radius=0.06)
                 for s in (0.0, 0.5, 1.0)]
        edge_dot = Dot(edge.point(), color=YELLOW, radius=0.06)

        legend = Text("green = on the table (supported), orange = hanging (free)",
                      font_size=21, color=WHITE).to_edge(DOWN, buff=0.75)
        cap = Text("COM drifts toward the edge as the chain pours over",
                   font_size=21, color=YELLOW).to_edge(DOWN, buff=0.4)
        self.play(FadeIn(a.mobject), FadeIn(chain.mobject), FadeIn(edge_dot))
        self.play(FadeIn(supported), FadeIn(free), FadeIn(com_dot), *[FadeIn(m) for m in marks],
                  FadeIn(legend), FadeIn(cap))

        t = ValueTracker(0.0)

        def refresh(_m):
            split = split0 + (0.12 - split0) * t.get_value()
            chain.set_path(path_for(split))
            com_dot.move_to(chain.com())
            supported.become(chain.portion(0.0, split, color=GREEN))
            free.become(chain.portion(split, 1.0, color=ORANGE))
            for dot, s in zip(marks, (0.0, 0.5, 1.0), strict=True):
                dot.move_to(chain.keypoint(f"mark@{s}"))

        chain.mobject.add_updater(refresh)
        self.play(t.animate.set_value(1.0), run_time=5.0)
        chain.mobject.clear_updaters()
        self.wait(0.4)
        self.finish_with_narration()
