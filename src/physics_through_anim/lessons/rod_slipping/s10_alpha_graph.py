from manim import FadeIn, MathTex

from physics_through_anim.lessons.rod_slipping.common import (
    COLOR_ANGULAR_ACCEL,
    RodLessonScene,
    trajectory,
)


class Scene10AlphaGraph(RodLessonScene):
    """Scene 10 -- Live graph of alpha(t): rises then peaks."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "10", "Angular Acceleration Peaks", r"$\alpha(\theta)=\tfrac{3g}{2L}\sin\theta$ before slip"
        )
        self.play(FadeIn(header))

        traj = trajectory()
        mask = traj.phase == 0
        t = traj.t[mask]
        alpha = traj.alpha[mask]

        from manim import Axes

        axes = Axes(
            x_range=[0, float(t[-1]) * 1.05, float(t[-1]) / 5],
            y_range=[0, float(max(alpha)) * 1.15, float(max(alpha)) / 4],
            x_length=8,
            y_length=4,
            axis_config={"include_tip": False, "stroke_width": 2},
        )
        labels = axes.get_axis_labels(MathTex("t", font_size=26), MathTex(r"\alpha", font_size=26))
        curve = axes.plot_line_graph(
            x_values=t, y_values=alpha, line_color=COLOR_ANGULAR_ACCEL, add_vertex_dots=False
        )
        self.play(FadeIn(axes), FadeIn(labels))
        self.play(FadeIn(curve), run_time=2.0)
        self.wait(1.5)
