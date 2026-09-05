from manim import DOWN, FadeIn

from physics_through_anim.lessons.rod_slipping.common import (
    RodLessonScene,
    correction_card,
    misconception_card,
)


class Scene42WhyNotEnergyOnly(RodLessonScene):
    """Scene 42 -- Why energy alone cannot finish the problem."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "42", "Why Not Energy Alone?", "Energy gives no direction information"
        )
        self.play(FadeIn(header))

        wrong = misconception_card("Energy conservation can tell us when the rod separates")
        right = correction_card("Energy gives speed, not the force balance N>=0 that separation needs")
        wrong.to_edge(DOWN, buff=1.6)
        right.next_to(wrong, DOWN, buff=0.25)
        self.play(FadeIn(wrong))
        self.play(FadeIn(right))
        self.wait(2)
