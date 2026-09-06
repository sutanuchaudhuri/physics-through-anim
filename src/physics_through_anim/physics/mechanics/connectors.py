"""Flexible physical links (Milestone M4). Scaffold.

Ropes/cables are physical links (separate from typed constraints in
``constraints.py``).
"""

from __future__ import annotations

from dataclasses import dataclass

from physics_through_anim.physics.core.pose import Vec2


@dataclass
class Rope:
    from_ref: str = ""
    to_ref: str = ""
    tension_label: str = "T"
    slips: bool = False
    sag: float = 0.0

    def tension_on(self, body_ref: str, at: str, toward: Vec2):
        """Declare a TENSION force on a body along the rope."""
        raise NotImplementedError("M4 Rope.tension_on")


@dataclass
class MasslessLink:
    from_ref: str = ""
    to_ref: str = ""


@dataclass
class Cable(Rope):
    """A rope with give (elastic cable)."""
