from manim import BLUE, FadeIn, MathTex

from physics_through_anim.lessons.rod_slipping.common import RodLessonScene, trajectory


class Scene09OmegaGraph(RodLessonScene):
    """Scene 9 -- Live graph of omega(t) during phase A."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("09", "Angular Velocity Grows", r"$\omega(t)$ before slipping begins")
        self.play(FadeIn(header))

        traj = trajectory()
        mask = traj.phase == 0
        t = traj.t[mask]
        omega = traj.omega[mask]

        from manim import Axes

        axes = Axes(
            x_range=[0, float(t[-1]) * 1.05, float(t[-1]) / 5],
            y_range=[0, float(omega[-1]) * 1.15, float(omega[-1]) / 4],
            x_length=8,
            y_length=4,
            axis_config={"include_tip": False, "stroke_width": 2},
        )
        labels = axes.get_axis_labels(MathTex("t", font_size=26), MathTex(r"\omega", font_size=26))
        curve = axes.plot_line_graph(
            x_values=t, y_values=omega, line_color=BLUE, add_vertex_dots=False
        )
        self.play(FadeIn(axes), FadeIn(labels))
        self.play(FadeIn(curve), run_time=2.0)
        self.wait(1.5)
