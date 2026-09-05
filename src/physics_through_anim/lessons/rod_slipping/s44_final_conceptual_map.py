from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene


class Scene44FinalConceptualMap(RodLessonScene):
    """Scene 44 -- Final conceptual map and closing narration."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "44", "The Conceptual Map", "Every phase change means a fresh free-body diagram"
        )
        self.play(FadeIn(header))

        chain = MathTex(
            r"\text{static}\xrightarrow{f_s=\mu_s N}\text{sliding}\xrightarrow{\text{edge}}"
            r"\text{separation}\xrightarrow{N=0}\text{free flight}\xrightarrow{\min(y_A,y_B)=-h}\text{impact}",
            font_size=24,
        )
        self.play(Write(chain))
        self.wait(1.5)

        closing = MathTex(
            r"\text{No single equation governs a falling rod --- the physics itself changes phase by phase.}",
            font_size=22,
            color="#868E96",
        ).next_to(chain, DOWN, buff=0.6)
        self.play(FadeIn(closing))
        self.wait(2.5)
