from manim import FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene


class Scene34EndpointCoordinates(RodLessonScene):
    """Scene 34 -- Coordinates of both rod ends during flight."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "34", "Tracking Both Ends", "The endpoints trace the CM path plus a rotating offset"
        )
        self.play(FadeIn(header))

        eq = MathTex(
            r"\vec r_{A,B}(t)=\vec r_G(t)\pm s\big(\sin\theta(t),\ \cos\theta(t)\big)"
        )
        self.play(Write(eq))
        self.wait(2)
