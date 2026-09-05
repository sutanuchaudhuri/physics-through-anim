from manim import DOWN, RIGHT, FadeIn, MathTex, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    COLOR_APPLIED,
    RollingLessonScene,
    force_arrow,
    rough_ground,
    velocity_arrow,
    wheel_setup,
)


class TopPullForward(RollingLessonScene):
    """Scene 13 -- Can Friction Point Forward?"""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "13", "Can Friction Point Forward?", "Pull at the top instead of the center"
        )
        self.play(FadeIn(header))

        ground = rough_ground()
        disk = wheel_setup(radius=1.1)
        top_point = disk[0].get_top()
        applied = force_arrow(top_point, top_point + RIGHT * 1.3, "F", color=COLOR_APPLIED)
        self.play(FadeIn(ground), FadeIn(disk), FadeIn(applied))
        self.wait(1)

        self.zoom_to(disk[2].get_center(), width=2.6)
        slip_tendency = velocity_arrow(
            disk[2].get_center(), disk[2].get_center() + [-0.5, 0, 0], "v_{\\rm rel}"
        )
        self.play(FadeIn(slip_tendency))
        self.wait(1)
        self.zoom_out()

        friction = force_arrow(disk[2].get_center(), disk[2].get_center() + RIGHT * 1.0, "f")
        answer = MathTex(r"f \text{ points forward}").to_edge(DOWN, buff=0.35)
        self.play(FadeIn(friction), Write(answer))
        self.wait(2)
