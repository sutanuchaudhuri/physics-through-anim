from manim import DOWN, FadeIn, FadeOut, MathTex, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    RollingLessonScene,
    rough_ground,
    wheel_setup,
)


class DiskAtRest(RollingLessonScene):
    """Scene 7 -- A Disk Resting on the Ground."""

    def construct(self) -> None:
        self.add_narration()
        banner = self.chapter_banner("II", "From Sliding to Rolling")
        self.play(FadeIn(banner))
        self.wait(1.2)
        self.play(FadeOut(banner))

        header = self.scene_header(
            "07", "A Disk Resting on the Ground", "Available friction is not used friction"
        )
        self.play(FadeIn(header))

        ground = rough_ground()
        disk = wheel_setup(radius=1.1)
        self.play(FadeIn(ground), FadeIn(disk))

        zero_force = MathTex("F=0")
        self.play(Write(zero_force.shift([0, 1.9, 0])))
        self.wait(1)

        friction_zero = MathTex("f_s=0").to_edge(DOWN, buff=0.35)
        self.play(Write(friction_zero))
        self.wait(2)
