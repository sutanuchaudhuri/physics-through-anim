from manim import DOWN, FadeIn

from physics_through_anim.lessons.rod_slipping.common import (
    RodLessonScene,
    correction_card,
    misconception_card,
)


class Scene43WhyNotTorqueOnly(RodLessonScene):
    """Scene 43 -- Why the fixed-pivot torque trick cannot run forever."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "43", "Why Not Torque About P Forever?", r"$\sum\tau_P=I_P\alpha$ needs P fixed in an inertial frame"
        )
        self.play(FadeIn(header))

        wrong = misconception_card("Once we found alpha(theta) about P, that formula holds for the whole fall")
        right = correction_card("The formula is only valid while the foot does not slide")
        wrong.to_edge(DOWN, buff=1.6)
        right.next_to(wrong, DOWN, buff=0.25)
        self.play(FadeIn(wrong))
        self.play(FadeIn(right))
        self.wait(2)
