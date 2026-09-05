from manim import DOWN, RIGHT, FadeIn, MathTex, VGroup, Write

from physics_through_anim.lessons.rod_slipping.common import (
    COLOR_FRICTION,
    COLOR_NORMAL,
    RodLessonScene,
    force_arrow,
    rod_at,
)


class Scene03FirstFBD(RodLessonScene):
    """Scene 3 -- First FBD."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("03", "First Free-Body Diagram", "Which point should we take torque about?")
        self.play(FadeIn(header))

        rod = rod_at(0.5)
        weight = force_arrow(rod.cm, rod.cm + [0, -1.0, 0], "mg", color="#9775FA")
        normal = force_arrow(rod.foot, rod.foot + [0, 0.9, 0], "N", color=COLOR_NORMAL)
        friction = force_arrow(rod.foot, rod.foot + [-0.8, 0, 0], "f_s", color=COLOR_FRICTION)
        self.play(FadeIn(rod), FadeIn(weight), FadeIn(normal), FadeIn(friction))
        self.wait(1)

        question = MathTex(r"\text{Torque about } P \quad\text{or}\quad G\, ?").to_edge(DOWN, buff=0.5)
        candidates = VGroup(MathTex("P", font_size=36), MathTex("G", font_size=36)).arrange(
            RIGHT, buff=2.0
        ).next_to(question, DOWN, buff=0.2)
        self.play(Write(question), Write(candidates))
        self.wait(2)
