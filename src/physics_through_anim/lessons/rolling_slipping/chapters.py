"""Chapter metadata for the Rolling, Slipping and Friction lesson."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chapter:
    number: str
    name: str


CHAPTERS: dict[str, Chapter] = {
    "0": Chapter("0", "Opening Hook"),
    "I": Chapter("I", "What Friction Really Does"),
    "II": Chapter("II", "From Sliding to Rolling"),
    "III": Chapter("III", "Where Friction Direction Really Comes From"),
    "IV": Chapter("IV", "Why Rotation Responds to Torque"),
    "V": Chapter("V", "Translation Plus Rotation"),
    "VI": Chapter("VI", "Translation and Rotation as Two Coupled Problems"),
    "Bonus": Chapter("Bonus", "Simulated with manim-physics"),
}
