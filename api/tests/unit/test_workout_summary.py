import uuid

from models.exercise import Exercise, ExerciseCategory
from models.set_log import SetLog
from workout_log.summary import workout_summary

BENCH_PRESS = uuid.uuid4()
ROWING = uuid.uuid4()


def _set(exercise_id: uuid.UUID, set_index: int, *, completed: bool = True, **kwargs) -> SetLog:
    return SetLog(exercise_id=exercise_id, set_index=set_index, completed=completed, **kwargs)


def _named(name: str, category: ExerciseCategory) -> Exercise:
    return Exercise(name=name, category=category)


def test_summary_without_sets():
    assert workout_summary([]) == "No sets were recorded for this workout."


def test_summary_groups_sets_by_exercise():
    bench = _named("Bench Press", ExerciseCategory.STRENGTH)
    rowing = _named("Rowing", ExerciseCategory.CARDIO)
    sets = [
        _set(BENCH_PRESS, 0, reps=10, weight=60.0, exercise=bench),
        _set(ROWING, 0, duration_seconds=600, distance_m=2000.0, exercise=rowing),
        _set(BENCH_PRESS, 1, reps=8, weight=65.0, exercise=bench),
    ]

    assert workout_summary(sets) == "Bench Press: 60kg × 10, 65kg × 8\nRowing: 10:00 / 2 km"


def test_summary_orders_sets_by_index():
    bench = _named("Bench Press", ExerciseCategory.STRENGTH)
    sets = [
        _set(BENCH_PRESS, 2, reps=6, weight=70.0, exercise=bench),
        _set(BENCH_PRESS, 0, reps=10, weight=60.0, exercise=bench),
        _set(BENCH_PRESS, 1, reps=8, weight=65.0, exercise=bench),
    ]

    assert workout_summary(sets) == "Bench Press: 60kg × 10, 65kg × 8, 70kg × 6"


def test_summary_falls_back_to_exercise_id_when_unnamed():
    sets = [_set(BENCH_PRESS, 0, reps=10, weight=60.0)]

    assert workout_summary(sets) == f"exercise {BENCH_PRESS}: 60kg × 10"


def test_summary_renders_partial_metrics():
    bench = _named("Bench Press", ExerciseCategory.STRENGTH)
    sets = [
        _set(BENCH_PRESS, 0, reps=12, exercise=bench),
        _set(BENCH_PRESS, 1, weight=40.0, exercise=bench),
        _set(BENCH_PRESS, 2, exercise=bench),
    ]

    assert workout_summary(sets) == "Bench Press: 12 reps, 40kg, logged, no metrics"


def test_summary_marks_incomplete_sets():
    bench = _named("Bench Press", ExerciseCategory.STRENGTH)
    sets = [_set(BENCH_PRESS, 0, reps=10, weight=60.0, completed=False, exercise=bench)]

    assert workout_summary(sets) == "Bench Press: 60kg × 10 (incomplete)"


def test_summary_formats_durations_over_an_hour():
    rowing = _named("Rowing", ExerciseCategory.CARDIO)
    sets = [_set(ROWING, 0, duration_seconds=3725, exercise=rowing)]

    assert workout_summary(sets) == "Rowing: 1:02:05"


def test_summary_trims_trailing_zeros_from_numbers():
    rowing = _named("Rowing", ExerciseCategory.CARDIO)
    sets = [_set(ROWING, 0, weight=62.5, reps=5, distance_m=1500.0, exercise=rowing)]

    assert workout_summary(sets) == "Rowing: 62.5kg × 5 / 1.5 km"
