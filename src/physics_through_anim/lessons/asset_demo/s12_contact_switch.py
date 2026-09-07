"""Scene 12 -- M7 contact switch + separation: a held body is released.

A block is *held* by a constraint (reaction ``R`` balances ``mg``). At a
**CONSTRAINT_CHANGE** event the hold releases: the reaction goes to zero (the
contact separates) and the body free-falls under a supplied trajectory. Every
time the constraint changes, the governing description is reconsidered -- the
framework only *marks* the instant; the trajectory supplies *when*.
"""

from __future__ import annotations

from manim import DOWN, RED, WHITE, FadeIn, FadeOut, Flash, Text, ValueTracker

from physics_through_anim.lessons.asset_demo.common import AssetDemoScene
from physics_through_anim.physics.core.events import ConstraintChange, Event, EventKind
from physics_through_anim.physics.core.pose import Pose2D
from physics_through_anim.physics.core.state import RigidKinematicState, SystemState
from physics_through_anim.physics.mechanics import Assembly, Block, Floor, Hinge
from physics_through_anim.physics.mechanics.constraints import PinConstraint
from physics_through_anim.physics.mechanics.contact import Contact
from physics_through_anim.physics.mechanics.kinds import ForceKind

GROUND_Y = -2.6
G = 6.0
HOLD_Y = 1.6


class ContactSwitch(AssetDemoScene):
    """Held (reaction balances weight) -> released (reaction gone, free fall)."""

    def construct(self) -> None:
        self.add_narration()
        header = self.scene_header("12", "Contact switch + separation", "a held body is released")
        self.play(FadeIn(header))

        a = Assembly()
        floor = Floor(y=GROUND_Y, half_width=6.0)
        a.add(floor)
        block = Block(name="block", position=(0.0, HOLD_Y), width=1.0, label="m")
        block.add_force(ForceKind.REACTION, at="top", label="R", direction="up")
        a.add(block)
        hinge = Hinge(at=(0.0, HOLD_Y + block.display_height / 2.0))
        a.add(hinge)

        # Relations + the release event on the timeline.
        contact = Contact(body="block", surface="hold")
        a.add_relation(contact)
        a.add_relation(PinConstraint(participants=("block", "hold")), name="hold")
        a.timeline.add(
            Event(time=1.0, kind=EventKind.CONSTRAINT_CHANGE, participants=("block", "hold"),
                  changes=ConstraintChange(deactivate=("hold",)), tag="released")
        )

        fbd = a.fbd()  # R up, mg down -- balanced while held
        held = Text("held: reaction R balances weight mg (constraint ACTIVE)",
                    font_size=21, color=WHITE).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(a.mobject), FadeIn(fbd), FadeIn(held))
        self.wait(0.8)

        # --- the release event: constraint off, N/R -> 0, contact separates ---
        a.at(1.5)  # apply the constraint set after the event
        assert a.constraints_by_name["hold"].active is False
        contact.on_separation(block, normal_label="R")
        self.play(Flash(hinge.keypoint("H"), color=RED, flash_radius=0.4),
                  FadeOut(fbd), FadeOut(hinge.mobject), FadeOut(held))
        released = Text("released: R -> 0, contact SEPARATES -> free fall",
                        font_size=21, color=RED).to_edge(DOWN, buff=0.5)
        self.play(FadeIn(released))

        # --- free flight from the supplied trajectory (asset never integrates) ---
        half_h = block.display_height / 2.0
        drop = HOLD_Y - (GROUND_Y + half_h)
        t_land = float((2.0 * drop / G) ** 0.5)

        def fall(t: float) -> SystemState:
            y = HOLD_Y - 0.5 * G * t * t
            return SystemState(
                entities={"block": RigidKinematicState(pose=Pose2D(position=(0.0, y)),
                                                       velocity=(0.0, -G * t))}
            )

        s = ValueTracker(0.0)

        def drop_block(_):
            block.apply_state(fall(s.get_value()).entities["block"])

        block.mobject.add_updater(drop_block)
        self.play(s.animate.set_value(t_land), run_time=1.6)
        block.mobject.clear_updaters()
        self.wait(0.4)
        self.finish_with_narration()
