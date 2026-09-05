from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene, trajectory


class Scene27SeparationInThisExample(RodLessonScene):
    """Scene 27 -- Why the table's finite width ends contact here."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "27", "This Table Has an Edge", "Contact ends when the foot runs out of table, not when N=0"
        )
        self.play(FadeIn(header))

        import numpy as np

        traj = trajectory()
        eq = MathTex(rf"\theta_{{\text{{edge}}}}={np.degrees(traj.theta_sep):.0f}^\circ")
        self.play(Write(eq))
        self.wait(1)

        note = MathTex(
            r"N\ge0 \text{ is still the general theoretical rule for lift-off}",
            font_size=24,
            color="#868E96",
        ).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note))
        self.wait(2)
