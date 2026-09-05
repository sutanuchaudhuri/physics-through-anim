from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene, rod_at, table


class Scene19SlipBegins(RodLessonScene):
    """Scene 19 -- The instant static friction is exhausted."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "19", "The Foot Begins to Slide", r"$f_s$ has reached its ceiling $\mu_s N$"
        )
        self.play(FadeIn(header))

        floor = table(half_width=4.0)
        rod = rod_at(0.42)
        self.play(FadeIn(floor), FadeIn(rod))
        self.wait(0.6)

        eq = MathTex(r"|f_s|=\mu_s N \ \Rightarrow\ \text{contact becomes kinetic}").to_edge(
            DOWN, buff=0.4
        )
        self.play(Write(eq))
        self.wait(2)
