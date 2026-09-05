from manim import FadeIn, FadeOut

from physics_through_anim.lessons.rod_slipping.common import (
    RodLessonScene,
    rod_at,
    table,
    trajectory,
)


class Scene40FullTelemetryReplay(RodLessonScene):
    """Scene 40 -- Full replay of the rod's rotation across all phases."""

    def construct(self) -> None:
        self.add_narration()
        banner = self.chapter_banner("VI", "Synthesis")
        self.play(FadeIn(banner))
        self.wait(1.2)
        self.play(FadeOut(banner))

        header = self.scene_header(
            "40", "The Whole Story, Replayed", "One continuous simulation, three phases"
        )
        self.play(FadeIn(header))

        traj = trajectory()
        floor = table(half_width=4.0)
        self.play(FadeIn(floor))

        import numpy as np

        sample_idx = np.linspace(0, len(traj.t) - 1, 24).astype(int)
        rod = rod_at(float(traj.theta[sample_idx[0]]))
        self.play(FadeIn(rod))
        for i in sample_idx[1:]:
            new_rod = rod_at(float(traj.theta[i]))
            self.play(rod.animate.become(new_rod), run_time=0.12)
        self.wait(1)
