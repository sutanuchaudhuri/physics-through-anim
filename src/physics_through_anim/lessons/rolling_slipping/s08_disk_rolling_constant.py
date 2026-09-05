from manim import DOWN, ORANGE, Dot, FadeIn, MathTex, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    RollingLessonScene,
    animate_rolling,
    rough_ground,
    wheel_setup,
)


class DiskRollingConstant(RollingLessonScene):
    """Scene 8 -- A Disk Already Rolling at Constant Speed."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "08", "Rolling at Constant Speed", "No friction is needed to keep it going"
        )
        self.play(FadeIn(header))

        ground = rough_ground()
        disk = wheel_setup(radius=1.0, x=-3.0)
        marker = Dot(disk[0].point_from_proportion(0.0), color=ORANGE, radius=0.06)
        disk.add(marker)
        self.play(FadeIn(ground), FadeIn(disk))

        # Real rolling: translate and spin together (v = omega * R), not a bare slide.
        animate_rolling(self, disk, radius=1.0, distance=6.0, run_time=3)
        self.wait(0.5)

        zero_friction = MathTex("f=0").to_edge(DOWN, buff=0.35)
        self.play(Write(zero_friction))
        self.wait(2)
