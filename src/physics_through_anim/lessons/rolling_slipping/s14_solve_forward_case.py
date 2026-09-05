from manim import DOWN, RIGHT, UP, FadeIn, MathTex, VGroup, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    COLOR_APPLIED,
    COLOR_FRICTION,
    RollingLessonScene,
    force_arrow,
    rough_ground,
    wheel_setup,
)


class SolveForwardCase(RollingLessonScene):
    """Scene 14 -- Solve the Forward-Friction Case."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "14", "Solving the Forward-Friction Case", "Same wheel, opposite friction"
        )
        self.play(FadeIn(header))

        ground = rough_ground(half_width=2.4)
        disk = wheel_setup(radius=0.75, x=-3.3)
        top_point = disk[0].get_top()
        applied = force_arrow(top_point, top_point + RIGHT * 0.9, "F", color=COLOR_APPLIED)
        friction = force_arrow(
            disk[2].get_center(), disk[2].get_center() + RIGHT * 0.7, "f", color=COLOR_FRICTION
        )
        self.play(FadeIn(ground), FadeIn(disk), FadeIn(applied), FadeIn(friction))

        translation = MathTex(r"F+f=ma", font_size=32)
        rotation = MathTex(r"(F-f)R=I\alpha", font_size=32)
        constraint = MathTex(r"a=\alpha R", font_size=32)
        equations = (
            VGroup(translation, rotation, constraint)
            .arrange(DOWN, buff=0.3)
            .move_to(RIGHT * 2.2 + UP * 1.0)
        )
        self.play(Write(equations))
        self.wait(1)

        result = MathTex(r"\boxed{f=\tfrac{F}{3}} \quad \boxed{a=\tfrac{4F}{3m}}").shift(
            [0, -1.0, 0]
        )
        self.play(Write(result))
        self.wait(1)

        moral = MathTex(
            r"\text{Center of mass, force, and friction all point right.}", font_size=30
        ).shift([0, -2.3, 0])
        self.play(Write(moral))
        self.wait(2)
