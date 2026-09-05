from manim import (
    BLUE,
    DOWN,
    ORANGE,
    PI,
    TEAL,
    YELLOW,
    Dot,
    FadeIn,
    Line,
    MathTex,
    Rotate,
    VGroup,
    Write,
    linear,
)

from physics_through_anim.lessons.rolling_slipping.common import (
    RollingLessonScene,
    quadrant_anchors,
)


class RotationalEnergy(RollingLessonScene):
    """Scene 18 -- Why I Also Appears in Rotational Energy.

    Four small orbiting-particle animations, one per quadrant, instead of a
    single column of four equations: each quadrant *shows* a particle moving
    faster at a larger radius, alongside the line of the derivation it justifies.
    """

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "18", "Moment of Inertia in Rotational Energy", "Faster particles contribute more"
        )
        self.play(FadeIn(header))

        anchors = quadrant_anchors(spread=3.2)
        radii = {"top_left": 0.35, "top_right": 0.55, "bottom_left": 0.75, "bottom_right": 0.95}
        colors = {
            "top_left": BLUE,
            "top_right": TEAL,
            "bottom_left": ORANGE,
            "bottom_right": YELLOW,
        }
        labels = {
            "top_left": r"v_i=\omega r_i",
            "top_right": r"K_i=\tfrac12 m_i v_i^2",
            "bottom_left": r"K_i=\tfrac12 m_i \omega^2 r_i^2",
            "bottom_right": r"K_{\rm rot}=\tfrac12\left(\sum_i m_i r_i^2\right)\omega^2",
        }
        for key, anchor in anchors.items():
            radius = radii[key]
            color = colors[key]
            pivot = Dot(anchor, radius=0.04, color="#888888")
            spoke = Line(anchor, anchor + [radius, 0, 0], color=color, stroke_width=3)
            particle = Dot(anchor + [radius, 0, 0], color=color, radius=0.08)
            orbit = VGroup(spoke, particle)
            label = MathTex(labels[key], font_size=28, color=color).next_to(
                anchor, DOWN, buff=radius + 0.35
            )
            self.play(FadeIn(pivot), FadeIn(orbit), Write(label))
            self.play(
                Rotate(orbit, angle=2 * PI, about_point=anchor), run_time=1.3, rate_func=linear
            )

        result = MathTex(r"\boxed{K_{\rm rot}=\tfrac12 I \omega^2}").to_edge(DOWN, buff=0.3)
        self.play(Write(result))
        self.wait(2)
