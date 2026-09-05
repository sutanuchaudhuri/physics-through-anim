from manim import FadeIn, FadeOut

from physics_through_anim.lessons.rolling_slipping.common import (
    RollingLessonScene,
    derive_with_assumption,
    rolling_constraint_bridge,
    translation_rotation_panels,
)


class CenterPullEquations(RollingLessonScene):
    """Scene 10 -- Translation and Rotation for the Center-Pulled Disk."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "10", "Translation and Rotation", "Coupled by the no-slip constraint"
        )
        self.play(FadeIn(header))

        panels = translation_rotation_panels("F-f=ma", "fR=I\\alpha")
        self.play(FadeIn(panels))
        bridge = rolling_constraint_bridge().shift([0, -1.8, 0])
        self.play(FadeIn(bridge))
        self.wait(1)
        self.play(FadeOut(panels), FadeOut(bridge))

        # Assumption check: I = (1/2) m R^2 only holds for a *solid* disk.
        # Show it explicitly, then fade the general relation + assumption into
        # the specific numeric result, instead of a boxed answer from nowhere.
        derive_with_assumption(
            self,
            general_tex=r"f=\frac{I\alpha}{R},\quad a=\alpha R",
            assumption_tex=r"\text{solid disk:}\ \ I=\tfrac12 mR^2",
            result_tex=r"\boxed{f=\tfrac{F}{3}}",
        )
        self.wait(2)
