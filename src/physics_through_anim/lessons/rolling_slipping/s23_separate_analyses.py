from manim import DOWN, FadeIn, FadeOut, MathTex, VGroup, Write

from physics_through_anim.lessons.rolling_slipping.common import (
    RollingLessonScene,
    translation_rotation_panels,
)


class SeparateAnalyses(RollingLessonScene):
    """Scene 23 -- Separate the Two Analyses."""

    def construct(self) -> None:
        self.add_narration()
        banner = self.chapter_banner("VI", "Translation and Rotation as Two Coupled Problems")
        self.play(FadeIn(banner))
        self.wait(1.2)
        self.play(FadeOut(banner))

        header = self.scene_header(
            "23", "Separate the Two Analyses", "First translation, then rotation"
        )
        self.play(FadeIn(header))

        panels = translation_rotation_panels(
            r"\sum F_x=ma_{\rm CM}", r"\sum \tau_{\rm CM}=I_{\rm CM}\alpha"
        )
        self.play(FadeIn(panels))
        self.wait(1)

        note = (
            VGroup(
                MathTex(r"\text{Separate equations...}"),
                MathTex(r"\text{...coupled only by the contact condition.}"),
            )
            .arrange(DOWN, buff=0.2)
            .to_edge(DOWN, buff=0.4)
        )
        self.play(Write(note))
        self.wait(2)
