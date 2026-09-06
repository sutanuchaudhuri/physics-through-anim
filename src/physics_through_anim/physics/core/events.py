"""Events + phases (Milestone M7). Scaffold.

Events carry ``changes``/``payload`` (not full before/after states); before/after
derive from ``trajectory.state_at(t -/+ eps)``. ``EventKind`` stays small; named
occurrences use string ``tag``s.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum


class Phase(StrEnum):
    """Temporal phase around an event."""

    BEFORE = "before"
    DURING = "during"
    AFTER = "after"


class EventKind(StrEnum):
    """Core event taxonomy (named specifics go in ``Event.tag``)."""

    IMPACT = "impact"
    CONTACT_CHANGE = "contact_change"
    CONSTRAINT_CHANGE = "constraint_change"
    THRESHOLD = "threshold"
    TURNING_POINT = "turning_point"
    IMPULSE = "impulse"
    CUSTOM = "custom"


@dataclass(frozen=True)
class ConstraintChange:
    """Which relations an event activates/deactivates."""

    activate: tuple[str, ...] = ()
    deactivate: tuple[str, ...] = ()


@dataclass(frozen=True)
class Event:
    """An instant at which a relationship changes."""

    time: float = 0.0
    kind: EventKind = EventKind.CUSTOM
    participants: tuple[str, ...] = ()
    changes: ConstraintChange | None = None
    payload: Mapping = field(default_factory=dict)
    tag: str | None = None


@dataclass
class EventSequence:
    """An ordered list of events with cursor + query helpers."""

    events: list = field(default_factory=list)

    def add(self, event: Event) -> None:
        self.events.append(event)

    @property
    def count(self) -> int:
        return len(self.events)

    def sort_by_time(self) -> None:
        raise NotImplementedError("M7 EventSequence.sort_by_time")

    def at_or_before(self, t: float) -> Event | None:
        raise NotImplementedError("M7 EventSequence.at_or_before")


def phase_of(seq: EventSequence, t: float) -> Phase:
    """BEFORE the first event, DURING one, else AFTER."""
    raise NotImplementedError("M7 phase_of")
