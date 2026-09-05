from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Arrow,
    Axes,
    DashedLine,
    DecimalNumber,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    MathTex,
    Text,
    ValueTracker,
    VGroup,
    Write,
    always_redraw,
)
from manim import GRAY as MGRAY

from physics_through_anim.lessons.rolling_slipping.common import (
    COLOR_APPLIED,
    COLOR_FRICTION,
    RollingLessonScene,
    rough_ground,
    thin_block,
)

# The static-friction limit mu_s N corresponds to F_MAX "newtons"; 1 N of
# force draws as FORCE_SCALE screen-units of arrow.
F_MAX = 6.0
FORCE_SCALE = 0.26


class WhyNotBackward(RollingLessonScene):
    """Scene 2 -- How static friction responds (graph-anchored).

    The graph of f_s vs F is the conceptual anchor: a dot climbs the line
    f_s = F in exact sync with the block's two force arrows growing, until it
    reaches the ceiling f_{s,max} = mu_s N. One ValueTracker drives the graph
    dot, both arrows, and the numeric readouts so everything advances together.
    """

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header(
            "02",
            "How Static Friction Responds",
            "Static friction adjusts — up to a limit",
        )
        self.play(FadeIn(header))

        applied = ValueTracker(0.0)

        # --- Graph (conceptual anchor, upper band) ------------------------
        axes = Axes(
            x_range=[0, 7, 1],
            y_range=[0, 7, 1],
            x_length=5.6,
            y_length=2.4,
            tips=False,
            axis_config={"include_numbers": False},
        ).move_to(UP * 1.0)
        x_label = MathTex("F", color=COLOR_APPLIED).scale(0.7).next_to(axes.x_axis, RIGHT, buff=0.1)
        y_label = MathTex("f_s", color=COLOR_FRICTION).scale(0.7).next_to(axes.y_axis, UP, buff=0.1)
        graph_title = Text("Static friction vs applied force", font_size=20, color=MGRAY)
        graph_title.next_to(axes, UP, buff=0.15)
        self.play(FadeIn(VGroup(axes, x_label, y_label, graph_title)))

        # Ceiling: the maximum static friction available.
        max_line = DashedLine(axes.c2p(0, F_MAX), axes.c2p(7, F_MAX), color=MGRAY, dash_length=0.08)
        max_label = MathTex(r"f_{s,\max}=\mu_s N", color=COLOR_FRICTION).scale(0.55)
        max_label.next_to(axes.c2p(7, F_MAX), RIGHT, buff=0.1)
        self.play(FadeIn(max_line), Write(max_label))

        # The solid f_s = F line is DISCOVERED as the experiment runs: it grows
        # from the origin behind the moving state dot, both tied to `applied`.
        def graph_end():
            v = max(applied.get_value(), 0.001)
            return axes.c2p(v, v)

        graph_line = always_redraw(
            lambda: Line(axes.c2p(0, 0), graph_end(), color=COLOR_FRICTION, stroke_width=5)
        )
        state_dot = always_redraw(lambda: Dot(graph_end(), color=COLOR_FRICTION, radius=0.08))

        # --- Block + synchronized force arrows (lower band) ---------------
        ground = rough_ground()
        block = thin_block(width=1.7, height=0.6, x=0.0)
        block_label = MathTex("m").move_to(block.get_center())
        self.play(FadeIn(ground), FadeIn(block), FadeIn(block_label))

        def applied_arrow() -> Arrow:
            start = block.get_right()
            end = start + RIGHT * (0.18 + FORCE_SCALE * applied.get_value())
            return Arrow(start, end, buff=0, color=COLOR_APPLIED, stroke_width=6)

        def friction_arrow() -> Arrow:
            start = block.get_left()
            end = start + LEFT * (0.18 + FORCE_SCALE * min(applied.get_value(), F_MAX))
            return Arrow(start, end, buff=0, color=COLOR_FRICTION, stroke_width=6)

        f_arrow = always_redraw(applied_arrow)
        f_label = MathTex("F", color=COLOR_APPLIED).scale(0.8)
        f_label.add_updater(lambda m: m.next_to(f_arrow, RIGHT, buff=0.1))
        fs_arrow = always_redraw(friction_arrow)
        fs_label = MathTex("f_s", color=COLOR_FRICTION).scale(0.8)
        fs_label.add_updater(lambda m: m.next_to(fs_arrow, LEFT, buff=0.1))

        f_num = DecimalNumber(0, num_decimal_places=1).scale(0.7)
        f_num.add_updater(lambda d: d.set_value(applied.get_value()))
        fs_num = DecimalNumber(0, num_decimal_places=1).scale(0.7)
        fs_num.add_updater(lambda d: d.set_value(min(applied.get_value(), F_MAX)))
        readout = VGroup(
            MathTex("F=", color=COLOR_APPLIED).scale(0.7), f_num, MathTex(r"\text{N}").scale(0.7),
            MathTex("f_s=", color=COLOR_FRICTION).scale(0.7), fs_num,
            MathTex(r"\text{N}").scale(0.7),
        ).arrange(RIGHT, buff=0.12).to_edge(DOWN, buff=0.35)

        # Beat 1: start from zero -- no tendency to slip, so f_s = 0.
        zero_statement = MathTex(r"F=0 \ \Rightarrow\ f_s=0").scale(0.75).move_to(DOWN * 0.7)
        self.play(Write(zero_statement))
        self.wait(1.2)
        self.play(FadeOut(zero_statement))
        self.add(f_arrow, f_label, fs_arrow, fs_label, readout, graph_line, state_dot)

        # Beat 2: friction adjusts to match -- climb the line together, slowly
        # enough that the dot and arrows track the voice-over (Rule 18).
        relation = MathTex(r"f_s = F", color=COLOR_FRICTION).scale(0.75).move_to(DOWN * 0.7)
        self.play(Write(relation))
        self.play(applied.animate.set_value(2.0), run_time=8.0)
        self.wait(1.0)
        self.play(applied.animate.set_value(4.0), run_time=8.0)
        self.wait(1.0)

        # Beat 3: approach the ceiling.
        nearing = MathTex(r"F\uparrow \ \Rightarrow\ f_s\uparrow").scale(0.75).move_to(DOWN * 0.7)
        self.play(FadeOut(relation), FadeIn(nearing))
        self.play(applied.animate.set_value(5.5), run_time=6.0)
        self.wait(1.0)

        # Beat 4: reach the maximum -- friction can climb no further.
        self.play(applied.animate.set_value(F_MAX), run_time=5.0)
        max_point = Dot(axes.c2p(F_MAX, F_MAX), color=COLOR_APPLIED, radius=0.1)
        self.play(FadeIn(max_point))
        self.play(FadeOut(nearing))
        limit_statement = MathTex(
            r"f_s = f_{s,\max} = \mu_s N", color=COLOR_FRICTION
        ).scale(0.75).move_to(DOWN * 0.7)
        self.play(Write(limit_statement))
        self.wait(1.2)

        # Closing takeaway: mu_s N is a capacity, not the value friction exerts.
        self.play(FadeOut(limit_statement))
        final_statement = (
            MathTex(r"\boxed{\,0 \le f_s \le \mu_s N\,}").scale(0.85).move_to(DOWN * 0.7)
        )
        self.play(Write(final_statement))

        # Keep the last frame up until the voice-over finishes (Rule 18).
        self.finish_with_narration()
