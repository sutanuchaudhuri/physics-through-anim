"""Contact threshold classification + slack string (variable-length) behaviour."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.mechanics import (
    Assembly,
    Block,
    Floor,
    Particle,
    SlackString,
    contact_state,
)
from physics_through_anim.physics.mechanics.connectors import Rope
from physics_through_anim.physics.mechanics.geometry import TOUCH_TOL, Circle2D


def test_contact_state_bands() -> None:
    floor = Floor(y=0.0)
    assert contact_state(Circle2D(center=(0.0, 1.0), radius=0.5), floor) == "free"
    assert contact_state(Circle2D(center=(0.0, 0.5), radius=0.5), floor) == "touching"
    # a tiny overlap within the band still reads as touching, not penetrating
    near = Circle2D(center=(0.0, 0.5 - 0.5 * TOUCH_TOL), radius=0.5)
    deep = Circle2D(center=(0.0, 0.5 - 2.0 * TOUCH_TOL), radius=0.5)
    assert contact_state(near, floor) == "touching"
    assert contact_state(deep, floor) == "penetrating"


def test_assembly_tolerates_a_touch_within_the_band() -> None:
    a = Assembly()
    floor = Floor(y=0.0)
    a.add(floor)
    # a dot whose bottom dips slightly below the floor, within the contact band
    ball = Particle(name="ball", position=(0.0, 0.5 - 0.5 * TOUCH_TOL), radius=0.5)
    a.add(ball)  # must NOT raise -- this is contact, not penetration
    assert "ball.CM" in a.keypoints


def test_assembly_still_rejects_real_penetration() -> None:
    import pytest

    a = Assembly()
    a.add(Floor(y=0.0))
    with pytest.raises(ValueError, match="impenetrable"):
        a.add(Block(name="sunk", position=(0.0, -1.0), width=1.0))


# --- slack string ---------------------------------------------------------


def test_slack_string_sags_when_ends_are_close() -> None:
    s = SlackString(from_point=(-1.0, 0.0), to_point=(1.0, 0.0), rest_length=3.0)
    assert not s.is_taut()  # span 2 < rest 3
    lowest_y = float(s.mobject.submobjects[0].points[:, 1].min())
    assert lowest_y < -1e-3  # the curve droops below the chord


def test_slack_string_is_taut_when_stretched() -> None:
    s = SlackString(from_point=(-1.5, 0.0), to_point=(1.5, 0.0), rest_length=2.0)
    assert s.is_taut()  # span 3 >= rest 2 -> straight


def test_slack_string_transitions_on_set_endpoints() -> None:
    s = SlackString(from_point=(0.0, 0.0), to_point=(1.0, 0.0), rest_length=2.5)
    assert not s.is_taut()
    s.set_endpoints(np.array([-1.5, 0.0, 0.0]), np.array([1.5, 0.0, 0.0]))  # span 3 > rest
    assert s.is_taut()


def test_plain_rope_has_no_rest_length_and_is_always_taut() -> None:
    r = Rope(from_point=(0.0, 0.0), to_point=(0.0, -2.0))
    assert r.is_taut()
