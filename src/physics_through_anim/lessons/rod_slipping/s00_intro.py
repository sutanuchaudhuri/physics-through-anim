from manim import DOWN, FadeIn, FadeOut, MathTex, Text, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene


class Scene00Intro(RodLessonScene):
    """Scene 0 -- The Physical Story."""

    def construct(self) -> None:
        self.add_narration()
        title = Text("FALLING ROD AT A TABLE EDGE", font_size=34, weight="BOLD")
        subtitle = Text(
            "We do NOT use one equation for the entire motion.", font_size=22, color="#FF6B6B"
        ).next_to(title, DOWN, buff=0.3)
        self.play(Write(title), FadeIn(subtitle))
        self.log_mobject("title_written", title)  # manual transcript entry, see scene_logging.py
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(subtitle))

        header = self.scene_header("00", "The Physical Story", "Every constraint change needs new equations")
        self.play(FadeIn(header))

        chain = MathTex(
            r"\text{static contact} \to \text{slipping} \to \text{edge} \to "
            r"\text{separation} \to \text{free flight} \to \text{impact}",
            font_size=26,
        )
        self.play(Write(chain))
        self.wait(2)
