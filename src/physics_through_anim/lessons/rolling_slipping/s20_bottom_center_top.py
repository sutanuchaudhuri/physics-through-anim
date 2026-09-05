from manim import DOWN, RIGHT, FadeIn, FadeOut, MathTex, VGroup, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    RollingLessonScene,
    rolling_point_velocities,
    rough_ground,
    velocity_arrow,
    wheel_setup,
)


class BottomCenterTop(RollingLessonScene):
    """Scene 20 -- Bottom, Center and Top of a Rolling Wheel."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "20", "Bottom, Center and Top", "Rotation cancels below, reinforces above"
        )
        self.play(FadeIn(header))

        ground = rough_ground()
        disk = wheel_setup(radius=1.1)
        top_point = disk[0].get_top()
        v_center = velocity_arrow(disk.wheel_center, disk.wheel_center + RIGHT * 1.0, "v")
        v_top = velocity_arrow(top_point, top_point + RIGHT * 2.0, "2v")
        self.play(FadeIn(ground), FadeIn(disk))
        self.play(FadeIn(v_center), FadeIn(v_top))
        self.wait(1)

        bottom_label = MathTex(r"v_{\rm bottom}=0", font_size=28).next_to(disk[2], DOWN, buff=0.3)
        self.play(Write(bottom_label))

        summary = (
            VGroup(
                MathTex(r"v_{\rm center}=v"),
                MathTex(r"v_{\rm bottom}=0"),
                MathTex(r"v_{\rm top}=2v"),
            )
            .arrange(RIGHT, buff=0.8)
            .to_edge(DOWN, buff=0.4)
        )
        self.play(Write(summary))
        self.wait(2)
        self.play(FadeOut(v_center), FadeOut(v_top), FadeOut(bottom_label), FadeOut(summary))

        # Generalize: every rim point's velocity is perpendicular to the line
        # from it to the contact point (the instantaneous axis of rotation).
        field = rolling_point_velocities(disk, v_scale=1.4)
        axis_label = MathTex(r"\vec v_P \perp \overline{P\,\text{contact}}", font_size=30).to_edge(
            DOWN, buff=0.4
        )
        self.play(FadeIn(field))
        self.play(Write(axis_label))
        self.wait(2)
