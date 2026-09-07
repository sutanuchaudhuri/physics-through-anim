"""State snapshots, timeline blocks, and the pluggable render engines (M17)."""

from __future__ import annotations

from pathlib import Path

import pytest

from physics_through_anim.physics.mechanics import Assembly, Block, Disk
from physics_through_anim.physics.problems.scene_plan import (
    EntitySpec,
    ProblemScenePlan,
    RelationSpec,
    StepKind,
    StepSpec,
)
from physics_through_anim.physics.rendering import (
    available_renderers,
    get_renderer,
    render_plan_file,
)
from physics_through_anim.physics.serialization import (
    from_json,
    from_xml,
    snapshot_assembly,
    to_json,
    to_xml,
)


def _plan() -> ProblemScenePlan:
    return ProblemScenePlan(
        entities=[
            EntitySpec(kind="block", name="m_1", params={"position": [-0.5, 0.4], "width": 0.8}),
            EntitySpec(kind="disk", name="d", params={"position": [1.5, 0.5], "radius": 0.5}),
        ],
        relations=[RelationSpec(kind="rolling", participants=("d", "m_1"),
                                params={"radius": 0.5, "name": "roll"})],
        steps=[
            StepSpec(kind=StepKind.INITIALIZE, at=0.0, label="seat"),
            StepSpec(kind=StepKind.TIMESTEP, at=0.0, dt=0.5, label="advance"),
            StepSpec(kind=StepKind.SCENE_CHANGE, at=2.0, params={"deactivate": ["roll"]}),
        ],
    )


def test_steps_round_trip_through_json_and_xml() -> None:
    plan = _plan()
    assert from_json(ProblemScenePlan, to_json(plan)) == plan
    assert from_xml(ProblemScenePlan, to_xml(plan, root="plan")) == plan


def test_snapshot_captures_live_keypoints() -> None:
    a = Assembly()
    a.add(Block(name="b", position=(1.0, 2.0), width=0.8))
    a.add(Disk(name="d", position=(-1.0, 0.5), radius=0.5))
    snap = snapshot_assembly(a, t=1.5)
    assert snap.t == 1.5
    by_name = {s.name: s for s in snap.assets}
    assert by_name["b"].keypoints["CM"] == (1.0, 2.0)
    assert by_name["d"].kind == "Disk"
    # Snapshots serialise (live geometry, distinct from the authoring spec).
    assert to_json(snap)


def test_snapshot_reflects_a_shift() -> None:
    a = Assembly()
    block = Block(name="b", position=(0.0, 0.0))
    a.add(block)
    block.shift((2.0, 0.0))
    snap = snapshot_assembly(a)
    assert snap.assets[0].keypoints["CM"] == (2.0, 0.0)


def test_all_engines_are_registered() -> None:
    assert available_renderers() == ["manim", "matplotlib", "plotly", "pymunk", "svg"]
    assert get_renderer("manim").kind == "video"
    assert get_renderer("svg").kind == "snapshot"


def test_svg_renderer_writes_a_real_svg(tmp_path: Path) -> None:
    plan_path = tmp_path / "scene.json"
    plan_path.write_text(to_json(_plan()), encoding="utf-8")
    out = render_plan_file(plan_path, renderer="svg", output=tmp_path / "scene.svg")
    text = out.read_text(encoding="utf-8")
    assert text.startswith("<svg")
    assert "<circle" in text  # the disk
    assert "<rect" in text  # background + the block
    assert ">d<" in text and ">m_1<" in text  # asset labels


def test_scaffolded_engines_raise_informative_errors(tmp_path: Path) -> None:
    plan_path = tmp_path / "scene.json"
    plan_path.write_text(to_json(_plan()), encoding="utf-8")
    for name in ("matplotlib", "plotly", "pymunk"):
        with pytest.raises(NotImplementedError):
            render_plan_file(plan_path, renderer=name, output=tmp_path / "x")


def test_unknown_renderer_and_format_are_rejected(tmp_path: Path) -> None:
    good = tmp_path / "s.json"
    good.write_text(to_json(_plan()), encoding="utf-8")
    with pytest.raises(KeyError):
        render_plan_file(good, renderer="nope")
    bad = tmp_path / "s.yaml"
    bad.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported plan format"):
        render_plan_file(bad, renderer="svg")


def test_markers_render_as_coloured_dots(tmp_path: Path) -> None:
    from physics_through_anim.physics.problems.scene_plan import MarkerSpec

    plan = _plan()
    plan.markers.append(MarkerSpec(point=(3.0, 0.0), label="pivot", color="#ff4444"))
    plan_path = tmp_path / "scene.json"
    plan_path.write_text(to_json(plan), encoding="utf-8")
    out = render_plan_file(plan_path, renderer="svg", output=tmp_path / "scene.svg")
    text = out.read_text(encoding="utf-8")
    assert 'fill="#ff4444"' in text
    assert ">pivot<" in text


