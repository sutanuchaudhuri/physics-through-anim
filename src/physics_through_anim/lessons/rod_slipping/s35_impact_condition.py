from manim import FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import TABLE_HEIGHT, RodLessonScene


class Scene35ImpactCondition(RodLessonScene):
    """Scene 35 -- The exact impact condition."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "35", "The Impact Condition", "Whichever end reaches the floor first ends the flight"
        )
        self.play(FadeIn(header))

        eq = MathTex(
            rf"\min\big(y_A(t),\,y_B(t)\big)=-{TABLE_HEIGHT:.1f}"
        )
        self.play(Write(eq))
        self.wait(2)
