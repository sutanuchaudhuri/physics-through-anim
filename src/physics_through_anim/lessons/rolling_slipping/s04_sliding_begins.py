from manim import DOWN, RIGHT, FadeIn, MathTex, ReplacementTransform, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    COLOR_APPLIED,
    RollingLessonScene,
    force_arrow,
    rough_ground,
    thin_block,
)


class SlidingBegins(RollingLessonScene):
    """Scene 4 -- Sliding Begins."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "04", "Sliding Begins", "Static friction hands off to kinetic friction"
        )
        self.play(FadeIn(header))

        ground = rough_ground()
        block = thin_block(x=-1.0)
        applied = force_arrow(
            block.get_right(), block.get_right() + RIGHT * 2.0, "F", color=COLOR_APPLIED
        )
        friction_static = force_arrow(block.get_left(), block.get_left() + [-1.6, 0, 0], "f_s")
        self.play(FadeIn(ground), FadeIn(block), FadeIn(applied), FadeIn(friction_static))
        self.wait(1)

        friction_kinetic = force_arrow(
            block.get_left(), block.get_left() + [-1.1, 0, 0], "f_k=\\mu_k N"
        )
        self.play(ReplacementTransform(friction_static, friction_kinetic))

        equation = MathTex(r"ma = F - \mu_k N").to_edge(DOWN, buff=0.35)
        self.play(Write(equation))
        self.wait(2)
