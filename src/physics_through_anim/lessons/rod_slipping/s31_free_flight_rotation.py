from manim import FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene


class Scene31FreeFlightRotation(RodLessonScene):
    """Scene 31 -- Free flight: constant angular velocity."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "31", "Rotation Keeps Its Own Pace", "No torque about G means constant omega"
        )
        self.play(FadeIn(header))

        eq = MathTex(r"\sum\tau_G=0 \ \Rightarrow\ \alpha=0 \ \Rightarrow\ \theta(t)=\theta_{sep}+\omega_{sep}\,t")
        self.play(Write(eq))
        self.wait(2)
