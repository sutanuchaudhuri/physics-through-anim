from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene


class Scene16SlipAngleEquation(RodLessonScene):
    """Scene 16 -- Solving for the slip angle."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("16", "Solving for the Slip Angle", "Setting the ratio equal to mu_s")
        self.play(FadeIn(header))

        eq = MathTex(
            r"\mu_s=\dfrac{f_s(\theta_s)}{N(\theta_s)}"
            r"=\dfrac{3\sin\theta_s(3\cos\theta_s-2)}{(3\cos\theta_s-1)^2}"
        )
        self.play(Write(eq))
        self.wait(1)

        note = MathTex(
            r"\text{Transcendental in }\theta_s\ \Rightarrow\ \text{solved numerically}",
            font_size=24,
            color="#868E96",
        ).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note))
        self.wait(2)
