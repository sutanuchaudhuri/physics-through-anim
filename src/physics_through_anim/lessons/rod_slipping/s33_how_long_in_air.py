from manim import FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene, trajectory


class Scene33HowLongInAir(RodLessonScene):
    """Scene 33 -- How long is the rod airborne?"""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("33", "How Long Is It Airborne?", "Solved by root-finding on the endpoints")
        self.play(FadeIn(header))

        traj = trajectory()
        dt = traj.t_hit - traj.t_sep
        eq = MathTex(rf"\Delta t_{{\text{{flight}}}}={dt:.2f}\ \text{{s}}")
        self.play(Write(eq))
        self.wait(2)
