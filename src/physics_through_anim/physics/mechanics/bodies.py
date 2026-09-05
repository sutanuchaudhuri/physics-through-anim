"""Rigid bodies for the mechanics asset library.

Milestone 1 ships ``Block`` (a rectangular mass, aliased ``RectangularMass``):
a centre-of-mass keypoint, edge keypoints, and an auto-declared weight force.
"""

from __future__ import annotations

from dataclasses import dataclass

from manim import BLUE, YELLOW, Dot, Rectangle, VGroup

from physics_through_anim.physics.mechanics.base import PhysicsAsset
from physics_through_anim.physics.mechanics.kinds import (
    BodyDynamics,
    ForceKind,
    MotionState,
)


@dataclass
class Block(PhysicsAsset):
    """A rectangular (or square) rigid mass with a centre-of-mass keypoint.

    Defaults give a unit-mass rectangle at the origin that already carries its
    own weight vector ``mg`` down from the CM. Supply only what differs.
    """

    name: str = "block"
    mass: float = 1.0
    position: tuple[float, float] = (0.0, 0.0)  # CM position in world coords
    width: float = 0.9
    height: float | None = None  # defaults to 0.6*width (rectangle) or width (square)
    shape: str = "rectangle"  # "rectangle" | "square"
    color: str | None = None
    fill_opacity: float = 0.3
    motion_state: MotionState = MotionState.AT_REST
    velocity: tuple[float, float] = (0.0, 0.0)
    show_cm: bool = True
    show_weight: bool = True
    label: str | None = "m"
    dynamics: BodyDynamics = BodyDynamics.DYNAMIC

    def __post_init__(self) -> None:
        if self.mass <= 0:
            raise ValueError(f"Block mass must be > 0, got {self.mass}")
        if self.shape not in ("rectangle", "square"):
            raise ValueError(f"shape must be 'rectangle' or 'square', got {self.shape!r}")
        super().__post_init__()

    @property
    def display_height(self) -> float:
        if self.height is not None:
            return self.height
        return self.width if self.shape == "square" else self.width * 0.6

    def build(self) -> VGroup:
        cx, cy = self.position
        color = self.color or BLUE
        rect = Rectangle(
            width=self.width,
            height=self.display_height,
            color=color,
            fill_color=color,
            fill_opacity=self.fill_opacity,
            stroke_width=5,
        ).move_to([cx, cy, 0.0])
        group = VGroup(rect)

        half_h = self.display_height / 2.0
        half_w = self.width / 2.0
        self.set_keypoint("CM", [cx, cy])
        self.set_keypoint("top", [cx, cy + half_h])
        self.set_keypoint("bottom", [cx, cy - half_h])
        self.set_keypoint("left", [cx - half_w, cy])
        self.set_keypoint("right", [cx + half_w, cy])

        if self.show_cm:
            group.add(Dot([cx, cy, 0.0], color=YELLOW, radius=0.06))
        if self.show_weight:
            self.add_force(ForceKind.WEIGHT, at="CM", label="mg", direction="down")
        return group


# The default rectangular mass is also exported under this clearer name.
RectangularMass = Block
