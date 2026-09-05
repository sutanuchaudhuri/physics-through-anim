from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import (
    COLOR_WEIGHT,
    RodLessonScene,
    rod_at,
    table,
)


class Scene07EnergyVisualized(RodLessonScene):
    """Scene 7 -- Visualizing potential-to-kinetic energy trade."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("07", "Energy Trade, Visualized", "The CM falls; rotation speeds up")
        self.play(FadeIn(header))

        floor = table(half_width=4.0)
        self.play(FadeIn(floor))

        thetas = [0.05, 0.6, 1.0, 1.3]
        rod = rod_at(thetas[0])
        self.play(FadeIn(rod))
        for th in thetas[1:]:
            new_rod = rod_at(th)
            self.play(rod.animate.become(new_rod), run_time=0.9)

        pe_ke = MathTex(
            r"PE\downarrow \ \Rightarrow\ KE_{rot}\uparrow", color=COLOR_WEIGHT
        ).to_edge(DOWN, buff=0.4)
        self.play(Write(pe_ke))
        self.wait(1.5)
