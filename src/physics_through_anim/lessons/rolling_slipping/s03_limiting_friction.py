from manim import DOWN, FadeIn, MathTex, ReplacementTransform, Write

from physics_through_anim.lessons.rolling_slipping.common import RollingLessonScene, friction_meter


class LimitingFriction(RollingLessonScene):
    """Scene 3 -- Limiting Static Friction."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "03", "Limiting Static Friction", "Friction rises with the push, up to a ceiling"
        )
        self.play(FadeIn(header))

        meter = friction_meter(0.0)
        self.play(FadeIn(meter))
        for fraction in (0.3, 0.6, 0.85, 1.0):
            next_meter = friction_meter(fraction)
            self.play(ReplacementTransform(meter, next_meter))
            meter = next_meter

        limit = MathTex(r"f_{s,\max} = \mu_s N").to_edge(DOWN, buff=0.35)
        self.play(Write(limit))
        self.wait(2)
