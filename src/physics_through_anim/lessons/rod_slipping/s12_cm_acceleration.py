from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene


class Scene12CMAcceleration(RodLessonScene):
    """Scene 12 -- The CM acceleration components."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("12", "Acceleration of the Center of Mass", "G moves on a circular arc about P")
        self.play(FadeIn(header))

        pos = MathTex(r"x_G=\tfrac L2\sin\theta,\qquad y_G=\tfrac L2\cos\theta")
        self.play(Write(pos))
        self.wait(1)

        accel = MathTex(
            r"a_{Gx}=\tfrac L2(\alpha\cos\theta-\omega^2\sin\theta)"
        ).next_to(pos, DOWN, buff=0.4)
        accel2 = MathTex(
            r"a_{Gy}=-\tfrac L2(\alpha\sin\theta+\omega^2\cos\theta)"
        ).next_to(accel, DOWN, buff=0.3)
        self.play(Write(accel))
        self.play(Write(accel2))
        self.wait(2)
