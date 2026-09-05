from __future__ import annotations

from manim import (
    BLUE,
    DOWN,
    GREEN,
    ORANGE,
    RIGHT,
    UP,
    Arrow,
    DashedLine,
    MathTex,
    Text,
    VGroup,
)


def lesson_title(title: str, subtitle: str) -> VGroup:
    heading = Text(title, font_size=40, weight="BOLD")
    subheading = Text(subtitle, font_size=22, color=ORANGE)
    subheading.next_to(heading, DOWN, buff=0.2)
    return VGroup(heading, subheading).to_edge(UP)


def axis_labels(x_label: str = "x", y_label: str = "y") -> VGroup:
    return VGroup(
        MathTex(x_label, color=BLUE).next_to(RIGHT * 3.2, RIGHT),
        MathTex(y_label, color=GREEN).next_to(UP * 2.2, UP),
    )


def vector_arrow(start, end, label: str, color=BLUE) -> VGroup:
    arrow = Arrow(start, end, buff=0, color=color, stroke_width=6)
    text = MathTex(label, color=color).next_to(arrow, UP, buff=0.15)
    return VGroup(arrow, text)


def dashed_resultant(start, end) -> DashedLine:
    return DashedLine(start, end, color=ORANGE, stroke_width=5)
