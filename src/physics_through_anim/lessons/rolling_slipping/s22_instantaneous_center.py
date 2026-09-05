from manim import RIGHT, FadeIn, MathTex, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    RollingLessonScene,
    correction_card,
    misconception_card,
    rough_ground,
    wheel_setup,
)


class InstantaneousCenter(RollingLessonScene):
    """Scene 22 -- The Instantaneous Center of Rotation."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "22", "The Instantaneous Center of Rotation", "Zero velocity is not a permanent hinge"
        )
        self.play(FadeIn(header))

        ground = rough_ground()
        disk = wheel_setup(radius=1.1)
        label = MathTex("P", font_size=30).next_to(disk[2], RIGHT, buff=0.15)
        self.play(FadeIn(ground), FadeIn(disk), Write(label))
        self.wait(1)

        wrong = misconception_card("Zero velocity at the bottom means zero acceleration too.")
        wrong.shift([0, -3.0, 0])
        self.play(FadeIn(wrong))
        self.wait(1)
        right = correction_card(
            "Instantaneous zero velocity does not imply zero acceleration."
        ).move_to(wrong)
        self.play(FadeIn(right))
        self.wait(1)

        wrong2 = misconception_card("The contact point is a permanent pivot.")
        wrong2.move_to(right)
        self.play(FadeIn(wrong2))
        self.wait(1)
        right2 = correction_card(
            "It is instantaneous only -- a new material point touches down next."
        ).move_to(wrong2)
        self.play(FadeIn(right2))
        self.wait(2)
