import numpy as np
from manim import DOWN, RIGHT, UP, DashedLine, FadeIn, FadeOut, MathTex, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    RollingLessonScene,
    reference_frame_icon,
    rough_ground,
    velocity_arrow,
    wheel_setup,
)


class VelocityOfPoint(RollingLessonScene):
    """Scene 19 -- Velocity of Any Point on the Wheel."""

    def construct(self) -> None:
        self.add_narration()
        banner = self.chapter_banner("V", "Translation Plus Rotation")
        self.play(FadeIn(banner))
        self.wait(1.2)
        self.play(FadeOut(banner))

        header = self.scene_header(
            "19", "Velocity of Any Point", "Translation plus rotation, added as vectors"
        )
        self.play(FadeIn(header))

        # Every kinematic vector is measured relative to an observer -- state it.
        frame_icon = reference_frame_icon(scale=0.35).to_corner(UP + RIGHT, buff=0.35)
        frame_label = MathTex(r"S\ (\text{ground frame})", font_size=24).next_to(
            frame_icon, DOWN, buff=0.1
        )
        self.play(FadeIn(frame_icon), Write(frame_label))

        ground = rough_ground()
        disk = wheel_setup(radius=1.1)
        point_p = disk[0].point_from_proportion(0.15)

        # omega x r is tangential: perpendicular to the radius line to P, not a fixed direction.
        r_vec = point_p - disk.wheel_center
        tangent_dir = np.array([r_vec[1], -r_vec[0], 0.0])
        tangent_dir = tangent_dir / np.linalg.norm(tangent_dir) * 0.9
        radius_line = DashedLine(disk.wheel_center, point_p, color="#888888", stroke_width=2)

        v_cm = velocity_arrow(disk.wheel_center, disk.wheel_center + RIGHT * 1.0, "v_{\\rm CM}")
        v_rot = velocity_arrow(point_p, point_p + tangent_dir, "\\vec\\omega\\times\\vec r")
        self.play(FadeIn(ground), FadeIn(disk))
        self.play(FadeIn(radius_line), FadeIn(v_cm), FadeIn(v_rot))
        self.wait(1)

        equation = MathTex(
            r"\boxed{\vec v_P = \vec v_{\rm CM} + \vec\omega\times\vec r_{P/\rm CM}}"
        ).to_edge(DOWN, buff=0.4)
        self.play(Write(equation))
        self.wait(2)
