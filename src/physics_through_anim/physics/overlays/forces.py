"""FBD overlays: component / system FBD + isolate (Milestone M9). Scaffold."""

from __future__ import annotations


def component_fbd(model, ref: str):
    raise NotImplementedError("M9 component_fbd")


def system_fbd(model, members: tuple[str, ...]):
    raise NotImplementedError("M9 system_fbd")


def isolate(model, members: tuple[str, ...]):
    """Fade everything else; suppress internal forces, show only external ones."""
    raise NotImplementedError("M9 isolate")
