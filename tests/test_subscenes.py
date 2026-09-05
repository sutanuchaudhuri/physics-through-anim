from manim import Dot, FadeIn, FadeOut

from physics_through_anim.subscenes import SubScene, default_anchors, play_subscenes


class FakeScene:
    """Records the animation/wait calls play_subscenes issues, without rendering."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def play(self, *anims, run_time=None) -> None:
        self.calls.append(("play", tuple(type(a).__name__ for a in anims)))

    def wait(self, duration) -> None:
        self.calls.append(("wait", round(float(duration), 3)))


def _subs(n: int) -> list[SubScene]:
    return [SubScene(build=lambda: Dot(), hold=1.0, name=f"s{i}") for i in range(n)]


def test_sequential_fades_each_in_holds_then_out() -> None:
    scene = FakeScene()
    play_subscenes(scene, _subs(2), mode="sequential")
    kinds = [c[0] for c in scene.calls]
    assert kinds == ["play", "wait", "play", "play", "wait", "play"]
    fade_anims = [c[1] for c in scene.calls if c[0] == "play"]
    assert fade_anims[0] == (FadeIn.__name__,)
    assert fade_anims[1] == (FadeOut.__name__,)


def test_sequential_keep_last_leaves_final_on_screen() -> None:
    scene = FakeScene()
    shown = play_subscenes(scene, _subs(2), mode="sequential", keep_last=True)
    # first sub fades in+out, last only fades in (no trailing FadeOut)
    assert [c[0] for c in scene.calls] == ["play", "wait", "play", "play", "wait"]
    assert len(shown) == 1


def test_together_fades_all_in_at_once() -> None:
    scene = FakeScene()
    play_subscenes(scene, _subs(3), mode="together", hold=2.0)
    assert [c[0] for c in scene.calls] == ["play", "wait", "play"]
    # a single play with three FadeIns, then one hold, then one play of three FadeOuts
    assert scene.calls[0][1] == (FadeIn.__name__, FadeIn.__name__, FadeIn.__name__)
    assert scene.calls[1] == ("wait", 2.0)
    assert scene.calls[2][1] == (FadeOut.__name__, FadeOut.__name__, FadeOut.__name__)


def test_together_fade_out_false_returns_mobjects() -> None:
    scene = FakeScene()
    shown = play_subscenes(scene, _subs(2), mode="together", fade_out=False)
    assert [c[0] for c in scene.calls] == ["play", "wait"]
    assert len(shown) == 2


def test_default_anchors_are_distinct_and_sized() -> None:
    for n in range(1, 7):
        anchors = default_anchors(n)
        assert len(anchors) == n
        as_tuples = {tuple(a) for a in anchors}
        assert len(as_tuples) == n  # no two sub-scenes share a center
