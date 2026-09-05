from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene, rod_at, table


class Scene23SlidingTowardEdge(RodLessonScene):
    """Scene 23 -- The foot slides toward the table's edge."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "23", "Sliding Toward the Edge", "The contact point is not fixed in space anymore"
        )
        self.play(FadeIn(header))

        floor = table(half_width=4.0)
        rod = rod_at(0.5)
        self.play(FadeIn(floor), FadeIn(rod))

        for th in [0.6, 0.75, 0.9]:
            new_rod = rod_at(th, x_foot=(th - 0.5) * 1.5)
            self.play(rod.animate.become(new_rod), run_time=0.8)

        note = MathTex(r"x_P(t)=\int v_{\text{foot}}\,dt").to_edge(DOWN, buff=0.4)
        self.play(Write(note))
        self.wait(1.5)
