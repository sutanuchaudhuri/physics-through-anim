from manim import DOWN, RIGHT, UP, FadeIn, MathTex, VGroup, Write

from physics_through_anim.lessons.rod_slipping.common import (
    RodLessonScene,
    rod_at,
    table,
    trajectory,
)


class Scene01AlmostVertical(RodLessonScene):
    """Scene 1 -- The rod is almost vertical."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("01", "The Rod Is Almost Vertical", "A tiny initial tilt breaks the symmetry")
        self.play(FadeIn(header))

        traj = trajectory()
        floor = table(half_width=4.0)
        rod = rod_at(traj.theta[0])
        p_label = MathTex("P", font_size=28).next_to(rod.foot, DOWN, buff=0.15)
        g_label = MathTex("G", font_size=28, color="#FFD43B").next_to(rod.cm, RIGHT, buff=0.15)
        theta_label = MathTex(r"\theta_0\simeq2^\circ", font_size=26).next_to(rod.cm, UP, buff=0.3)
        self.play(FadeIn(floor), FadeIn(rod), Write(p_label), Write(g_label), Write(theta_label))
        self.wait(1)

        formulas = VGroup(
            MathTex(r"I_G=\tfrac1{12}mL^2", font_size=30),
            MathTex(r"I_P=\tfrac13mL^2", font_size=30),
        ).arrange(DOWN, buff=0.2).to_edge(DOWN, buff=0.4)
        self.play(Write(formulas))
        self.wait(2)
