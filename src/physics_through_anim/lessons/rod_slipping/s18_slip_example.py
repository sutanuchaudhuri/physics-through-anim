from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene, trajectory


class Scene18SlipExample(RodLessonScene):
    """Scene 18 -- Worked numeric example: mu_s = 0.30."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("18", "A Worked Example", r"$\mu_s=0.30$")
        self.play(FadeIn(header))

        traj = trajectory()
        import numpy as np

        theta_s_deg = np.degrees(traj.theta_slip)
        eq = MathTex(r"\mu_s=0.30")
        self.play(Write(eq))
        self.wait(0.6)

        result = MathTex(rf"\boxed{{\theta_s\approx{theta_s_deg:.1f}^\circ}}").next_to(
            eq, DOWN, buff=0.5
        )
        self.play(Write(result))
        self.wait(2)
