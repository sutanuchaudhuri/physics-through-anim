"""M5 catalogue -- every asset family builds and exposes its documented keypoints."""

from __future__ import annotations

import pytest

from physics_through_anim.physics.mechanics import (
    Block,
    Ceiling,
    Conveyor,
    Cylinder,
    Disk,
    Floor,
    Hinge,
    Incline,
    Pulley,
    Ring,
    Rod,
    Rope,
    Sphere2D,
    Wall,
)


@pytest.mark.parametrize(
    "asset, keys",
    [
        (Block(), ("CM", "top", "bottom", "left", "right")),
        (Disk(), ("CM", "top", "bottom", "left", "right")),
        (Ring(), ("CM", "top", "bottom")),
        (Sphere2D(), ("CM", "top", "bottom")),
        (Cylinder(), ("CM", "top", "bottom")),
        (Rod(), ("A", "B", "CM")),
        (Floor(), ("surface", "left", "right")),
        (Wall(), ("surface", "start", "end")),
        (Ceiling(), ("surface", "start", "end")),
        (Incline(), ("foot", "apex", "surface_mid")),
        (Conveyor(), ("surface", "left", "right")),
        (Pulley(), ("axle", "A", "B")),
        (Rope(from_point=(0.0, 0.0), to_point=(1.0, 0.0)), ("from", "to", "mid")),
        (Hinge(at=(0.0, 0.0)), ("H",)),
    ],
)
def test_asset_builds_and_exposes_keypoints(asset, keys) -> None:
    assert len(asset.mobject.submobjects) >= 1  # something was drawn
    for key in keys:
        asset.keypoint(key)  # raises if missing


def test_full_catalogue_assembles() -> None:
    from physics_through_anim.physics.mechanics import Assembly

    a = Assembly()
    floor = Floor(y=-2.0)
    a.add(floor)
    a.add(Block(position=(-3.0, 3.0), width=0.8), place_on=floor)
    a.add(Disk(radius=0.5, position=(0.0, 3.0)), place_on=floor)
    assert len(a.members) == 3
    assert len(a.mobject.submobjects) == 3
