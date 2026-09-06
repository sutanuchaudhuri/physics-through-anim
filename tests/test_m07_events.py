"""TDD spec for M7 -- constraints + event model."""

from __future__ import annotations

import pytest

from physics_through_anim.physics.core.events import (
    ConstraintChange,
    Event,
    EventKind,
    EventSequence,
    Phase,
    phase_of,
)

TDD = pytest.mark.xfail(reason="M7 not implemented (TDD spec)", strict=False)


def test_event_kind_is_small_core() -> None:
    assert {k.value for k in EventKind} >= {"impact", "contact_change", "threshold"}
    assert {p.value for p in Phase} == {"before", "during", "after"}


def test_event_sequence_add_and_count() -> None:
    seq = EventSequence()
    seq.add(Event(time=1.0, kind=EventKind.IMPACT))
    assert seq.count == 1
    assert ConstraintChange(activate=("lock",)).deactivate == ()


@TDD
def test_at_or_before_and_sort() -> None:
    seq = EventSequence()
    seq.add(Event(time=2.0, kind=EventKind.IMPACT))
    seq.add(Event(time=1.0, kind=EventKind.THRESHOLD))
    seq.sort_by_time()
    assert seq.at_or_before(1.5).time == 1.0


@TDD
def test_phase_of() -> None:
    seq = EventSequence()
    seq.add(Event(time=1.0, kind=EventKind.IMPACT))
    assert phase_of(seq, 0.5) is Phase.BEFORE
