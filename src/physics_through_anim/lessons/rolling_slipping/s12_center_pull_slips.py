from manim import DOWN, LEFT, RIGHT, Cross, FadeIn, MathTex, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    COLOR_APPLIED,
    RollingLessonScene,
    force_arrow,
    rough_ground,
    velocity_arrow,
    wheel_setup,
)


class CenterPullSlips(RollingLessonScene):
    """Scene 12 -- The Center-Pulled Disk Begins to Slip."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("12", "The Disk Begins to Slip", "Translation outruns rotation")
        self.play(FadeIn(header))

        ground = rough_ground()
        disk = wheel_setup(radius=1.1)
        applied = force_arrow(
            disk.wheel_center, disk.wheel_center + RIGHT * 2.2, "F>3\\mu_s mg", color=COLOR_APPLIED
        )
        self.play(FadeIn(ground), FadeIn(disk), FadeIn(applied))

        self.zoom_to(disk[2].get_center(), width=2.6)
        slide = velocity_arrow(
            disk[2].get_center(), disk[2].get_center() + RIGHT * 0.6, "v_{\\rm rel}"
        )
        friction = force_arrow(disk[2].get_center(), disk[2].get_center() + [-0.6, 0, 0], "f_k")
        self.play(FadeIn(slide), FadeIn(friction))
        self.wait(1.2)
        self.zoom_out()

        kinetic = MathTex(r"f_k=\mu_k mg")
        translation = MathTex(r"ma=F-f_k")
        rotation = MathTex(r"I\alpha=f_k R")
        broken = MathTex(r"a=\alpha R").set_color("#FF6B6B")
        cross = Cross(broken, stroke_color="#FF6B6B")
        kinetic.to_edge(DOWN, buff=1.3)
        translation.next_to(kinetic, LEFT * 3, buff=0.6)
        rotation.next_to(kinetic, RIGHT * 3, buff=0.6)
        broken.next_to(kinetic, DOWN, buff=0.35)
        cross.move_to(broken)
        self.play(Write(kinetic))
        self.play(Write(translation), Write(rotation))
        self.play(Write(broken))
        self.play(FadeIn(cross))
        self.wait(2)
