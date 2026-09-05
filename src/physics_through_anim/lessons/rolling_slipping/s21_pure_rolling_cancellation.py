from manim import RIGHT, FadeIn, FadeOut, MathTex, ReplacementTransform, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    RollingLessonScene,
    rough_ground,
    velocity_arrow,
    wheel_setup,
)


class PureRollingCancellation(RollingLessonScene):
    """Scene 21 -- Pure Rolling Is a Cancellation Condition."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "21", "Pure Rolling Is a Cancellation", "Translation and rotation meet at the contact"
        )
        self.play(FadeIn(header))

        ground = rough_ground()
        disk = wheel_setup(radius=1.1)
        self.play(FadeIn(ground), FadeIn(disk))

        equation = MathTex(r"v_{\rm contact}=v_{\rm CM}-\omega R").shift([0, -1.8, 0])
        self.play(Write(equation))

        forward_slip = velocity_arrow(
            disk[2].get_center(), disk[2].get_center() + RIGHT * 0.6, "v_{\\rm CM}>\\omega R"
        )
        self.play(FadeIn(forward_slip))
        self.wait(1)

        backward_slip = velocity_arrow(
            disk[2].get_center(), disk[2].get_center() + [-0.6, 0, 0], "v_{\\rm CM}<\\omega R"
        )
        self.play(ReplacementTransform(forward_slip, backward_slip))
        self.wait(1)

        boxed = MathTex(r"\boxed{v_{\rm CM}=\omega R}").shift([0, -3.1, 0])
        self.play(FadeOut(backward_slip))
        self.play(Write(boxed))
        self.wait(2)
