from manim import BLUE, DOWN, ORANGE, FadeIn, MathTex

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene, trajectory


class Scene15FrictionDemandGraph(RodLessonScene):
    """Scene 15 -- Graphing the friction ratio f_s/N vs theta."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "15", "The Friction-Demand Curve", r"$f_s(\theta)/N(\theta)$ rises toward the slip limit"
        )
        self.play(FadeIn(header))

        traj = trajectory()
        mask = traj.phase == 0
        theta = traj.theta[mask]
        with_zero_normal = traj.normal[mask] > 1e-6
        ratio = traj.friction[mask][with_zero_normal] / traj.normal[mask][with_zero_normal]
        theta = theta[with_zero_normal]

        from manim import Axes

        axes = Axes(
            x_range=[0, float(theta[-1]) * 1.05, float(theta[-1]) / 5],
            y_range=[0, 0.35, 0.05],
            x_length=8,
            y_length=4,
            axis_config={"include_tip": False, "stroke_width": 2},
        )
        labels = axes.get_axis_labels(MathTex(r"\theta", font_size=26), MathTex(r"f_s/N", font_size=26))
        curve = axes.plot_line_graph(x_values=theta, y_values=ratio, line_color=ORANGE, add_vertex_dots=False)
        limit_line = axes.plot(lambda x: 0.30, color=BLUE)
        limit_label = MathTex(r"\mu_s=0.30", color=BLUE, font_size=24).next_to(axes, DOWN, buff=0.3)
        self.play(FadeIn(axes), FadeIn(labels))
        self.play(FadeIn(curve), FadeIn(limit_line), FadeIn(limit_label), run_time=2.0)
        self.wait(1.5)
