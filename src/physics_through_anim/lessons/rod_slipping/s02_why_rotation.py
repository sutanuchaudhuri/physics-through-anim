from manim import DOWN, RIGHT, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import (
    RodLessonScene,
    force_arrow,
    rod_at,
    table,
)


class Scene02WhyRotation(RodLessonScene):
    """Scene 2 -- Why gravity creates rotation."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("02", "Why Gravity Creates Rotation", "Gravity acquires a moment arm")
        self.play(FadeIn(header))

        floor = table(half_width=4.0)
        rod = rod_at(0.5)
        weight = force_arrow(rod.cm, rod.cm + [0, -1.0, 0], "mg", color="#9775FA")
        lever = MathTex(r"\tfrac L2\sin\theta", font_size=26).next_to(rod.foot, RIGHT, buff=1.0)
        self.play(FadeIn(floor), FadeIn(rod))
        self.play(FadeIn(weight), Write(lever))
        self.wait(1)

        equation = MathTex(r"\tau_P=mg\tfrac L2\sin\theta").to_edge(DOWN, buff=0.4)
        self.play(Write(equation))
        self.wait(2)
