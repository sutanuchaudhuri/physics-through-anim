from manim import DOWN, FadeIn, MathTex, VGroup, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene, quadrant_anchors


class Scene04WhyContactPoint(RodLessonScene):
    """Scene 4 -- Why calculate torque about the contact point?"""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "04", "Why Torque About the Contact Point?", "The shortcut removes two unknown forces"
        )
        self.play(FadeIn(header))

        anchors = quadrant_anchors()
        about_g = VGroup(
            MathTex("G", font_size=30, color="#FFD43B"),
            MathTex(r"I_G\alpha=\tau_N+\tau_f", font_size=26),
        ).arrange(DOWN, buff=0.25).move_to(anchors["top_left"])
        about_p = VGroup(
            MathTex("P", font_size=30, color="#FF6B6B"),
            MathTex(r"\tau_N=0,\ \tau_f=0", font_size=26),
        ).arrange(DOWN, buff=0.25).move_to(anchors["top_right"])
        self.play(FadeIn(about_g), FadeIn(about_p))
        self.wait(1)

        result = MathTex(
            r"\tfrac13mL^2\alpha=mg\tfrac L2\sin\theta \ \Rightarrow\ "
            r"\boxed{\alpha=\tfrac{3g}{2L}\sin\theta}"
        ).to_edge(DOWN, buff=0.4)
        self.play(Write(result))
        self.wait(2)
