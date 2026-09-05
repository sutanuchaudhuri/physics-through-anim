from manim import DOWN, LEFT, RIGHT, FadeIn, FadeOut, MathTex, VGroup, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    COLOR_APPLIED,
    RollingLessonScene,
    force_arrow,
    rough_ground,
    wheel_setup,
)


class FinalChallenge(RollingLessonScene):
    """Scene 27 -- Final Concept Challenge."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "27", "Final Concept Challenge", "Predict the friction before solving anything"
        )
        self.play(FadeIn(header))

        ground = rough_ground()
        disk_a = wheel_setup(radius=0.9, x=-3.2)
        disk_b = wheel_setup(radius=0.9, x=3.2)
        applied_a = force_arrow(
            disk_a.wheel_center, disk_a.wheel_center + RIGHT * 1.0, "F", color=COLOR_APPLIED
        )
        applied_b = force_arrow(
            disk_b[0].get_top(), disk_b[0].get_top() + RIGHT * 1.0, "F", color=COLOR_APPLIED
        )
        self.play(
            FadeIn(ground), FadeIn(disk_a), FadeIn(disk_b), FadeIn(applied_a), FadeIn(applied_b)
        )

        prompt = MathTex(r"\text{Predict the direction of friction for each wheel.}").to_edge(
            DOWN, buff=0.7
        )
        self.play(Write(prompt))
        self.wait(2)

        friction_a = force_arrow(disk_a[2].get_center(), disk_a[2].get_center() + LEFT * 0.9, "f")
        friction_b = force_arrow(disk_b[2].get_center(), disk_b[2].get_center() + RIGHT * 0.9, "f")
        self.play(FadeIn(friction_a), FadeIn(friction_b))
        self.wait(1)

        self.play(FadeOut(prompt))
        conclusion = (
            VGroup(
                MathTex(r"\boxed{\text{Friction responds to relative slipping.}}"),
                MathTex(r"\boxed{\text{Rolling occurs when translation and rotation cooperate.}}"),
            )
            .arrange(DOWN, buff=0.25)
            .to_edge(DOWN, buff=0.4)
        )
        self.play(Write(conclusion))
        self.wait(2)
