from manim import DOWN, FadeIn, FadeOut, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene


class Scene20FrictionBecomesKinetic(RodLessonScene):
    """Scene 20 -- omega is continuous; alpha can jump."""

    def construct(self) -> None:
        self.add_narration()
        banner = self.chapter_banner("IV", "Sliding, Reversal, and Loss of Contact")
        self.play(FadeIn(banner))
        self.wait(1.2)
        self.play(FadeOut(banner))

        header = self.scene_header(
            "20", "Right After Slip Begins", r"$\omega$ does not jump; $\alpha$ can"
        )
        self.play(FadeIn(header))

        eq1 = MathTex(r"\omega(t_s^-)=\omega(t_s^+)")
        eq2 = MathTex(r"\alpha(t_s^-)\ne\alpha(t_s^+)", color="#C77DFF").next_to(eq1, DOWN, buff=0.4)
        self.play(Write(eq1))
        self.play(Write(eq2))
        self.wait(2)
