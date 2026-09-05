from manim import DEGREES, Circle, Sphere, ThreeDAxes

from physics_through_anim.threed import (
    ISO_PHI,
    ISO_THETA,
    TOP_DOWN_PHI,
    ThreeDLessonScene,
    lift_to_3d,
    physics_axes_3d,
)


class FakeThreeDScene:
    """Records camera moves / transforms lift_to_3d issues, without rendering."""

    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def move_camera(self, phi=None, theta=None, added_anims=None, run_time=None) -> None:
        anim_names = tuple(type(a).__name__ for a in added_anims or ())
        self.calls.append(("move_camera", phi, theta, anim_names))

    def log_event(self, label, **fields) -> None:
        self.calls.append(("log", label))


def test_physics_axes_3d_builds_threedaxes() -> None:
    axes = physics_axes_3d()
    assert isinstance(axes, ThreeDAxes)


def test_lift_to_3d_moves_camera_and_transforms() -> None:
    scene = FakeThreeDScene()
    flat, solid = Circle(), Sphere()
    returned = lift_to_3d(scene, flat, solid)
    assert returned is solid
    move = [c for c in scene.calls if c[0] == "move_camera"]
    assert len(move) == 1
    _, phi, theta, anims = move[0]
    assert phi == ISO_PHI * DEGREES
    assert theta == ISO_THETA * DEGREES
    assert anims == ("ReplacementTransform",)
    assert ("log", "lift_to_3d") in scene.calls


def test_angle_constants_are_sane() -> None:
    assert TOP_DOWN_PHI == 0.0
    assert 0 < ISO_PHI < 90


def test_base_class_sets_lesson_name_default() -> None:
    assert ThreeDLessonScene.LESSON_NAME == "unknown_lesson"
    # convenience camera/HUD helpers exist for scene authors
    helpers = ("standard_view", "top_down_view", "orbit", "stop_orbit", "hud", "play_subscenes")
    for method in helpers:
        assert callable(getattr(ThreeDLessonScene, method))