def test_style_resolution_maps_display_and_fill() -> None:
    from physics_through_anim.physics.problems.scene_plan import StyleSpec
    from physics_through_anim.physics.rendering.style import resolve_style

    assert resolve_style(StyleSpec(display="fade")).stroke_opacity == 0.4
    assert resolve_style(StyleSpec(display="dotted")).dash == "2,3"
    assert resolve_style(StyleSpec(display="dashed")).dash == "7,5"
    assert resolve_style(StyleSpec(fill="hashed")).hashed is True
    assert resolve_style(StyleSpec(fill="none")).fill_opacity == 0.0
    assert resolve_style(StyleSpec(opacity=0.5)).stroke_opacity == 0.5


def test_svg_applies_entity_styles(tmp_path: Path) -> None:
    from physics_through_anim.physics.problems.scene_plan import (
        EntitySpec,
        ProblemScenePlan,
        StyleSpec,
    )

    plan = ProblemScenePlan(entities=[
        EntitySpec(kind="block", name="b", params={"position": [0.0, 0.0]},
                   style=StyleSpec(fill="hashed", show_corners=True, corner_labels=True)),
        EntitySpec(kind="disk", name="d", params={"position": [2.0, 0.0], "radius": 0.5},
                   style=StyleSpec(display="fade")),
    ])
    path = tmp_path / "s.json"
    path.write_text(to_json(plan), encoding="utf-8")
    text = render_plan_file(path, renderer="svg", output=tmp_path / "s.svg").read_text()
    assert "url(#hatch)" in text  # hashed block
    assert ">TL<" in text  # corner label
    assert 'stroke-opacity="0.4"' in text  # faded disk


def test_manim_group_builds_without_rendering() -> None:
    from manim import VGroup

    from physics_through_anim.physics.problems.scene_plan import MarkerSpec
    from physics_through_anim.physics.rendering.manim_style import build_manim_group

    plan = _plan()
    plan.markers.append(MarkerSpec(point=(0.0, 0.0), label="p"))
    group, assembly = build_manim_group(plan)
    assert isinstance(group, VGroup)
    # every assembly member plus the marker dot + its label are present.
    assert len(group.submobjects) >= len(assembly.members) + 1


def test_marker_show_label_toggles_the_text(tmp_path: Path) -> None:
    from physics_through_anim.physics.problems.scene_plan import (
        EntitySpec,
        MarkerSpec,
        ProblemScenePlan,
    )

    plan = ProblemScenePlan(
        entities=[EntitySpec(kind="disk", name="d", params={"radius": 0.5})],
        markers=[MarkerSpec(at="d.CM", label="hidden", color="#ff4444", show_label=False)],
    )
    path = tmp_path / "s.json"
    path.write_text(to_json(plan), encoding="utf-8")
    text = render_plan_file(path, renderer="svg", output=tmp_path / "s.svg").read_text()
    assert ">hidden<" not in text  # label suppressed
    assert 'fill="#ff4444"' in text  # dot still drawn


def test_masks_render_as_transparent_overlays(tmp_path: Path) -> None:
    from physics_through_anim.physics.problems.scene_plan import (
        EntitySpec,
        MaskSpec,
        ProblemScenePlan,
    )

    plan = ProblemScenePlan(
        entities=[EntitySpec(kind="particle", name="r", params={"position": [0.0, 0.8]})],
        masks=[
            MaskSpec(kind="rocket", at="r.CM", color="#adb5bd"),
            MaskSpec(kind="plume", point=(0.0, -0.1), opacity=0.3),
        ],
    )
    path = tmp_path / "s.json"
    path.write_text(to_json(plan), encoding="utf-8")
    text = render_plan_file(path, renderer="svg", output=tmp_path / "s.svg").read_text()
    assert "<polygon" in text  # mask shapes drawn
    assert 'fill-opacity="0.3"' in text  # transparency taken from JSON


def test_parabola_path_and_chain_mask_render(tmp_path: Path) -> None:
    from physics_through_anim.physics.problems.scene_plan import (
        EntitySpec,
        MaskSpec,
        PathSpec,
        ProblemScenePlan,
    )

    plan = ProblemScenePlan(
        entities=[EntitySpec(kind="particle", name="p", params={"position": [0.0, 0.0]})],
        paths=[PathSpec(kind="parabola", points=[(-2.0, 0.0), (2.0, 0.0)], height=1.5, samples=12)],
        masks=[MaskSpec(kind="chain", opacity=0.5,
                        points=[(-2.0, 1.0), (0.0, 0.0), (2.0, 1.0)])],
    )
    path = tmp_path / "s.json"
    path.write_text(to_json(plan), encoding="utf-8")
    text = render_plan_file(path, renderer="svg", output=tmp_path / "s.svg").read_text()
    # The parabola expands to many points (a smooth arch), not just the two endpoints.
    assert text.count(",") > 12
    assert "<ellipse" in text  # interlocked chain links
    assert 'stroke-opacity="0.9"' in text  # links read stronger than the flat ribbon


