"""ProblemScenePlan: the declarative bridge (Milestone M17). Scaffold.

Typed, inspectable specs -- no dict-of-anything for physics quantities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

from physics_through_anim.physics.core.scene_data import VectorSpec
from physics_through_anim.physics.problems.refs import ProblemRef


class StepKind(StrEnum):
    """A block in a scene's timeline (what a renderer executes in order)."""

    INITIALIZE = "initialize"  # build/seat entities, set the opening state
    TIMESTEP = "timestep"  # advance the scene by ``dt`` (physics step / interpolate)
    SCENE_CHANGE = "scene_change"  # toggle relations, swap a view, or run a transition


class LabelPlacement(StrEnum):
    """Where a node's label sits relative to the node (or ``AUTO``)."""

    AUTO = "auto"
    CENTER = "center"
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"


@dataclass
class LabelSpec:
    """A node's label: whether to show it, where to place it, and optional overrides.

    ``at`` (explicit world coords) overrides ``placement``; ``text`` overrides the
    node's default label (its name).
    """

    show: bool = True
    placement: LabelPlacement = LabelPlacement.AUTO
    at: tuple[float, float] | None = None
    text: str = ""


@dataclass
class StyleSpec:
    """Per-entity render styling (honoured by every renderer).

    ``display``: ``solid`` | ``fade`` | ``dotted`` | ``dashed`` (outline/opacity).
    ``fill``:    ``solid`` | ``hashed`` | ``none`` (interior texture).
    ``show_corners``/``corner_labels`` mark a polygon body's corners; ``end_dots``
    marks a spring/rope/rod's end points.
    """

    display: str = "solid"
    fill: str = "solid"
    opacity: float | None = None
    show_corners: bool = False
    corner_labels: bool = False
    end_dots: bool = False


@dataclass
class PlacementSpec:
    """Relative placement -- prefer this over absolute ``position`` params.

    ``on`` seats this body on a support entity (a floor/incline/wall/table).
    Otherwise ``my`` keypoint is moved onto ``at`` (an ``asset.keypoint`` ref)
    plus ``offset`` -- e.g. hang a mass with ``at="pulley.left", my="top",
    offset=[0, -1.6]``.
    """

    on: str = ""
    at: str = ""
    my: str = "CM"
    offset: tuple[float, float] = (0.0, 0.0)


@dataclass
class EntitySpec:
    kind: str = ""
    name: str = ""
    params: dict[str, object] = field(default_factory=dict)
    style: StyleSpec = field(default_factory=StyleSpec)
    place: PlacementSpec | None = None
    label: LabelSpec = field(default_factory=LabelSpec)


@dataclass
class RelationSpec:
    kind: str = ""
    participants: tuple[str, ...] = ()
    params: dict[str, object] = field(default_factory=dict)


@dataclass
class TransformSpec:
    """A vector-driven motion applied to one entity during a timestep.

    ``translate`` shifts by ``(dx, dy)``; ``rotate_deg`` spins about ``about``
    (an ``asset.keypoint`` pivot ref, or the body's CM when empty).
    """

    target: str = ""
    translate: tuple[float, float] | None = None
    rotate_deg: float = 0.0
    about: str = ""


@dataclass
class StepSpec:
    """One timeline block: initialize, a timestep, or a scene change."""

    kind: StepKind = StepKind.TIMESTEP
    at: float = 0.0  # scene time this block starts (seconds)
    dt: float = 0.0  # duration/step size for TIMESTEP blocks
    label: str = ""
    transforms: list[TransformSpec] = field(default_factory=list)
    params: dict[str, object] = field(default_factory=dict)


@dataclass
class PhaseSpec:
    tag: str = ""
    t_start: float = 0.0
    t_end: float = 0.0


@dataclass
class MomentSpec:
    tag: str = ""
    t: float = 0.0


@dataclass
class OverlaySpec:
    kind: str = ""
    target: str = ""
    params: dict[str, object] = field(default_factory=dict)


@dataclass
class MarkerSpec:
    """A highlighted point (e.g. a pivot/hinge): an ``asset.keypoint`` ref or an
    explicit ``point``, drawn as a coloured dot with an optional label.

    Set ``show_label=False`` to draw the dot only (keeping the ``label`` text for
    documentation without cluttering the picture).
    """

    at: str = ""  # "asset.keypoint" ref (empty -> use ``point``)
    point: tuple[float, float] | None = None  # explicit world point
    label: str = ""
    color: str = "#ff4444"  # SVG colour (default red)
    show_label: bool = True
    placement: LabelPlacement = LabelPlacement.AUTO


@dataclass
class PathSpec:
    """A supplied polyline/trace to draw (e.g. a CM parabola). Points are world
    coordinates the caller has already computed -- the framework only renders.

    ``kind="parabola"`` generates an arch from ``points[0]`` to ``points[-1]``
    peaking ``height`` above the chord (illustrative, not necessarily to scale).
    """

    points: list[tuple[float, float]] = field(default_factory=list)
    color: str = "#ffd43b"
    label: str = ""
    closed: bool = False
    kind: str = "polyline"  # polyline | parabola
    height: float = 1.0  # parabola peak above the chord (world units)
    samples: int = 24


@dataclass
class MaskSpec:
    """A cosmetic, physics-free overlay (flame/plume/rocket body/ellipse/chain).

    Masks carry no physics -- they are pure decoration anchored to ``at`` (an
    ``asset.keypoint``) or an explicit ``point``, or drawn along ``points`` (chain,
    spring). Transparent by default; set ``opacity`` (0..1). ``direction`` orients
    directional masks (plume/flame). A ``spring``/``helix`` coil runs between its
    two ``points`` (the key ends), whose separation may change; it is massless.
    """

    kind: str = "plume"  # plume|flame|exhaust|rocket|ellipse|box|chain|spring|helix
    at: str = ""
    point: tuple[float, float] | None = None
    points: list[tuple[float, float]] = field(default_factory=list)  # path masks (chain/spring)
    length: float = 2.0
    width: float = 0.6
    direction: tuple[float, float] = (0.0, -1.0)
    color: str = "#ff922b"
    opacity: float = 0.4
    coils: int = 8  # loops for a spring/helix mask


@dataclass
class ProblemScenePlan:
    problem: ProblemRef = field(default_factory=ProblemRef)
    entities: list[EntitySpec] = field(default_factory=list)
    relations: list[RelationSpec] = field(default_factory=list)
    markers: list[MarkerSpec] = field(default_factory=list)
    vectors: list[VectorSpec] = field(default_factory=list)
    paths: list[PathSpec] = field(default_factory=list)
    masks: list[MaskSpec] = field(default_factory=list)
    steps: list[StepSpec] = field(default_factory=list)
    label_placement: LabelPlacement = LabelPlacement.AUTO  # default for every node
    phases: list[PhaseSpec] = field(default_factory=list)
    moments: dict[str, MomentSpec] = field(default_factory=dict)
    required_overlays: list[OverlaySpec] = field(default_factory=list)
    trajectory_provider: str | None = None
    learning_objectives: list[str] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)
    misconceptions: list[str] = field(default_factory=list)
