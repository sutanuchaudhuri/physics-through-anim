"""Scene 02 -- M1.6 render smoke: eight acceptance cases driven by bindings.

Every case is posed by the M1.6 kinematics layer (``Transform2D``/``Pose2D`` +
``kinematics`` bindings), never by ad-hoc ``.animate.shift().rotate()``. Each
segment fades in, animates from a supplied kinematic parameter, and fades out
(SKILL Rule 16 sequential), so a frame per case verifies pose, attachment
tracking, rolling (no drift), and path-tangent orientation.
"""

from __future__ import annotations

from math import cos, pi, sin

import numpy as np
from manim import (
    BLUE,
    DOWN,
    GREEN,
    ORIGIN,
    WHITE,
    YELLOW,
    Arc,
    Circle,
    Dot,
    FadeIn,
    FadeOut,
    Line,
    Rectangle,
    Text,
    Triangle,
    ValueTracker,
    VGroup,
)

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.kinematics import (
    PathPoseBinding,
    PointAttachmentBinding,
    RelativePoseBinding,
    RollingKinematicRelation,
)
from physics_through_anim.physics.mechanics.massprops import MassProperties
from physics_through_anim.physics.mechanics.rigidbody import RigidBody2D

GROUND_Y = -2.4


def _place(mob, base, pose: Pose2D) -> None:
    """Pose a mobject from its canonical (origin-built) ``base`` -- drift-free."""
    mob.become(base.copy())
    mob.rotate(pose.angle, about_point=ORIGIN)
    mob.shift(np.array([pose.position[0], pose.position[1], 0.0]))


def _body(**keypoints) -> RigidBody2D:
    kp = {"CM": (0.0, 0.0)}
    kp.update(keypoints)
    return RigidBody2D(mass_props=MassProperties(mass=1.0, inertia_cm=0.5), local_keypoints=kp)