def test_spring_mask_renders_as_transparent_helix(tmp_path: Path) -> None:
    from physics_through_anim.physics.problems.scene_plan import (
        MaskSpec,
        ProblemScenePlan,
    )

    plan = ProblemScenePlan(
        masks=[MaskSpec(kind="spring", opacity=0.5, width=0.5, coils=6,
                        points=[(-2.0, 0.0), (1.0, 0.0)])],
    )
    path = tmp_path / "s.json"
    path.write_text(to_json(plan), encoding="utf-8")
    text = render_plan_file(path, renderer="svg", output=tmp_path / "s.svg").read_text()
    assert "<polyline" in text  # the coil is a sampled helix polyline
    assert 'stroke-opacity="0.5"' in text  # massless coil is transparent, from JSON
    assert text.count(",") > 24  # many samples => a smooth coil, not a straight line


def test_entity_label_placement_and_suppression(tmp_path: Path) -> None:
    from physics_through_anim.physics.problems.scene_plan import (
        EntitySpec,
        LabelPlacement,
        LabelSpec,
        ProblemScenePlan,
    )

    plan = ProblemScenePlan(entities=[
        EntitySpec(kind="disk", name="hidden", params={"position": [0.0, 0.0], "radius": 0.5},
                   label=LabelSpec(show=False)),
        EntitySpec(kind="disk", name="shown", params={"position": [3.0, 0.0], "radius": 0.5},
                   label=LabelSpec(placement=LabelPlacement.TOP, text="custom")),
    ])
    path = tmp_path / "s.json"
    path.write_text(to_json(plan), encoding="utf-8")
    text = render_plan_file(path, renderer="svg", output=tmp_path / "s.svg").read_text()
    assert ">hidden<" not in text  # suppressed label
    assert ">custom<" in text  # override text shown
    assert 'text-anchor="middle"' in text  # TOP placement centres the text


def test_vector_label_placement_and_plan_default(tmp_path: Path) -> None:
    from physics_through_anim.physics.core.scene_data import VectorSpec
    from physics_through_anim.physics.problems.scene_plan import (
        EntitySpec,
        LabelPlacement,
        ProblemScenePlan,
    )

    plan = ProblemScenePlan(
        label_placement=LabelPlacement.TOP,  # global default for every node
        entities=[EntitySpec(kind="disk", name="d",
                             params={"position": [0.0, 0.0], "radius": 0.5})],
        vectors=[
            VectorSpec(anchor="d.CM", vector=(1.0, 0.0), label="shown"),
            VectorSpec(anchor="d.top", vector=(1.0, 0.0), label="hidden", show_label=False),
        ],
    )
    path = tmp_path / "s.json"
    path.write_text(to_json(plan), encoding="utf-8")
    text = render_plan_file(path, renderer="svg", output=tmp_path / "s.svg").read_text()
    assert ">shown<" in text  # vector label drawn
    assert ">hidden<" not in text  # show_label=False suppresses it
    assert 'text-anchor="middle"' in text  # plan-default TOP placement applied to the disk label


def test_svg_shows_dotted_transform_ghosts(tmp_path: Path) -> None:
    from physics_through_anim.physics.problems.scene_plan import (
        EntitySpec,
        ProblemScenePlan,
        StepKind,
        StepSpec,
        TransformSpec,
    )

    plan = ProblemScenePlan(
        entities=[EntitySpec(kind="disk", name="d",
                             params={"position": [0.0, 0.0], "radius": 0.5})],
        steps=[StepSpec(kind=StepKind.TIMESTEP, dt=1.0,
                        transforms=[TransformSpec(target="d", translate=(2.0, 0.0))])],
    )
    path = tmp_path / "s.json"
    path.write_text(to_json(plan), encoding="utf-8")
    text = render_plan_file(path, renderer="svg", output=tmp_path / "s.svg").read_text()
    assert 'stroke-dasharray="2,3"' in text  # a dotted ghost frame


def test_transform_timeline_resolves_vector_driven_motions() -> None:
    from physics_through_anim.physics.problems.scene_plan import (
        EntitySpec,
        ProblemScenePlan,
        StepKind,
        StepSpec,
        TransformSpec,
    )
    from physics_through_anim.physics.rendering.manim_style import resolve_step_motions
    from physics_through_anim.physics.serialization.assembly_io import plan_to_assembly

    plan = ProblemScenePlan(
        entities=[
            EntitySpec(kind="edge", name="corner", params={"at": [1.0, 0.0]}),
            EntitySpec(kind="cylinder", name="c", params={"position": [1.0, 0.6], "radius": 0.6}),
        ],
        steps=[
            StepSpec(kind=StepKind.INITIALIZE, at=0.0),
            StepSpec(kind=StepKind.TIMESTEP, at=0.0, dt=1.5,
                     transforms=[TransformSpec(target="c", rotate_deg=-80.0, about="corner.E")]),
            StepSpec(kind=StepKind.TIMESTEP, at=1.5, dt=1.0,
                     transforms=[TransformSpec(target="c", translate=(0.5, -3.0))]),
        ],
    )
    timeline = resolve_step_motions(plan, plan_to_assembly(plan))
    assert timeline[0] == []  # initialize holds
    rotate = timeline[1][0]
    assert rotate.angle_rad != 0.0 and rotate.pivot is not None  # pivots about corner.E
    shift = timeline[2][0]
    assert shift.shift == (0.5, -3.0)



