"""Scene 16 -- M10: series & parallel spring banks from one helper each.

Two banks between one pair of connectors apiece: a series stack (1/k = Sum 1/k_i,
coils end-to-end joined by junction dots) and a parallel stack (k = Sum k_i, coils
sharing the same two endpoints). The effective stiffness is a local label, not a
solve. Note how little code composes each bank.
"""

from __future__ import annotations

from enum import StrEnum

from manim import DOWN, UP, WHITE, FadeIn, MathTex, Text

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.mechanics import (
    LinearSpring,
    parallel_springs,
    series_springs,
)
from physics_through_anim.physics.mechanics.palette import COLOR_SPRING
from physics_through_anim.physics.render.layout import NamedPoints


class End(StrEnum):
    """Named spring-bank endpoints -- referenced by id, never by raw tuple."""

    SERIES_L = "series_L"
    SERIES_R = "series_R"
    PARALLEL_L = "parallel_L"
    PARALLEL_R = "parallel_R"


class SpringBanks(AssetDemoScene):
    """A series bank and a parallel bank, each built by one helper call."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("16", "Series & parallel springs", "one helper each")
        self.play(FadeIn(header))

        # Define the connection points once, by id; reference them everywhere.
        pts = NamedPoints().define(
            series_L=(-4.5, 1.2), series_R=(1.5, 1.2),
            parallel_L=(-4.5, -1.4), parallel_R=(-0.5, -1.4),
        )

        series = series_springs(
            [LinearSpring(k=4.0, coils=6), LinearSpring(k=4.0, coils=6),
             LinearSpring(k=4.0, coils=6)],
            from_point=pts[End.SERIES_L], to_point=pts[End.SERIES_R],
        )
        parallel = parallel_springs(
            [LinearSpring(k=3.0, coils=8), LinearSpring(k=5.0, coils=8)],
            from_point=pts[End.PARALLEL_L], to_point=pts[End.PARALLEL_R], offset=0.5,
        )

        s_label = Text("series: coils end-to-end, junction connectors",
                       font_size=22, color=WHITE).next_to(series.mobject, UP, buff=0.35)
        s_eff = MathTex(
            r"\frac{1}{k_{eff}}=\sum\frac{1}{k_i}\;\Rightarrow\;k_{eff}="
            + f"{series.k_eff:.2f}", color=COLOR_SPRING, font_size=34)
        s_eff.next_to(series.mobject, DOWN, buff=0.3)
        self.play(FadeIn(series.mobject), FadeIn(s_label))
        self.play(FadeIn(s_eff))

        p_label = Text("parallel: coils share both connectors",
                       font_size=22, color=WHITE).next_to(parallel.mobject, UP, buff=0.35)
        p_eff = MathTex(r"k_{eff}=\sum k_i=" + f"{parallel.k_eff:.1f}",
                        color=COLOR_SPRING, font_size=34)
        p_eff.next_to(parallel.mobject, DOWN, buff=0.3)
        self.play(FadeIn(parallel.mobject), FadeIn(p_label))
        self.play(FadeIn(p_eff))

        self.wait(0.4)
        self.finish_with_narration()
