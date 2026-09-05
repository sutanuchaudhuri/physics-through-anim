from manim import FadeIn, MathTex, Table

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene


class Scene41FourToolComparison(RodLessonScene):
    """Scene 41 -- Comparing the four analysis tools used."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "41", "Four Tools, One Rod", "Torque, energy, kinematics, and Newton-Euler each had a job"
        )
        self.play(FadeIn(header))

        table = Table(
            [
                ["Fixed pivot", "before slip", r"$\alpha=\tfrac{3g}{2L}\sin\theta$"],
                ["Energy", "before slip", r"$\omega(\theta)$ without solving an ODE"],
                ["Kinematics", "before slip", r"$t(\theta)$ from $\omega(\theta)$"],
                ["Newton-Euler", "after slip", r"full $(N,f,\alpha)$ once P is not fixed"],
            ],
            col_labels=[MathTex("\\text{Tool}"), MathTex("\\text{Regime}"), MathTex("\\text{Gives}")],
            include_outer_lines=True,
        ).scale(0.42)
        self.play(FadeIn(table))
        self.wait(2)
