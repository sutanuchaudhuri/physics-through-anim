"""Scene 14 -- M9 flagship: state-driven overlays on a rolling disk.

Nothing here is hand-computed. The Rule-5 rolling **velocity field** is read from
the disk's own kinematics, and a **GraphBinding** plots omega-vs-t from a supplied
trajectory's observables, its cursor synced to the same time tracker that drives
the roll. Move the clock once; the wheel, the perpendicular rim arrows, and the
graph cursor all advance together.
"""

from __future__ import annotations

import numpy as np
from manim import (
    DOWN,
    UP,
    WHITE,
    FadeIn,
    Text,
    ValueTracker,
)

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.core.refs import QuantityRef
from physics_through_anim.physics.core.state import SystemState
from physics_through_anim.physics.core.trajectory import AnalyticTrajectory
from physics_through_anim.physics.mechanics import Assembly, Disk, Floor
from physics_through_anim.physics.overlays.graphs import (
    GraphBinding,
    QuantitySignal,
    TimeSignal,
)
from physics_through_anim.physics.overlays.kinematics import rolling_velocity_field

GROUND_Y = -2.0
R = 0.8
OMEGA0 = 0.5
ALPHA = 1.0
T_END = 2.0


class RollingFieldGraph(AssetDemoScene):
    """Rule-5 velocity field + a synced omega-vs-t graph, both from state."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("14", "Overlays from state", "velocity field + synced graph")
        self.play(FadeIn(header))

        a = Assembly()
        floor = Floor(y=GROUND_Y, half_width=6.0)
        a.add(floor)
        disk = Disk(name="disk", radius=R, position=(3.5, GROUND_Y + R), label="m")
        disk.set_keypoint("contact", (3.5, GROUND_Y))
        self.add(disk.mobject)
        self.play(FadeIn(a.mobject))

        # omega(t) lives in the trajectory's observables -- the graph reads it, not us.
        def state_at(t: float) -> SystemState:
            return SystemState(observables={"omega": OMEGA0 + ALPHA * t})

        traj = AnalyticTrajectory(state_at)
        graph = GraphBinding(
            x=TimeSignal(),
            y=QuantitySignal(ref=QuantityRef("omega")),
            x_range=(0.0, T_END),
            y_range=(0.0, OMEGA0 + ALPHA * T_END),
        )
        graph_group = graph.build(traj, 0.0, T_END, n=60).scale(0.7)
        graph_group.to_corner(np.array([1.0, 1.0, 0.0]), buff=0.5)
        gl = Text("omega vs t", font_size=20, color=WHITE).next_to(graph_group, UP, buff=0.1)
        self.play(FadeIn(graph_group), FadeIn(gl))

        clock = ValueTracker(0.0)
        base = disk.mobject.copy()
        cm0 = disk.keypoint("CM").copy()

        def roll(m):
            t = clock.get_value()
            angle = OMEGA0 * t + 0.5 * ALPHA * t * t
            x = cm0[0] - R * angle  # CCW spin rolls left, matching the Rule-5 field
            m.become(base.copy())
            m.rotate(angle, about_point=cm0)
            m.shift([x - cm0[0], 0.0, 0.0])
            disk.keypoints["CM"] = np.array([x, cm0[1], 0.0])
            disk.keypoints["contact"] = np.array([x, cm0[1] - R, 0.0])

        def make_field():
            v_cm = (OMEGA0 + ALPHA * clock.get_value()) * R
            return rolling_velocity_field(disk, v_cm=v_cm, points=("top", "3", "9"), scale=0.35)

        field = make_field()
        cap = Text("rim arrows perp to (point - contact); v = 0 at the contact",
                   font_size=21, color=WHITE).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(field), FadeIn(cap))

        disk.mobject.add_updater(roll)
        field.add_updater(lambda m: m.become(make_field()))
        graph.bind(self, clock)
        self.play(clock.animate.set_value(T_END), run_time=3.0)
        disk.mobject.clear_updaters()
        field.clear_updaters()
        self.wait(0.4)
        self.finish_with_narration()
