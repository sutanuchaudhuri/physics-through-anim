"""Stress test: every committed example plan validates and renders to SVG."""

from __future__ import annotations

from pathlib import Path

import pytest

from physics_through_anim.physics.rendering import render_plan_file, validate_plan_file

_PLANS_DIR = Path(__file__).resolve().parents[1] / "examples" / "plans"
_PLANS = sorted(_PLANS_DIR.rglob("*.json"))


def test_there_are_example_plans() -> None:
    assert _PLANS, f"no example plans found under {_PLANS_DIR}"


@pytest.mark.parametrize("plan_path", _PLANS, ids=lambda p: p.stem)
def test_example_plan_is_valid(plan_path: Path) -> None:
    errors = validate_plan_file(plan_path)
    assert errors == [], "\n".join(str(e) for e in errors)


@pytest.mark.parametrize("plan_path", _PLANS, ids=lambda p: p.stem)
def test_example_plan_renders_svg(plan_path: Path, tmp_path: Path) -> None:
    out = render_plan_file(plan_path, renderer="svg", output=tmp_path / f"{plan_path.stem}.svg")
    assert out.read_text(encoding="utf-8").startswith("<svg")
