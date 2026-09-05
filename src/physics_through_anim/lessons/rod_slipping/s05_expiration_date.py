from manim import DOWN, UP, FadeIn, FadeOut, MathTex, ReplacementTransform, VGroup, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene


class Scene05ExpirationDate(RodLessonScene):
    """Scene 5 -- Important warning: this trick has an expiration date."""

    def construct(self) -> None:
        self.add_narration()
        banner = self.chapter_banner("I", "Setting Up the Fixed-Pivot Phase")
        self.play(FadeIn(banner))
        self.wait(1.2)
        self.play(FadeOut(banner))

        header = self.scene_header(
            "05", "This Shortcut Has an Expiration Date", "It only works while P is fixed"
        )
        self.play(FadeIn(header))

        lock_label = MathTex(r"\text{FIXED IN AN INERTIAL FRAME}", font_size=24, color="#4CD964")
        simple_eq = MathTex(r"\sum\tau_P=I_P\alpha").next_to(lock_label, DOWN, buff=0.3)
        self.play(Write(lock_label), Write(simple_eq))
        self.wait(1)

        general_eq = MathTex(
            r"\sum\tau_P=I_G\alpha+\vec r_{G/P}\times m\vec a_G"
        ).to_edge(DOWN, buff=0.7)
        safe_eq = MathTex(r"\boxed{\sum\tau_G=I_G\alpha}", color="#4CD964").next_to(
            general_eq, UP, buff=0.3
        )
        self.play(ReplacementTransform(VGroup(lock_label, simple_eq), safe_eq))
        self.play(Write(general_eq))
        self.wait(2)
