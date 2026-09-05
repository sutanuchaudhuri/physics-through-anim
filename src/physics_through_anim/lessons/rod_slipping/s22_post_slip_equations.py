from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene


class Scene22PostSlipEquations(RodLessonScene):
    """Scene 22 -- Newton-Euler equations for the sliding phase."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "22", "New Equations for the Sliding Phase", "P is no longer fixed"
        )
        self.play(FadeIn(header))

        eq1 = MathTex(r"I_G\alpha=-\,s\,N\sin\theta+s\,f\cos\theta")
        eq2 = MathTex(r"N-mg=m\,a_{Gy},\qquad f=m\,a_{Gx}").next_to(eq1, DOWN, buff=0.4)
        self.play(Write(eq1))
        self.play(Write(eq2))
        self.wait(2)
