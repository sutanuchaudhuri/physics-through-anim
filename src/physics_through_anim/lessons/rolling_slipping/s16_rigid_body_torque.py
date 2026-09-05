from manim import (
    DOWN,
    LEFT,
    PI,
    RIGHT,
    UP,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    MathTex,
    Rotate,
    VGroup,
    Write,
)

from physics_through_anim.lessons.rolling_slipping.common import (
    COLOR_ANGULAR_ACCEL,
    COLOR_APPLIED,
    RollingLessonScene,
    angular_accel_arc,
)


class RigidBodyTorque(RollingLessonScene):
    """Scene 16 -- Build a Rigid Body From Particles.

    Paired layout, not a text wall: a live particle-on-a-rod diagram on the
    left (with its tangential force and angular acceleration arc) alongside
    the derivation it justifies on the right.
    """

    def construct(self) -> None:
        self.add_narration()
        banner = self.chapter_banner("IV", "Why Rotation Responds to Torque")
        self.play(FadeIn(banner))
        self.wait(1.2)
        self.play(FadeOut(banner))

        header = self.scene_header(
            "16", "Build a Rigid Body From Particles", "Sum the torques particle by particle"
        )
        self.play(FadeIn(header))

        pivot = LEFT * 3.4
        radius = 1.1
        spoke = Line(pivot, pivot + RIGHT * radius, color="#888888", stroke_width=3)
        particle = Dot(pivot + RIGHT * radius, color=COLOR_APPLIED, radius=0.09)
        tangential_force = Line(
            pivot + RIGHT * radius,
            pivot + RIGHT * radius + UP * 0.8,
            color=COLOR_APPLIED,
            stroke_width=5,
        )
        alpha_arc = angular_accel_arc(pivot, radius=0.5)
        r_label = MathTex("r_i", font_size=26).next_to(spoke, DOWN, buff=0.12)
        diagram = VGroup(spoke, particle, tangential_force, alpha_arc, r_label)
        self.play(FadeIn(diagram))
        self.play(
            Rotate(VGroup(spoke, particle, tangential_force), angle=PI / 3, about_point=pivot)
        )

        step1 = MathTex(r"a_{t,i}=\alpha r_i \ \Rightarrow\ F_{t,i}=m_i\alpha r_i", font_size=32)
        step2 = MathTex(r"\tau_i = r_i F_{t,i} = m_i r_i^2 \alpha", font_size=32)
        step3 = MathTex(r"\sum_i \tau_i = \left(\sum_i m_i r_i^2\right)\alpha", font_size=32)
        definition = MathTex(r"\boxed{I \equiv \sum_i m_i r_i^2}", font_size=32)
        result = MathTex(r"\boxed{\tau = I\alpha}", font_size=34, color=COLOR_ANGULAR_ACCEL)
        stack = (
            VGroup(step1, step2, step3, definition, result)
            .arrange(DOWN, buff=0.3)
            .move_to(RIGHT * 2.2)
        )
        for line in stack:
            self.play(Write(line))
        self.wait(2)
