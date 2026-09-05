from manim import DOWN, FadeIn

from physics_through_anim.lessons.rod_slipping.common import (
    RodLessonScene,
    correction_card,
    misconception_card,
)


class Scene37The180Subtlety(RodLessonScene):
    """Scene 37 -- The 180-degree repeat-appearance subtlety."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "37", "A Subtle Trap", r"A rod rotated $180^\circ$ looks identical -- unless one end is marked"
        )
        self.play(FadeIn(header))

        wrong = misconception_card("Any orientation matching the original silhouette must be the same state")
        right = correction_card("Track a marked end (A) explicitly; theta must be unwrapped, not modulo pi")
        wrong.to_edge(DOWN, buff=1.6)
        right.next_to(wrong, DOWN, buff=0.25)
        self.play(FadeIn(wrong))
        self.play(FadeIn(right))
        self.wait(2)
