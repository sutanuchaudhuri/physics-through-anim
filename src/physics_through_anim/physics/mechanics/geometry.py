"""Non-penetration geometry (Milestone M2).

Walls and floors are impenetrable boundaries: a body's geometry may never cross
to a wall's solid (inward) side. This module is pure geometry -- signed distance,
clearance, the two-wall corner seat, and a projection that clamps a penetrating
body back to tangency -- shared by assembly placement and rolling/trajectory
updates. It decides *where*, never forces.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from physics_through_anim.physics.core.pose import Pose2D, Vec2

EPS = 1e-6
TOUCH_TOL = 0.03  # contact band (world units): |clearance| <= TOUCH_TOL reads as "touching"


@dataclass(frozen=True)
class Circle2D:
    """A round body: centre + radius (disk, cylinder, ball)."""

    center: Vec2 = (0.0, 0.0)
    radius: float = 0.5


@dataclass(frozen=True)
class Polygon2D:
    """A polygonal body given by its world-space vertices."""

    vertices: tuple[Vec2, ...] = ()


def _wall_frame(wall) -> tuple[np.ndarray, np.ndarray]:
    """A surface point ``q`` and outward unit normal ``n`` for any wall."""
    q = np.asarray(wall.contact_at(0.5), dtype=float)
    n = np.asarray(wall.normal(), dtype=float)
    return q, n


def signed_distance(point: Vec2, wall) -> float:
    """``(p - q) . n`` -- positive on the wall's outward (free) side."""
    q, n = _wall_frame(wall)
    p = np.array([point[0], point[1], 0.0])
    return float(np.dot(p - q, n))


def clearance(shape, wall) -> float:
    """Gap between ``shape`` and ``wall``: >0 free, ~0 touching, <0 penetrating."""
    if isinstance(shape, Circle2D):
        return signed_distance(shape.center, wall) - shape.radius
    if isinstance(shape, Polygon2D):
        return min(signed_distance(v, wall) for v in shape.vertices)
    raise TypeError(f"clearance() needs a Circle2D or Polygon2D, got {type(shape).__name__}")


def contact_state(shape, wall, *, tol: float = TOUCH_TOL) -> str:
    """Classify a body against a wall: ``"free"`` / ``"touching"`` / ``"penetrating"``.

    A small tolerance band ``tol`` around tangency counts as *touching* (contact),
    so numerical/pixel-scale overlaps register as contact rather than penetration.
    """
    gap = clearance(shape, wall)
    if gap < -tol:
        return "penetrating"
    if gap <= tol:
        return "touching"
    return "free"


def penetrates(shape, wall, *, tol: float = TOUCH_TOL) -> bool:
    return clearance(shape, wall) < -tol


def touches(shape, wall, *, tol: float = TOUCH_TOL) -> bool:
    return abs(clearance(shape, wall)) <= tol


def corner_seat(radius: float, wall_a, wall_b) -> np.ndarray:
    """Centre of a circle of ``radius`` tangent to both walls (solve the 2x2)."""
    qa, na = _wall_frame(wall_a)
    qb, nb = _wall_frame(wall_b)
    a = np.array([na[:2], nb[:2]])
    rhs = np.array([radius + float(qa[:2] @ na[:2]), radius + float(qb[:2] @ nb[:2])])
    c = np.linalg.solve(a, rhs)
    return np.array([c[0], c[1], 0.0])


def seat_circle_on_surface(radius: float, wall, near: Vec2) -> tuple[np.ndarray, np.ndarray]:
    """Seat a circle of ``radius`` tangent to ``wall`` at the surface point nearest ``near``.

    Returns ``(centre, contact)``: the contact is the foot on the surface (clamped to
    the segment), the centre is that foot pushed out by ``radius`` along the normal --
    the tangency (``clearance == 0``) condition, so the body neither pierces nor floats.
    """
    surf = wall.surface()
    a = np.array([surf.a[0], surf.a[1], 0.0])
    b = np.array([surf.b[0], surf.b[1], 0.0])
    ab = b - a
    length_sq = float(ab @ ab)
    p = np.array([near[0], near[1], 0.0])
    t = 0.0 if length_sq == 0.0 else float((p - a) @ ab) / length_sq
    t = min(1.0, max(0.0, t))
    contact = a + t * ab
    n = np.asarray(wall.normal(), dtype=float)
    return contact + radius * n, contact



def project_circle_out(center: Vec2, radius: float, wall) -> np.ndarray:
    """Push a circle centre along ``+n`` to tangency if it penetrates ``wall``."""
    c = np.array([center[0], center[1], 0.0])
    gap = signed_distance((c[0], c[1]), wall) - radius
    if gap < 0.0:
        _, n = _wall_frame(wall)
        c = c - gap * n  # gap < 0 => moves along +n to clearance 0
    return c


def body_shape(body):
    """Best-effort collision shape for a mechanics asset (circle or polygon).

    Polygon corners are built from the edge-midpoint keypoints, so the shape is
    correct even when the body has been rotated (e.g. a block seated on a slope).
    """
    if hasattr(body, "radius"):
        cm = body.keypoint("CM")
        return Circle2D(center=(float(cm[0]), float(cm[1])), radius=float(body.radius))
    keys = ("CM", "left", "right", "top", "bottom")
    if all(k in getattr(body, "keypoints", {}) for k in keys):
        cm = body.keypoint("CM")
        left = body.keypoint("left") - cm
        right = body.keypoint("right") - cm
        top = body.keypoint("top") - cm
        bottom = body.keypoint("bottom") - cm
        corners = (bottom + left, bottom + right, top + right, top + left)
        return Polygon2D(vertices=tuple((float((cm + c)[0]), float((cm + c)[1])) for c in corners))
    cm = body.keypoint("CM")
    return Polygon2D(vertices=((float(cm[0]), float(cm[1])),))


def no_penetration_clamp(radius: float, walls):
    """A pose post-processor that keeps a round body of ``radius`` out of ``walls``."""

    def clamp(pose: Pose2D) -> Pose2D:
        c = np.array([pose.position[0], pose.position[1], 0.0])
        for wall in walls:
            c = project_circle_out((c[0], c[1]), radius, wall)
        return Pose2D(position=(float(c[0]), float(c[1])), angle=pose.angle)

    return clamp
