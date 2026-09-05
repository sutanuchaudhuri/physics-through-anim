from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    RollingLessonScene,
    rolling_constraint_bridge,
)


class RollingConstraintCouples(RollingLessonScene):
    """Scene 24 -- The Rolling Constraint Couples Them."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "24", "The Rolling Constraint", "One equation bridges translation and rotation"
        )
        self.play(FadeIn(header))

        bridge = rolling_constraint_bridge().shift([0, 0.4, 0])
        self.play(FadeIn(bridge))
        self.wait(1)

        note = MathTex(r"\text{If slipping occurs, this equation must be removed.}").to_edge(
            DOWN, buff=0.4
        )
        self.play(Write(note))
        self.wait(2)
