"""Problem references (Milestone M17). Scaffold.

``mechanics/`` receives only a ``ProblemRef`` + resolved metadata; it never parses
source formats.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProblemRef:
    problem_id: str = ""  # stable id, e.g. "KRO-045"
    source_id: str = ""
    problem_number: str = ""
    source_title: str | None = None
    source_url: str | None = None
