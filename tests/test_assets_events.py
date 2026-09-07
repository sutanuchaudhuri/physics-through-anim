"""M7 asset integration -- relations, constraint toggling, contact lifecycle."""

from __future__ import annotations

from physics_through_anim.physics.core.events import (
    ConstraintChange,
    Event,
    EventKind,
)
from physics_through_anim.physics.mechanics import Assembly, Block, Floor
from physics_through_anim.physics.mechanics.constraints import PinConstraint
from physics_through_anim.physics.mechanics.contact import (
    Contact,
    ContactLifecycle,
)
from physics_through_anim.physics.mechanics.kinds import ForceKind


def test_add_relation_stores_contacts_and_constraints_separately() -> None:
    a = Assembly()
    a.add_relation(Contact(body="block", surface="floor"))
    a.add_relation(PinConstraint(participants=("rod", "wall")), name="pin")
    assert len(a.contacts) == 1
    assert len(a.constraints) == 1
    assert "pin" in a.constraints_by_name


def test_constraint_toggles_off_at_a_release_event() -> None:
    a = Assembly()
    a.add_relation(PinConstraint(participants=("block", "floor")), name="on_floor")
    a.timeline.add(
        Event(time=1.0, kind=EventKind.CONSTRAINT_CHANGE,
              changes=ConstraintChange(deactivate=("on_floor",)))
    )
    a.at(0.5)
    assert a.constraints_by_name["on_floor"].active is True  # before the release
    a.at(1.5)
    assert a.constraints_by_name["on_floor"].active is False  # released


def test_contact_transition_and_separation_removes_normal_force() -> None:
    block = Block(position=(0.0, 0.0), width=0.8)
    block.add_force(ForceKind.NORMAL, at="CM", label="N", direction="up")
    contact = Contact(body="block", surface="floor")
    contact.transition_to(ContactLifecycle.ESTABLISHING)
    assert contact.lifecycle is ContactLifecycle.ESTABLISHING
    contact.on_separation(block, normal_label="N")
    assert contact.lifecycle is ContactLifecycle.SEPARATING
    assert not any(f.label == "N" for f in block.forces)  # N faded at separation


def test_assembly_timeline_is_queryable() -> None:
    a = Assembly()
    a.add(Floor(y=-2.0))
    a.timeline.add(Event(time=2.0, kind=EventKind.IMPACT))
    a.timeline.add(Event(time=1.0, kind=EventKind.CONTACT_CHANGE))
    a.timeline.sort_by_time()
    assert a.timeline.at_or_before(1.5).kind is EventKind.CONTACT_CHANGE
