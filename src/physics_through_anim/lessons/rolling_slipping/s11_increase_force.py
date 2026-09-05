from manim import BLUE, DOWN, GREEN, RIGHT, UP, FadeIn, Line, MathTex, VGroup, Write

from physics_through_anim.lessons.rolling_slipping.common import RollingLessonScene


class IncreaseForce(RollingLessonScene):
    """Scene 11 -- Increase the Force Slowly."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "11", "Increase the Force Slowly", "The disk keeps rolling until friction runs out"
        )
        self.play(FadeIn(header))

        axes_v = Line(DOWN * 1.6, UP * 1.6, color="#888888")
        axes_h = Line(DOWN * 1.6 + [-2.6, 0, 0], DOWN * 1.6 + [2.6, 0, 0], color="#888888")
        required_line = Line(
            DOWN * 1.6 + [-2.4, 0, 0], DOWN * 1.6 + [2.4, 1.6, 0], color=BLUE, stroke_width=5
        )
        limit_line = Line(
            DOWN * 1.6 + [-2.4, 1.0, 0], DOWN * 1.6 + [2.4, 1.0, 0], color=GREEN, stroke_width=5
        )
        required_label = MathTex(
            r"f_{\rm required}=\tfrac{F}{3}", color=BLUE, font_size=28
        ).next_to(required_line, RIGHT, buff=0.2)
        limit_label = MathTex(r"f_{s,\max}=\mu_s mg", color=GREEN, font_size=28).next_to(
            limit_line, RIGHT, buff=0.2
        )
        self.play(FadeIn(VGroup(axes_v, axes_h)))
        self.play(FadeIn(required_line), FadeIn(required_label))
        self.play(FadeIn(limit_line), FadeIn(limit_label))
        self.wait(1)

        threshold = MathTex(r"\boxed{F_{\rm critical}=3\mu_s mg}").to_edge(DOWN, buff=0.3)
        self.play(Write(threshold))
        self.wait(2)
