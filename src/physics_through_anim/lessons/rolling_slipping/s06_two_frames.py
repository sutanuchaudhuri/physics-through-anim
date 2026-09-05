from manim import DOWN, LEFT, RIGHT, FadeIn, MathTex, VGroup, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    RollingLessonScene,
    reference_frame_icon,
    thin_block,
    velocity_arrow,
)


class TwoFrames(RollingLessonScene):
    """Scene 6 -- The Same Slip Seen From Two Frames."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "06", "The Same Slip, Two Frames", "Relative velocity does not depend on the observer"
        )
        self.play(FadeIn(header))

        left_title = MathTex("S", font_size=32).shift(LEFT * 3.5 + [0, 1.6, 0])
        right_title = MathTex("S'", font_size=32).shift(RIGHT * 3.5 + [0, 1.6, 0])
        left_icon = reference_frame_icon(scale=0.4).next_to(left_title, DOWN, buff=0.15)
        right_icon = reference_frame_icon(scale=0.4).next_to(right_title, DOWN, buff=0.15)
        left_block = thin_block(x=-3.5, y=0.0)
        right_block = thin_block(x=3.5, y=0.0)
        left_v = velocity_arrow(left_block.get_right(), left_block.get_right() + RIGHT * 1.0, "v")
        right_v = velocity_arrow(
            right_block.get_left() + [0, -0.6, 0],
            right_block.get_left() + [0, -0.6, 0] + LEFT * 1.0,
            "v",
        )
        self.play(
            FadeIn(left_title),
            FadeIn(right_title),
            FadeIn(left_icon),
            FadeIn(right_icon),
            FadeIn(left_block),
            FadeIn(right_block),
            FadeIn(left_v),
            FadeIn(right_v),
        )

        equation = MathTex(r"|v_{\rm rel}| = v \ \text{in both frames}")
        boxed = MathTex(r"\boxed{\text{Slip is determined by relative velocity.}}")
        VGroup(equation, boxed).arrange(DOWN, buff=0.2).to_edge(DOWN, buff=0.3)
        self.play(Write(equation))
        self.play(Write(boxed))
        self.wait(2)
