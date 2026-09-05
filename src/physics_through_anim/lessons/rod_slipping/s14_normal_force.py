from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import COLOR_NORMAL, RodLessonScene


class Scene14NormalForce(RodLessonScene):
    """Scene 14 -- The normal force N(theta)."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("14", "The Normal Force N(theta)", "Vertical equation: N - mg = m a_Gy")
        self.play(FadeIn(header))

        newton = MathTex(r"N-mg=m\,a_{Gy}")
        self.play(Write(newton))
        self.wait(1)

        result = MathTex(
            r"\boxed{N(\theta)=\tfrac{mg}4(3\cos\theta-1)^2}", color=COLOR_NORMAL
        ).next_to(newton, DOWN, buff=0.5)
        self.play(Write(result))
        self.wait(2)
