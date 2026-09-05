"""Chapter metadata for the Rod Slipping at a Table Edge lesson."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Chapter:
    number: str
    name: str


CHAPTERS: dict[str, Chapter] = {
    "0": Chapter("0", "The Physical Story"),
    "I": Chapter("I", "Setting Up the Fixed-Pivot Phase"),
    "II": Chapter("II", "Energy and Kinematics Before Slip"),
    "III": Chapter("III", "Finding the Slip Condition"),
    "IV": Chapter("IV", "Sliding, Reversal, and Loss of Contact"),
    "V": Chapter("V", "Free Flight and Ground Impact"),
    "VI": Chapter("VI", "Synthesis"),
}
