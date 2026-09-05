from manim import FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene, trajectory


class Scene36HowManySpins(RodLessonScene):
    """Scene 36 -- Number of full rotations before impact."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("36", "How Many Spins?", "Rotation continues uniformly through the fall")
        self.play(FadeIn(header))

        traj = trajectory()
        eq = MathTex(rf"n_{{\text{{spins}}}}={traj.n_spins:.2f}")
        self.play(Write(eq))
        self.wait(2)
