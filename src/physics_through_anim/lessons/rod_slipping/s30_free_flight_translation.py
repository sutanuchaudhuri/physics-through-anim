from manim import FadeIn, FadeOut, MathTex, Write

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene


class Scene30FreeFlightTranslation(RodLessonScene):
    """Scene 30 -- Free flight: the CM becomes a projectile."""

    def construct(self) -> None:
        self.add_narration()
        banner = self.chapter_banner("V", "Free Flight and Ground Impact")
        self.play(FadeIn(banner))
        self.wait(1.2)
        self.play(FadeOut(banner))

        header = self.scene_header(
            "30", "The CM Becomes a Projectile", "No more contact forces act on the rod"
        )
        self.play(FadeIn(header))

        eqs = MathTex(
            r"x_G(t)=x_{G,0}+v_{Gx,0}t,\qquad y_G(t)=y_{G,0}+v_{Gy,0}t-\tfrac12 g t^2"
        )
        self.play(Write(eqs))
        self.wait(2)
