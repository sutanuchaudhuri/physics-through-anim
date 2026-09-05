from manim import DOWN, RIGHT, FadeIn, FadeOut, MathTex, ReplacementTransform, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    COLOR_APPLIED,
    RollingLessonScene,
    force_arrow,
    rough_ground,
    thin_block,
)


class BlockStatic(RollingLessonScene):
    """Scene 1 -- A Block That Refuses to Move."""

    def construct(self) -> None:
        self.add_narration()
        banner = self.chapter_banner("I", "What Friction Really Does")
        self.play(FadeIn(banner))
        self.wait(1.2)
        self.play(FadeOut(banner))

        header = self.scene_header(
            "01", "A Block That Refuses to Move", "Static friction matches the push"
        )
        self.play(FadeIn(header))

        ground = rough_ground()
        block = thin_block(x=-1.0)
        self.play(FadeIn(ground), FadeIn(block))

        applied = force_arrow(
            block.get_right(),
            block.get_right() + RIGHT * 1.0,
            "F=1\\,{\\rm N}",
            color=COLOR_APPLIED,
        )
        friction = force_arrow(
            block.get_left(), block.get_left() + [-1.0, 0, 0], "f_s=1\\,{\\rm N}"
        )
        self.play(FadeIn(applied), FadeIn(friction))
        self.wait(1)

        applied2 = force_arrow(
            block.get_right(),
            block.get_right() + RIGHT * 1.6,
            "F=2\\,{\\rm N}",
            color=COLOR_APPLIED,
        )
        friction2 = force_arrow(
            block.get_left(), block.get_left() + [-1.6, 0, 0], "f_s=2\\,{\\rm N}"
        )
        self.play(
            ReplacementTransform(applied, applied2), ReplacementTransform(friction, friction2)
        )

        equation = MathTex(r"\sum F_x = F - f_s = 0 \ \Rightarrow\ a=0").to_edge(DOWN, buff=0.35)
        self.play(Write(equation))
        self.wait(2)
