from manim import DOWN, LEFT, FadeIn, MathTex, Text, VGroup, Write

from physics_through_anim.lessons.rolling_slipping.common import RollingLessonScene


class CompleteSolver(RollingLessonScene):
    """Scene 25 -- The Complete Solver."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "25", "The Complete Solver", "One method for every rolling problem"
        )
        self.play(FadeIn(header))

        steps = (
            VGroup(
                Text("1. Draw the free-body diagram.", font_size=24),
                MathTex(r"\text{2. } \sum F_x=ma"),
                MathTex(r"\text{3. } \sum \tau_{\rm CM}=I\alpha"),
                MathTex(r"\text{4. Assume no slip: } a=\alpha R"),
                Text("5. Solve for the required f_s.", font_size=24),
                MathTex(r"\text{6. Check } |f_s|\leq\mu_s N"),
            )
            .arrange(DOWN, buff=0.22, aligned_edge=LEFT)
            .scale(0.85)
            .shift([0, 0.3, 0])
        )
        self.play(Write(steps))
        self.wait(1.5)

        branch = MathTex(
            r"\text{Yes: rolling without slipping.}\quad"
            r"\text{No: find the slip direction, use } f_k=\mu_k N.",
            font_size=26,
        ).to_edge(DOWN, buff=0.35)
        self.play(Write(branch))
        self.wait(2)
