"""Tests for semantic value tokens (Size / Span / Beat / Dir)."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.mechanics.bodies import Block
from physics_through_anim.physics.mechanics.contact import ContactFrame
from physics_through_anim.physics.mechanics.supports import Floor
from physics_through_anim.physics.render.tokens import Beat, Dir, Size, Span


def test_size_is_a_float_value() -> None:
    assert Size.MEDIUM == 1.0
    assert float(Size.LARGE) == 1.4
    assert Size.SMALL < Size.LARGE  # comparable like plain floats


def test_span_and_beat_are_floats() -> None:
    assert Span.WIDE == 6.0
    assert Beat.QUICK == 0.3
    assert Beat.INSTANT < Beat.HOLD


def test_dir_is_a_unit_tuple() -> None:
    assert Dir.RIGHT == (1.0, 0.0)
    assert Dir.UP == (0.0, 1.0)
    assert np.isclose(np.hypot(*Dir.UP_RIGHT), 1.0)


def test_tokens_are_drop_in_for_asset_params() -> None:
    block = Block(width=Size.LARGE, label="m")  # token used as a width
    assert np.isclose(block.width, 1.4)
    floor = Floor(y=-2.0, half_width=Span.WIDE)  # token used as a half-width
    assert np.isclose(floor.half_width, 6.0)
    frame = ContactFrame(point=(0.0, 0.0), tangent=Dir.RIGHT, normal=Dir.UP)
    assert tuple(frame.tangent) == (1.0, 0.0) and tuple(frame.normal) == (0.0, 1.0)


def test_custom_values_still_accepted() -> None:
    assert np.isclose(Block(width=1.23).width, 1.23)  # the custom escape hatch
    assert np.isclose(Floor(y=-2.0, half_width=5.0).half_width, 5.0)
