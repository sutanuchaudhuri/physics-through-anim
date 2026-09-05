from manim import DOWN, FadeIn, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene


class Scene21EnergyAfterSlip(RodLessonScene):
    """Scene 21 -- Energy after slip: kinetic friction now dissipates."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "21", "Energy After Slip Begins", "Kinetic friction can remove mechanical energy"
        )
        self.play(FadeIn(header))

        eq = MathTex(
            r"\Delta E=-\int \mu_k N\,v_{\text{slip}}\,dt"
        )
        self.play(Write(eq))
        self.wait(1)

        note = MathTex(
            r"\text{Modeled here as } \mu_k\to0 \text{ (frictionless sliding) for a clean closed form}",
            font_size=24,
            color="#868E96",
        ).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(note))
        self.wait(2)
