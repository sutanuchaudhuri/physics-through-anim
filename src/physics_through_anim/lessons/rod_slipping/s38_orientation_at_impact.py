from manim import FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene, trajectory


class Scene38OrientationAtImpact(RodLessonScene):
    """Scene 38 -- The rod's exact orientation at impact."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("38", "Orientation at Impact", "Read directly from the unwrapped angle")
        self.play(FadeIn(header))

        import numpy as np

        traj = trajectory()
        eq = MathTex(rf"\theta_{{\text{{hit}}}}={np.degrees(traj.theta_hit):.1f}^\circ")
        self.play(Write(eq))
        self.wait(2)
