from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import COLOR_FRICTION, RodLessonScene


class Scene13RequiredFriction(RodLessonScene):
    """Scene 13 -- Required friction from Newton's second law."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("13", "The Friction Newton's Laws Demand", "Horizontal equation: f_s = m a_Gx")
        self.play(FadeIn(header))

        newton = MathTex(r"f_s=m\,a_{Gx}")
        self.play(Write(newton))
        self.wait(1)

        result = MathTex(
            r"\boxed{f_s(\theta)=\tfrac34 mg\sin\theta\,(3\cos\theta-2)}",
            color=COLOR_FRICTION,
        ).next_to(newton, DOWN, buff=0.5)
        self.play(Write(result))
        self.wait(2)
