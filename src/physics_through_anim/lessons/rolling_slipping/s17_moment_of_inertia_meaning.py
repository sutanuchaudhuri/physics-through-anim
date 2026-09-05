from manim import BLUE, DOWN, ORANGE, Dot, FadeIn, MathTex, VGroup, Write

from physics_through_anim.lessons.rolling_slipping.common import RollingLessonScene


class MomentOfInertiaMeaning(RollingLessonScene):
    """Scene 17 -- What Moment of Inertia Actually Means."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "17", "What Moment of Inertia Means", "Same mass, different distribution"
        )
        self.play(FadeIn(header))

        left_center = [-3.2, 0.6, 0]
        right_center = [3.2, 0.6, 0]
        clustered = VGroup(
            *[
                Dot([left_center[0] + dx, left_center[1] + dy, 0], color=BLUE, radius=0.08)
                for dx, dy in [(-0.15, 0), (0.15, 0), (0, 0.15), (0, -0.15)]
            ]
        )
        spread = VGroup(
            *[
                Dot([right_center[0] + dx, right_center[1] + dy, 0], color=ORANGE, radius=0.08)
                for dx, dy in [(-1.0, 0), (1.0, 0), (0, 1.0), (0, -1.0)]
            ]
        )
        left_label = MathTex(r"I_{\rm small}", color=BLUE).next_to(clustered, DOWN, buff=0.6)
        right_label = MathTex(r"I_{\rm large}", color=ORANGE).next_to(spread, DOWN, buff=0.6)
        self.play(FadeIn(clustered), FadeIn(spread))
        self.play(Write(left_label), Write(right_label))

        equation = MathTex(r"I=\sum_i m_i r_i^2").to_edge(DOWN, buff=0.4)
        self.play(Write(equation))
        self.wait(2)
