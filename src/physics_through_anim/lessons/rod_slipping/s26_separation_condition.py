from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import COLOR_NORMAL, RodLessonScene


class Scene26SeparationCondition(RodLessonScene):
    """Scene 26 -- The theoretical separation criterion N=0."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "26", "When Does the Rod Leave the Surface?", r"General criterion: $N\ge0$"
        )
        self.play(FadeIn(header))

        eq = MathTex(r"N(\theta)=0 \ \Rightarrow\ \text{lift-off}", color=COLOR_NORMAL)
        self.play(Write(eq))
        self.wait(1)

        note = MathTex(
            r"\text{For }\mu_s=0.30,\ N(\theta)\text{ never reaches }0\text{ before the edge}",
            font_size=24,
            color="#868E96",
        ).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note))
        self.wait(2)
