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
    """An ordered list of events with a cursor + query helpers."""

    events: list = field(default_factory=list)
    _cursor: int = 0

    def add(self, event: Event) -> None:
        self.events.append(event)

    @property
    def count(self) -> int:
        return len(self.events)

    def sort_by_time(self) -> None:
        self.events.sort(key=lambda e: e.time)

    def at_or_before(self, t: float) -> Event | None:
        """The last event with ``time <= t`` (``None`` before the first event)."""
        result = None
        for event in sorted(self.events, key=lambda e: e.time):
            if event.time <= t:
                result = event
            else:
                break
        return result

    @property
    def current(self) -> Event | None:
        return self.events[self._cursor] if 0 <= self._cursor < len(self.events) else None

    @property
    def next(self) -> Event | None:
        nxt = self._cursor + 1
        return self.events[nxt] if 0 <= nxt < len(self.events) else None

    def advance(self) -> Event | None:
        """Step the cursor to the next event and return it."""
        if self._cursor + 1 < len(self.events):
            self._cursor += 1
        return self.current


def phase_of(seq: EventSequence, t: float, *, during_eps: float = 1e-6) -> Phase:
    """BEFORE the first event, DURING one (within ``during_eps``), else AFTER."""
    if not seq.events:
        return Phase.BEFORE
    times = sorted(e.time for e in seq.events)
    if t < times[0] - during_eps:
        return Phase.BEFORE
    if any(abs(t - ti) <= during_eps for ti in times):
        return Phase.DURING
    return Phase.AFTER

