from manim import FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene, trajectory


class Scene39WhichEndHitsFirst(RodLessonScene):
    """Scene 39 -- Which endpoint touches down first."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "39", "Which End Hits First?", "Determined purely by geometry, not assumed"
        )
        self.play(FadeIn(header))

        traj = trajectory()
        eq = MathTex(rf"\text{{End }} {traj.which_end_hits} \text{{ touches the floor first}}")
        self.play(Write(eq))
        self.wait(2)
