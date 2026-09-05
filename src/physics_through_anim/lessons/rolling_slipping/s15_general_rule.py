from manim import RIGHT, FadeIn, FadeOut, MathTex, VGroup, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    RollingLessonScene,
    correction_card,
    misconception_card,
)


class GeneralRule(RollingLessonScene):
    """Scene 15 -- The General Rule for Friction Direction."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "15", "The General Rule", "Ask what the surfaces tend to do, not where the object goes"
        )
        self.play(FadeIn(header))

        wrong = misconception_card("Friction always opposes the object's motion.")
        self.play(FadeIn(wrong))
        self.wait(1)
        right = correction_card(
            "Friction opposes the relative slipping tendency at contact."
        ).move_to(wrong)
        self.play(FadeIn(right))
        self.wait(1)
        self.play(FadeOut(right))

        case_a = MathTex(r"v_{\rm rel}\!\rightarrow \ \Rightarrow\ f\!\leftarrow").scale(0.85)
        case_b = MathTex(r"v_{\rm rel}\!\leftarrow \ \Rightarrow\ f\!\rightarrow").scale(0.85)
        case_c = MathTex(r"v_{\rm rel}=0 \ \Rightarrow\ f=0").scale(0.85)
        cases = VGroup(case_a, case_b, case_c).arrange(RIGHT, buff=0.8)
        self.play(Write(cases))
        self.wait(2)
