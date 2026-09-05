from manim import BLUE, FadeIn, MathTex

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene, trajectory


class Scene25GraphsDuringEdgeContact(RodLessonScene):
    """Scene 25 -- Live graphs of omega and theta during phase B."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "25", "Watching the Numbers While Sliding", r"$\theta(t)$ and $\omega(t)$ during Phase B"
        )
        self.play(FadeIn(header))

        traj = trajectory()
        mask = traj.phase == 1
        t = traj.t[mask]
        omega = traj.omega[mask]

        from manim import Axes

        axes = Axes(
            x_range=[float(t[0]), float(t[-1]) * 1.02, (float(t[-1]) - float(t[0])) / 5],
            y_range=[float(omega[0]) * 0.9, float(omega[-1]) * 1.1, (float(omega[-1]) - float(omega[0])) / 4],
            x_length=8,
            y_length=4,
            axis_config={"include_tip": False, "stroke_width": 2},
        )
        labels = axes.get_axis_labels(MathTex("t", font_size=26), MathTex(r"\omega", font_size=26))
        curve = axes.plot_line_graph(x_values=t, y_values=omega, line_color=BLUE, add_vertex_dots=False)
        self.play(FadeIn(axes), FadeIn(labels))
        self.play(FadeIn(curve), run_time=2.0)
        self.wait(1.5)
