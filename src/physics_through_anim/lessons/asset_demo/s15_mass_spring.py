"""Scene 15 -- M10 flagship: a horizontal mass-spring (SHM) with a phase portrait.

The coil is a real ``LinearSpring`` whose endpoints follow the block, so it
stretches and compresses on screen. The restoring ``F_s`` flips direction as the
mass passes the natural length. A GraphBinding plots velocity against
displacement -- the phase portrait traces an ellipse, its cursor synced to the
same clock that drives the motion. Motion is a supplied analytic SHM law; the
spring only evaluates its local geometry.
"""

from __future__ import annotations

import numpy as np
from manim import (
    DOWN,
    UP,
    WHITE,
    Arrow,
    FadeIn,
    Text,
    ValueTracker,
)

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.core.refs import QuantityRef
from physics_through_anim.physics.core.state import SystemState
from physics_through_anim.physics.core.trajectory import AnalyticTrajectory
from physics_through_anim.physics.mechanics import Floor, LinearSpring, Wall
from physics_through_anim.physics.mechanics.bodies import Block
from physics_through_anim.physics.mechanics.palette import COLOR_SPRING
from physics_through_anim.physics.overlays.graphs import GraphBinding, QuantitySignal

GROUND_Y = -2.0
WALL_X = -3.0
L0 = 2.0  # natural length
HALF = 0.4  # half block width
A = 0.8  # amplitude
OMEGA = 2.0
T_END = float(1.5 * 2.0 * np.pi / OMEGA)  # 1.5 periods


class MassSpringSHM(AssetDemoScene):
    """Live coil deformation + F_s reversal + a velocity-vs-displacement phase portrait."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("15", "Mass on a spring", "SHM + phase portrait")
        self.play(FadeIn(header))

        y = GROUND_Y + HALF
        floor = Floor(y=GROUND_Y, half_width=6.0)
        wall = Wall(angle_deg=90.0, center=(WALL_X, y + 0.3), length=1.8, facing="right")
        x0 = WALL_X + L0 + HALF  # equilibrium CM so spring sits at natural length
        block = Block(name="m", width=2 * HALF, height=2 * HALF, position=(x0, y), label="m")
        spring = LinearSpring(from_point=(WALL_X, y), to_point=(x0 - HALF, y),
                              natural_length=L0, coils=10, width=0.22)
        self.add(floor.mobject, wall.mobject, block.mobject, spring.mobject)
        self.play(FadeIn(floor.mobject), FadeIn(wall.mobject), FadeIn(block.mobject),
                  FadeIn(spring.mobject))

        # Supplied SHM: displacement + velocity live in the trajectory's observables.
        def state_at(t: float) -> SystemState:
            return SystemState(observables={
                "x": A * np.cos(OMEGA * t),
                "v": -A * OMEGA * np.sin(OMEGA * t),
            })

        traj = AnalyticTrajectory(state_at)
        graph = GraphBinding(
            x=QuantitySignal(ref=QuantityRef("x")),
            y=QuantitySignal(ref=QuantityRef("v")),
            x_range=(-A, A),
            y_range=(-A * OMEGA, A * OMEGA),
        )
        graph_group = graph.build(traj, 0.0, T_END, n=120).scale(0.7)
        graph_group.to_corner(np.array([1.0, 1.0, 0.0]), buff=0.5)
        gl = Text("phase portrait: v vs x", font_size=20, color=WHITE)
        gl.next_to(graph_group, UP, buff=0.1)
        self.play(FadeIn(graph_group), FadeIn(gl))

        clock = ValueTracker(0.0)
        base = block.mobject.copy()
        cm0 = block.keypoint("CM").copy()

        def displacement() -> float:
            return A * np.cos(OMEGA * clock.get_value())

        def move_block(m):
            x = cm0[0] + displacement()
            m.become(base.copy())
            m.shift([x - cm0[0], 0.0, 0.0])
            block.keypoints["CM"] = np.array([x, cm0[1], 0.0])
            block.keypoints["left"] = np.array([x - HALF, cm0[1], 0.0])

        def deform_spring(m):
            left = block.keypoints["left"]
            spring.set_endpoints((WALL_X, y), (left[0], y))

        def force_arrow():
            left = block.keypoints["left"]
            d = displacement()
            sign = -1.0 if d >= 0 else 1.0  # inward when stretched, outward when compressed
            tail = np.array([left[0], y, 0.0])
            return Arrow(tail, tail + np.array([0.7 * sign, 0.0, 0.0]),
                         buff=0.0, color=COLOR_SPRING, stroke_width=5)

        fs = force_arrow()
        cap = Text("F_s reverses as the mass crosses the natural length",
                   font_size=21, color=COLOR_SPRING).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(fs), FadeIn(cap))

        block.mobject.add_updater(move_block)
        spring.mobject.add_updater(deform_spring)
        fs.add_updater(lambda m: m.become(force_arrow()))
        graph.bind(self, clock)
        self.play(clock.animate.set_value(T_END), run_time=6.0)
        block.mobject.clear_updaters()
        spring.mobject.clear_updaters()
        fs.clear_updaters()
        self.wait(0.3)
        self.finish_with_narration()
