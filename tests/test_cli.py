"""CLI smoke tests for the plan/mask helper subcommands (Milestone M17)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import main  # noqa: E402


def test_list_masks_includes_the_new_masks(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["list-masks"]) == 0
    out = capsys.readouterr().out
    for kind in ("spring", "sand", "belt", "hopper", "chain", "box"):
        assert kind in out


def test_list_renderers_reports_svg_and_manim(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["list-renderers"]) == 0
    out = capsys.readouterr().out
    assert "svg" in out
    assert "manim" in out


def test_new_plan_scaffolds_a_valid_plan(tmp_path: Path) -> None:
    from physics_through_anim.physics.rendering import validate_plan_file

    plan = tmp_path / "scaffold.json"
    assert main(["new-plan", str(plan), "--mask", "spring", "--kind", "disk"]) == 0
    assert plan.exists()
    assert validate_plan_file(plan) == []


def test_new_plan_rejects_an_unknown_mask(tmp_path: Path) -> None:
    plan = tmp_path / "bad.json"
    assert main(["new-plan", str(plan), "--mask", "not_a_mask"]) == 1
    assert not plan.exists()


def test_render_gallery_batch_renders_a_directory(tmp_path: Path) -> None:
    src = tmp_path / "plans"
    src.mkdir()
    assert main(["new-plan", str(src / "one.json"), "--mask", "plume"]) == 0
    out = tmp_path / "svg"
    assert main(["render-gallery", str(src), "--renderer", "svg", "--output-dir", str(out)]) == 0
    assert (out / "one.svg").exists()
