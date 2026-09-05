from manim import DOWN, LEFT, RIGHT, UP, FadeIn, MathTex, VGroup, Write

from physics_through_anim.lessons.rolling_slipping.common import RollingLessonScene


class FourSituations(RollingLessonScene):
    """Scene 26 -- Four Situations, One Theory."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "26", "Four Situations, One Theory", "Always ask what the contact is doing"
        )
        self.play(FadeIn(header))

        panel1 = (
            VGroup(
                MathTex(r"\text{Stationary block}", font_size=26),
                MathTex(r"f_s=F,\ f_s<\mu_s N", font_size=26),
            )
            .arrange(DOWN, buff=0.15)
            .move_to(LEFT * 3.4 + UP * 1.2)
        )
        panel2 = (
            VGroup(
                MathTex(r"\text{Sliding block}", font_size=26),
                MathTex(r"f_k=\mu_k N", font_size=26),
            )
            .arrange(DOWN, buff=0.15)
            .move_to(RIGHT * 3.4 + UP * 1.2)
        )
        panel3 = (
            VGroup(
                MathTex(r"\text{Rolling, no slip}", font_size=26),
                MathTex(r"v_{\rm CM}=\omega R,\ f\in\{0,\pm\}", font_size=24),
            )
            .arrange(DOWN, buff=0.15)
            .move_to(LEFT * 3.4 + DOWN * 1.0)
        )
        panel4 = (
            VGroup(
                MathTex(r"\text{Rolling while slipping}", font_size=26),
                MathTex(r"v_{\rm CM}\neq\omega R", font_size=26),
            )
            .arrange(DOWN, buff=0.15)
            .move_to(RIGHT * 3.4 + DOWN * 1.0)
        )
        self.play(FadeIn(panel1), FadeIn(panel2), FadeIn(panel3), FadeIn(panel4))
        self.wait(1.5)

        summary = MathTex(
            r"\text{Look at the contact. Can static friction prevent relative motion?}",
            font_size=26,
        ).to_edge(DOWN, buff=0.35)
        self.play(Write(summary))
        self.wait(2)
