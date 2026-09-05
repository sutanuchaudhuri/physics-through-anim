from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import (
    RodLessonScene,
    correction_card,
    misconception_card,
)


class Scene17FrictionReversal(RodLessonScene):
    """Scene 17 -- The friction reversal point cos(theta)=2/3."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "17", "A Hidden Reversal", r"$f_s$ changes sign at $\cos\theta=2/3\approx48.19^\circ$"
        )
        self.play(FadeIn(header))

        eq = MathTex(r"3\cos\theta-2=0 \ \Rightarrow\ \theta\approx48.19^\circ")
        self.play(Write(eq))
        self.wait(1)

        wrong = misconception_card("Friction always points the same way while sliding")
        right = correction_card("Its direction depends on the sign of the required horizontal force")
        wrong.next_to(eq, DOWN, buff=0.6)
        right.next_to(wrong, DOWN, buff=0.25)
        self.play(FadeIn(wrong))
        self.play(FadeIn(right))
        self.wait(2)
