from manim import BLUE, ORANGE, UP, FadeIn, MathTex

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene, trajectory


class Scene29CombinedGraph(RodLessonScene):
    """Scene 29 -- Combined omega(t) graph across phases A and B."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "29", "One Continuous Story", r"$\omega(t)$ across both phases so far"
        )
        self.play(FadeIn(header))

        traj = trajectory()
        mask = traj.phase != 2
        t = traj.t[mask]
        omega = traj.omega[mask]

        from manim import Axes

        axes = Axes(
            x_range=[0, float(t[-1]) * 1.02, float(t[-1]) / 6],
            y_range=[0, float(omega[-1]) * 1.15, float(omega[-1]) / 4],
            x_length=8,
            y_length=4,
            axis_config={"include_tip": False, "stroke_width": 2},
        )
        labels = axes.get_axis_labels(MathTex("t", font_size=26), MathTex(r"\omega", font_size=26))
        curve = axes.plot_line_graph(x_values=t, y_values=omega, line_color=BLUE, add_vertex_dots=False)
        marker = MathTex(r"\text{slip}", font_size=20, color=ORANGE).next_to(axes, UP, buff=0.1)
        self.play(FadeIn(axes), FadeIn(labels))
        self.play(FadeIn(curve), FadeIn(marker), run_time=2.0)
        self.wait(1.5)
