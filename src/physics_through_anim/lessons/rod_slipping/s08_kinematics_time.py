from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene


class Scene08KinematicsTime(RodLessonScene):
    """Scene 8 -- Kinematics: getting time from theta."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("08", "From Angle to Time", "Separating variables to integrate")
        self.play(FadeIn(header))

        step1 = MathTex(r"\omega=\dfrac{d\theta}{dt}=\sqrt{\dfrac{3g}{L}(\cos\theta_0-\cos\theta)}")
        step2 = MathTex(
            r"t(\theta)=\int_{\theta_0}^{\theta}\dfrac{d\theta'}"
            r"{\sqrt{\tfrac{3g}{L}(\cos\theta_0-\cos\theta')}}"
        ).next_to(step1, DOWN, buff=0.5)
        self.play(Write(step1))
        self.play(Write(step2))
        self.wait(2)

        note = MathTex(r"\text{(evaluated numerically)}", font_size=24, color="#868E96").to_edge(
            DOWN, buff=0.4
        )
        self.play(FadeIn(note))
        self.wait(1)
