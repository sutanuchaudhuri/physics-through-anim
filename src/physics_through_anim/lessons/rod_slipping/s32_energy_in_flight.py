from manim import FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene


class Scene32EnergyInFlight(RodLessonScene):
    """Scene 32 -- Energy conservation during free flight."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("32", "Energy in Free Flight", "Only gravity does work now")
        self.play(FadeIn(header))

        eq = MathTex(
            r"\tfrac12 m v_G^2+\tfrac12 I_G\omega^2+mgy_G=\text{const}"
        )
        self.play(Write(eq))
        self.wait(2)
