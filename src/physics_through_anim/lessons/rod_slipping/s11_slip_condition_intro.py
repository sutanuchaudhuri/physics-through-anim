from manim import DOWN, FadeIn, FadeOut, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene


class Scene11SlipConditionIntro(RodLessonScene):
    """Scene 11 -- Introducing the slip condition."""

    def construct(self) -> None:
        self.add_narration()
        banner = self.chapter_banner("III", "Finding the Slip Condition")
        self.play(FadeIn(banner))
        self.wait(1.2)
        self.play(FadeOut(banner))

        header = self.scene_header(
            "11", "When Does the Foot Slip?", "Static friction has a maximum it can supply"
        )
        self.play(FadeIn(header))

        condition = MathTex(r"|f_s|\le\mu_s N")
        self.play(Write(condition))
        self.wait(1)

        question = MathTex(
            r"\text{We need } f_s(\theta) \text{ and } N(\theta) \text{ from the CM's real acceleration.}",
            font_size=24,
        ).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(question))
        self.wait(2)
