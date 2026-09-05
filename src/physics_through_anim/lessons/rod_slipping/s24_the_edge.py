from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene, rod_at, table


class Scene24TheEdge(RodLessonScene):
    """Scene 24 -- The rounded table edge geometry."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "24", "The Table's Edge", "A rounded edge avoids an infinite-curvature contact"
        )
        self.play(FadeIn(header))

        floor = table(half_width=4.0)
        rod = rod_at(1.0, x_foot=3.6)
        self.play(FadeIn(floor), FadeIn(rod))

        note = MathTex(r"\text{Contact ends when the foot reaches the physical edge}").to_edge(
            DOWN, buff=0.4
        )
        self.play(Write(note))
        self.wait(2)
