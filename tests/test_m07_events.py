"""M7 spec -- constraints + event model."""

from __future__ import annotations

from physics_through_anim.physics.core.events import (
    ConstraintChange,
    Event,
    EventKind,
    EventSequence,
    Phase,
    phase_of,
)


def test_event_kind_is_small_core() -> None:
    assert {k.value for k in EventKind} >= {"impact", "contact_change", "threshold"}
    assert {p.value for p in Phase} == {"before", "during", "after"}


def test_event_sequence_add_and_count() -> None:
    seq = EventSequence()
    seq.add(Event(time=1.0, kind=EventKind.IMPACT))
    assert seq.count == 1
    assert ConstraintChange(activate=("lock",)).deactivate == ()


def test_at_or_before_and_sort() -> None:
    seq = EventSequence()
    seq.add(Event(time=2.0, kind=EventKind.IMPACT))
    seq.add(Event(time=1.0, kind=EventKind.THRESHOLD))
    seq.sort_by_time()
    assert seq.at_or_before(1.5).time == 1.0
    assert seq.at_or_before(0.5) is None  # before the first event


def test_cursor_current_next_advance() -> None:
    seq = EventSequence()
    seq.add(Event(time=1.0, kind=EventKind.IMPACT, tag="first"))
    seq.add(Event(time=2.0, kind=EventKind.THRESHOLD, tag="second"))
    assert seq.current.tag == "first"
    assert seq.next.tag == "second"
    assert seq.advance().tag == "second"
    assert seq.next is None


def test_phase_of() -> None:
    seq = EventSequence()
    seq.add(Event(time=1.0, kind=EventKind.IMPACT))
    assert phase_of(seq, 0.5) is Phase.BEFORE
    assert phase_of(seq, 1.0) is Phase.DURING
    assert phase_of(seq, 1.5) is Phase.AFTER

