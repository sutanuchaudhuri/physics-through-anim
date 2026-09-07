"""Rope wrapping a pulley: tangent contacts, arc/arch, spindle wrap."""

from __future__ import annotations

import numpy as np

from physics_through_anim.physics.mechanics.circular import Pulley
from physics_through_anim.physics.mechanics.connectors import RopeOverPulley


def _rope(**kw):
    return RopeOverPulley(center=(0.0, 2.0), radius=0.7,
                          from_point=(-2.5, -1.0), to_point=(2.5, -1.0), **kw)


def test_contacts_lie_on_the_rim() -> None:
    r = _rope()
    c = np.array([0.0, 2.0, 0.0])
    for key in ("contact_a", "contact_b"):
        assert abs(float(np.linalg.norm(r.keypoint(key) - c)) - 0.7) < 1e-9


def test_free_segments_are_tangent() -> None:
    r = _rope()
    c = np.array([0.0, 2.0, 0.0])
    for anchor, key in ((np.array([-2.5, -1.0, 0.0]), "contact_a"),
                        (np.array([2.5, -1.0, 0.0]), "contact_b")):
        t = r.keypoint(key)
        radial = t - c
        along = anchor - t
        assert abs(float(np.dot(radial, along))) < 1e-9  # tangent: radius perp to rope


def test_wrap_arch_bulges_above_the_anchors() -> None:
    r = _rope()
    # both anchors are below the pulley centre -> the wrap rides over the top
    assert r.keypoint("arc_mid")[1] > 2.0
    assert 0.0 < r.wrap_angle() < 2.0 * np.pi


def test_spindle_wrap_adds_turns_and_loops() -> None:
    single = _rope(turns=1)
    triple = _rope(turns=3)
    assert triple.wrap_angle() > single.wrap_angle() + 2.0 * np.pi - 1e-9
    assert len(triple.mobject.submobjects) > len(single.mobject.submobjects)


def test_rope_over_a_pulley_object() -> None:
    pulley = Pulley(center=(0.0, 2.0), radius=0.6)
    r = RopeOverPulley(pulley=pulley, from_point=(-2.0, -1.0), to_point=(2.0, -1.0))
    c = pulley.keypoint("axle")
    assert abs(float(np.linalg.norm(r.keypoint("contact_a") - c)) - 0.6) < 1e-9
