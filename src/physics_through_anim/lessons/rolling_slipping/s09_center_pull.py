from manim import DOWN, RIGHT, FadeIn, FadeOut, MathTex, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    COLOR_APPLIED,
    RollingLessonScene,
    force_arrow,
    rough_ground,
    velocity_arrow,
    wheel_setup,
)


class CenterPull(RollingLessonScene):
    """Scene 9 -- Pull a Disk Through Its Center."""

    def construct(self) -> None:
        self.add_narration()
        banner = self.chapter_banner("III", "Where Friction Direction Really Comes From")
        self.play(FadeIn(banner))
        self.wait(1.2)
        self.play(FadeOut(banner))

        header = self.scene_header(
            "09", "Pull a Disk Through Its Center", "First imagine there is no friction"
        )
        self.play(FadeIn(header))

        ground = rough_ground()
        disk = wheel_setup(radius=1.1)
        applied = force_arrow(
            disk.wheel_center, disk.wheel_center + RIGHT * 1.3, "F", color=COLOR_APPLIED
        )
        self.play(FadeIn(ground), FadeIn(disk), FadeIn(applied))
        self.wait(1)

        self.zoom_to(disk[2].get_center(), width=2.6)
        slip_tendency = velocity_arrow(
            disk[2].get_center(), disk[2].get_center() + RIGHT * 0.5, "v_{\\rm rel}"
        )
        self.play(FadeIn(slip_tendency))
        self.wait(1.2)
        self.zoom_out()

        question = MathTex(r"\text{Which way must friction point?}").to_edge(DOWN, buff=0.7)
        self.play(Write(question))
        self.wait(1)
        friction = force_arrow(disk[2].get_center(), disk[2].get_center() + [-1.0, 0, 0], "f")
        answer = MathTex(r"f \text{ points backward}").next_to(question, DOWN, buff=0.2)
        self.play(FadeIn(friction), Write(answer))
        self.wait(2)
