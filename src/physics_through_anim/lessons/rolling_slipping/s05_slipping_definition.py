from manim import DOWN, LEFT, RIGHT, FadeIn, MathTex, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    RollingLessonScene,
    thin_block,
    velocity_arrow,
)


class SlippingDefinition(RollingLessonScene):
    """Scene 5 -- What Does "Slipping" Actually Mean?"""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "05", "What Does Slipping Actually Mean?", "Compare the two surfaces, not the object"
        )
        self.play(FadeIn(header))

        block = thin_block(x=-1.0)
        self.play(FadeIn(block))
        self.wait(0.5)

        contact_point = block.get_bottom()
        self.zoom_to(contact_point, width=3.2)

        point_a = MathTex("A", color="#39A8F0").next_to(contact_point, [0.3, 0.15, 0], buff=0.05)
        point_b = MathTex("B", color="#FF6B6B").next_to(contact_point, [0.3, -0.25, 0], buff=0.05)
        v_a = velocity_arrow(contact_point, contact_point + RIGHT * 0.6, "v_A")
        v_b_label = MathTex("v_B=0", font_size=28).next_to(contact_point, LEFT, buff=0.3)
        self.play(FadeIn(point_a), FadeIn(point_b), FadeIn(v_a), FadeIn(v_b_label))
        self.wait(1.5)

        self.zoom_out()
        equation = MathTex(
            r"v_{\rm rel} = v_A - v_B \neq 0 \ \Rightarrow\ \text{slipping}"
        ).to_edge(DOWN, buff=0.35)
        self.play(Write(equation))
        self.wait(2)
