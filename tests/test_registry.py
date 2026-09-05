from physics_through_anim.registry import TOPICS


def test_course_contains_all_planned_topics() -> None:
    assert set(TOPICS) == {
        "vectors",
        "kinematics",
        "newtons_laws",
        "circular_motion",
        "momentum",
        "energy",
        "rotational_motion",
        "orbital_mechanics",
        "shm",
        "fluid_mechanics",
    }


def test_topics_have_distinct_scene_names() -> None:
    assert len({topic.scene_name for topic in TOPICS.values()}) == len(TOPICS)
