from __future__ import annotations

from manim import (
    BLUE,
    DOWN,
    GREEN,
    ORANGE,
    ORIGIN,
    RIGHT,
    UP,
    Create,
    FadeIn,
    GrowArrow,
    MathTex,
    NumberPlane,
    Write,
)

from physics_through_anim.assets.narration import LocalNarrationScene
from physics_through_anim.assets.visuals import (
    axis_labels,
    dashed_resultant,
    lesson_title,
    vector_arrow,
)


class Vectors(LocalNarrationScene):
    def construct(self) -> None:
        self.add_local_narration()
        title = lesson_title("Vectors", "Direction and magnitude")
        axes = NumberPlane(
            x_range=[-4, 4],
            y_range=[-3, 3],
            background_line_style={"stroke_opacity": 0.25},
        )
        labels = axis_labels()
        first = vector_arrow(ORIGIN, RIGHT * 2, "\\vec{a}", BLUE)
        second = vector_arrow(RIGHT * 2, RIGHT * 2 + UP * 1.5, "\\vec{b}", GREEN)
        result = dashed_resultant(ORIGIN, RIGHT * 2 + UP * 1.5)
        equation = MathTex(r"\\vec{a}+\\vec{b}=\\vec{r}", color=ORANGE).to_edge(DOWN)
        self.play(FadeIn(title), Create(axes), FadeIn(labels))
        self.play(GrowArrow(first[0]), Write(first[1]))
        self.play(GrowArrow(second[0]), Write(second[1]))
        self.play(Create(result), Write(equation))
        self.wait(2)


class Kinematics(LocalNarrationScene):
    def construct(self) -> None:
        self.add_local_narration()
        self.play(Write(lesson_title("Kinematics", "Position, velocity, and acceleration")))
        self.play(Write(MathTex(r"v=\\frac{\\Delta x}{\\Delta t}").scale(1.5)))
        self.wait(2)


class NewtonsLaws(LocalNarrationScene):
    def construct(self) -> None:
        self.add_local_narration()
        self.play(Write(lesson_title("Newton's Laws", "Forces change motion")))
        self.play(Write(MathTex(r"\\sum \\vec F=m\\vec a").scale(1.5)))
        self.wait(2)


class CircularMotion(LocalNarrationScene):
    def construct(self) -> None:
        self.add_local_narration()
        self.play(
            Write(lesson_title("Circular Motion", "Acceleration can turn without speeding up"))
        )
        self.play(Write(MathTex(r"a_c=\\frac{v^2}{r}").scale(1.5)))
        self.wait(2)


class Momentum(LocalNarrationScene):
    def construct(self) -> None:
        self.add_local_narration()
        self.play(Write(lesson_title("Momentum", "Motion transferred in an isolated system")))
        self.play(Write(MathTex(r"\\vec p=m\\vec v").scale(1.5)))
        self.wait(2)


class Energy(LocalNarrationScene):
    def construct(self) -> None:
        self.add_local_narration()
        self.play(Write(lesson_title("Energy", "Track what changes and what stays")))
        self.play(Write(MathTex(r"K+U=\\text{constant}").scale(1.5)))
        self.wait(2)


class RotationalMotion(LocalNarrationScene):
    def construct(self) -> None:
        self.add_local_narration()
        self.play(Write(lesson_title("Rotational Motion", "Torque creates angular acceleration")))
        self.play(Write(MathTex(r"\\tau=I\\alpha").scale(1.5)))
        self.wait(2)


class OrbitalMechanics(LocalNarrationScene):
    def construct(self) -> None:
        self.add_local_narration()
        self.play(Write(lesson_title("Orbital Mechanics", "Falling around a planet")))
        self.play(Write(MathTex(r"F=G\\frac{Mm}{r^2}").scale(1.5)))
        self.wait(2)


class SHM(LocalNarrationScene):
    def construct(self) -> None:
        self.add_local_narration()
        self.play(Write(lesson_title("Simple Harmonic Motion", "A restoring force and a rhythm")))
        self.play(Write(MathTex(r"a=-\\omega^2x").scale(1.5)))
        self.wait(2)


class FluidMechanics(LocalNarrationScene):
    def construct(self) -> None:
        self.add_local_narration()
        self.play(Write(lesson_title("Fluid Mechanics", "Pressure, flow, and continuity")))
        self.play(Write(MathTex(r"A_1v_1=A_2v_2").scale(1.5)))
        self.wait(2)