class KinematicsBindings(AssetDemoScene):
    """The eight M1.6 acceptance cases, each posed by a binding."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("02", "M1.6 kinematics bindings", "one mechanism drives all")
        self.play(FadeIn(header))
        floor = Line([-6.0, GROUND_Y, 0.0], [6.0, GROUND_Y, 0.0], color=WHITE, stroke_width=2)
        self.add(floor)

        self._case_translation()
        self._case_rotation_about_hinge()
        self._case_general_plane_motion()
        self._case_point_attachment()
        self._case_spring_attachment()
        self._case_rolling()
        self._case_path_follow()
        self._case_linked_rods()

        self.finish_with_narration()

    # --- helpers ----------------------------------------------------------

    def _caption(self, text: str) -> Text:
        return Text(text, font_size=22, color=YELLOW).to_edge(DOWN, buff=0.5)

    def _run(self, caption: Text, mobjects, tracker_updater, run_time: float = 1.4) -> None:
        group = VGroup(*mobjects)
        self.play(FadeIn(group), FadeIn(caption), run_time=0.4)
        tracker_updater(run_time)
        self.play(FadeOut(group), FadeOut(caption), run_time=0.3)

    # --- 1. translating block --------------------------------------------

    def _case_translation(self) -> None:
        base = Rectangle(width=1.0, height=0.6, color=BLUE, fill_opacity=0.3).move_to(ORIGIN)
        block = base.copy()
        y = GROUND_Y + 0.3

        def drive(rt: float) -> None:
            s = ValueTracker(-3.0)
            block.add_updater(lambda m: _place(m, base, Pose2D(position=(s.get_value(), y))))
            self.play(s.animate.set_value(3.0), run_time=rt)
            block.clear_updaters()

        self._run(self._caption("1. translating block (RigidPoseBinding)"), [block], drive)

    # --- 2. rod rotating about a fixed hinge -----------------------------

    def _case_rotation_about_hinge(self) -> None:
        length = 2.4
        hinge = np.array([-2.5, GROUND_Y + 0.2, 0.0])
        base = Line(ORIGIN, [length, 0.0, 0.0], color=GREEN, stroke_width=8)
        rod = base.copy()
        pivot = Dot(hinge, color=YELLOW, radius=0.06)

        def drive(rt: float) -> None:
            theta = ValueTracker(0.0)
            rod.add_updater(
                lambda m: _place(
                    m, base, Pose2D(position=(hinge[0], hinge[1]), angle=theta.get_value())
                )
            )
            self.play(theta.animate.set_value(pi / 2), run_time=rt)
            rod.clear_updaters()

        self._run(self._caption("2. rod rotating about a fixed hinge"), [rod, pivot], drive)

    # --- 3. rod: translation + rotation (general plane motion) -----------

    def _case_general_plane_motion(self) -> None:
        length = 2.0
        base = Line(ORIGIN, [length, 0.0, 0.0], color=GREEN, stroke_width=8)
        rod = base.copy()

        def drive(rt: float) -> None:
            u = ValueTracker(0.0)

            def upd(m):
                x = -3.0 + 5.0 * u.get_value()
                _place(m, base, Pose2D(position=(x, GROUND_Y + 1.4), angle=pi * u.get_value()))

            rod.add_updater(upd)
            self.play(u.animate.set_value(1.0), run_time=rt)
            rod.clear_updaters()

        self._run(self._caption("3. translation + rotation (general plane motion)"), [rod], drive)

    # --- 4. point attached to a moving body ------------------------------

    def _case_point_attachment(self) -> None:
        base = Rectangle(width=1.2, height=0.7, color=BLUE, fill_opacity=0.3).move_to(ORIGIN)
        block = base.copy()
        marker = Dot(color=YELLOW, radius=0.08)
        parent = _body(corner=(0.6, 0.35))
        child = _body()
        y = GROUND_Y + 1.2

        def drive(rt: float) -> None:
            s = ValueTracker(-3.0)

            def upd(_):
                parent.set_pose(Pose2D(position=(s.get_value(), y), angle=0.5 * s.get_value()))
                PointAttachmentBinding(child, parent, "corner", "CM").apply()
                _place(block, base, parent.pose)
                marker.move_to(child.keypoint("CM"))

            block.add_updater(upd)
            self.play(s.animate.set_value(3.0), run_time=rt)
            block.clear_updaters()

        self._run(
            self._caption("4. point attached to a moving body (PointAttachmentBinding)"),
            [block, marker],
            drive,
        )

    # --- 5. spring attached to a moving block ----------------------------

    def _case_spring_attachment(self) -> None:
        wall = np.array([-4.5, GROUND_Y + 1.0, 0.0])
        anchor = Dot(wall, color=WHITE, radius=0.05)
        base = Rectangle(width=1.0, height=0.6, color=BLUE, fill_opacity=0.3).move_to(ORIGIN)
        block = base.copy()
        spring = Line(wall, wall, color=YELLOW, stroke_width=4)
        parent = _body(hook=(-0.5, 0.0))
        y = GROUND_Y + 1.0

        def drive(rt: float) -> None:
            s = ValueTracker(-1.5)

            def upd(_):
                parent.set_pose(Pose2D(position=(s.get_value(), y)))
                _place(block, base, parent.pose)
                hook = parent.keypoint("hook")
                spring.put_start_and_end_on(wall, hook)

            block.add_updater(upd)
            self.play(s.animate.set_value(2.5), run_time=rt)
            block.clear_updaters()

        self._run(
            self._caption("5. spring endpoint follows the block (attachment + redraw)"),
            [anchor, spring, block],
            drive,
        )

    # --- 6. wheel translating + rotating (rolling, no drift) -------------

    def _case_rolling(self) -> None:
        radius = 0.6
        rel = RollingKinematicRelation(radius=radius, direction=1)
        origin = Pose2D(position=(-3.0, GROUND_Y + radius))
        base = VGroup(
            Circle(radius=radius, color=BLUE),
            Line(ORIGIN, [radius, 0.0, 0.0], color=YELLOW, stroke_width=5),
        )
        wheel = base.copy()

        def drive(rt: float) -> None:
            s = ValueTracker(0.0)

            def upd(m):
                _place(m, base, origin.compose(rel.pose_from_arc(s.get_value())))

            wheel.add_updater(upd)
            self.play(s.animate.set_value(6.0), run_time=rt)
            wheel.clear_updaters()

        self._run(
            self._caption("6. wheel rolling: v = omega R (RollingPoseBinding)"), [wheel], drive
        )

    # --- 7. object following a curved path (tangent orientation) ---------

    def _case_path_follow(self) -> None:
        cx, cy, r = 2.5, GROUND_Y + 1.6, 1.3
        a0, a1 = pi, -pi / 6
        guide = Arc(radius=r, start_angle=a0, angle=a1 - a0, color=WHITE, stroke_width=2).move_to(
            [cx + 0 * r, cy, 0.0]
        )
        guide.shift([cx, cy, 0.0] - guide.get_arc_center())

        class _ArcPath:
            def point_at(self, s: float):
                ang = a0 + s * (a1 - a0)
                return (cx + r * cos(ang), cy + r * sin(ang))

            def tangent_angle(self, s: float) -> float:
                return a0 + s * (a1 - a0) + pi / 2

        base = Triangle(color=GREEN, fill_opacity=0.5).scale(0.22).rotate(-pi / 2)  # points +x
        glider = base.copy()
        body = _body()
        path = _ArcPath()

        def drive(rt: float) -> None:
            s = ValueTracker(0.0)

            def upd(m):
                PathPoseBinding(body, path, s=s.get_value(), orientation="tangent").apply()
                _place(m, base, body.pose)

            glider.add_updater(upd)
            self.play(s.animate.set_value(1.0), run_time=rt)
            glider.clear_updaters()

        self._run(
            self._caption("7. following a curved path (PathPoseBinding, tangent)"),
            [guide, glider],
            drive,
        )

    # --- 8. two linked rods (scene-graph propagation) --------------------

    def _case_linked_rods(self) -> None:
        l1, l2 = 1.8, 1.4
        hinge = np.array([-1.0, GROUND_Y + 1.4, 0.0])
        base1 = Line(ORIGIN, [l1, 0.0, 0.0], color=GREEN, stroke_width=8)
        base2 = Line(ORIGIN, [l2, 0.0, 0.0], color=BLUE, stroke_width=8)
        rod1, rod2 = base1.copy(), base2.copy()
        pivot = Dot(hinge, color=YELLOW, radius=0.06)
        body1 = _body(end=(l1, 0.0))
        body2 = _body()

        def drive(rt: float) -> None:
            u = ValueTracker(0.0)

            def upd(_):
                body1.set_pose(Pose2D(position=(hinge[0], hinge[1]), angle=0.6 * u.get_value()))
                RelativePoseBinding(
                    body2, body1, Pose2D(position=(l1, 0.0), angle=-1.2 * u.get_value())
                ).apply()
                _place(rod1, base1, body1.pose)
                _place(rod2, base2, body2.pose)

            rod1.add_updater(upd)
            self.play(u.animate.set_value(1.0), run_time=rt)
            rod1.clear_updaters()

        self._run(
            self._caption("8. two linked rods (RelativePoseBinding propagation)"),
            [rod1, rod2, pivot],
            drive,
        )
