"""Collision / event overlays (Milestone M12). Scaffold."""

from __future__ import annotations

from dataclasses import dataclass

from physics_through_anim.physics.core.events import Event, EventKind, EventSequence


@dataclass
class EventCounter:
    """On-screen tally of collisions so far."""

    seq: EventSequence = None
    kinds: tuple[EventKind, ...] = (EventKind.IMPACT,)

    def count_at(self, t: float) -> int:
        raise NotImplementedError("M12 EventCounter.count_at")


def impulse_arrow(body, impulse: float, at: str = "CM"):
    raise NotImplementedError("M12 impulse_arrow")


def collision(a: str, b: str, t: float, restitution: float = 1.0) -> Event:
    """Build an IMPACT event between two participants."""
    raise NotImplementedError("M12 collision")
