from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene


class Scene06EnergyMethod(RodLessonScene):
    """Scene 6 -- The energy method for omega(theta)."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("06", "The Energy Method", "Trading height for rotation speed")
        self.play(FadeIn(header))

        conservation = MathTex(
            r"mg\tfrac L2(\cos\theta_0-\cos\theta)=\tfrac12 I_P\omega^2"
        )
        self.play(Write(conservation))
        self.wait(1)

        solved = MathTex(
            r"\boxed{\omega(\theta)=\sqrt{\dfrac{3g}{L}(\cos\theta_0-\cos\theta)}}"
        ).next_to(conservation, DOWN, buff=0.5)
        self.play(Write(solved))
        self.wait(2)
