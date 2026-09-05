from manim import FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene, trajectory


class Scene28ExactSeparationState(RodLessonScene):
    """Scene 28 -- The exact kinematic state at separation."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("28", "The State at Separation", "Angle, angular velocity, and CM velocity")
        self.play(FadeIn(header))

        import numpy as np

        traj = trajectory()
        rows = MathTex(
            rf"\theta_{{sep}}={np.degrees(traj.theta_sep):.1f}^\circ,\quad "
            rf"\omega_{{sep}}={traj.omega_sep:.2f}\ \text{{rad/s}},\quad "
            rf"t_{{sep}}={traj.t_sep:.2f}\ \text{{s}}"
        )
        self.play(Write(rows))
        self.wait(2)
