import sys
from datetime import date, time, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import CareTask, Constraints, Pet, Plan, Priority, Recurrence, ScheduledTask, Scheduler


def test_mark_done_changes_task_status():
    """Verify that calling mark_done() actually changes the task's status."""
    task = CareTask(title="Feed the cat", category="feeding", duration_minutes=10)

    assert task.completed is False

    task.mark_done()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet(name="Whiskers", species="cat")
    task = CareTask(title="Feed the cat", category="feeding", duration_minutes=10)

    assert len(pet.get_tasks()) == 0

    pet.add_task(task)

    assert len(pet.get_tasks()) == 1


def test_completed_recurring_task_rolls_over_into_new_instance():
    """Verify that completing a daily/weekly task spawns a fresh instance on the next generate_plan call."""
    pet = Pet(name="Whiskers", species="cat")
    task = CareTask(
        title="Feed the cat",
        category="feeding",
        duration_minutes=10,
        recurrence=Recurrence.DAILY,
    )
    pet.add_task(task)
    original_id = task.id

    task.mark_done()

    scheduler = Scheduler()
    constraints = Constraints(available_minutes=60, day_start=time(6, 0), day_end=time(21, 0))
    scheduler.generate_plan(pet, constraints, date(2026, 1, 1))

    tasks = pet.get_tasks()
    assert len(tasks) == 1
    assert tasks[0].id != original_id
    assert tasks[0].completed is False
    assert tasks[0].title == "Feed the cat"
    assert tasks[0].due_date == date(2026, 1, 2)


def test_daily_next_occurrence_is_due_one_day_later():
    """Verify create_next_occurrence sets due_date to exactly today + 1 day for daily tasks."""
    task = CareTask(
        title="Feed the cat",
        category="feeding",
        duration_minutes=10,
        recurrence=Recurrence.DAILY,
    )

    next_task = task.create_next_occurrence(date(2026, 1, 1))

    assert next_task.due_date == date(2026, 1, 2)


def test_weekly_next_occurrence_is_due_seven_days_later():
    """Verify create_next_occurrence sets due_date to exactly today + 7 days for weekly tasks."""
    task = CareTask(
        title="Grooming",
        category="grooming",
        duration_minutes=30,
        recurrence=Recurrence.WEEKLY,
    )

    next_task = task.create_next_occurrence(date(2026, 1, 1))

    assert next_task.due_date == date(2026, 1, 8)


def test_rolled_over_task_is_not_scheduled_until_its_due_date():
    """Verify a rolled-over daily task doesn't reappear in today's plan, only once its due date arrives."""
    pet = Pet(name="Whiskers", species="cat")
    task = CareTask(
        title="Feed the cat",
        category="feeding",
        duration_minutes=10,
        recurrence=Recurrence.DAILY,
    )
    pet.add_task(task)
    task.mark_done()

    scheduler = Scheduler()
    today = date(2026, 1, 1)
    constraints = Constraints(available_minutes=60, day_start=time(6, 0), day_end=time(21, 0))

    plan_today = scheduler.generate_plan(pet, constraints, today)
    assert plan_today.scheduled_tasks == []

    tomorrow_constraints = Constraints(available_minutes=60, day_start=time(6, 0), day_end=time(21, 0))
    plan_tomorrow = scheduler.generate_plan(pet, tomorrow_constraints, today + timedelta(days=1))
    assert len(plan_tomorrow.scheduled_tasks) == 1
    assert plan_tomorrow.scheduled_tasks[0].task.title == "Feed the cat"


def test_find_conflicts_detects_overlap_across_different_pets():
    """Verify find_conflicts flags two different pets' tasks scheduled at overlapping times."""
    dog = Pet(name="Biscuit", species="dog")
    cat = Pet(name="Whiskers", species="cat")
    dog.add_task(
        CareTask(
            title="Morning walk",
            category="exercise",
            duration_minutes=30,
            priority=Priority.HIGH,
            time_window="06:00",
            is_flexible=False,
        )
    )
    cat.add_task(
        CareTask(
            title="Clean litter box",
            category="cleaning",
            duration_minutes=10,
            priority=Priority.HIGH,
            time_window="06:00",
            is_flexible=False,
        )
    )

    scheduler = Scheduler()
    today = date(2026, 1, 1)
    dog_plan = scheduler.generate_plan(
        dog, Constraints(available_minutes=60, day_start=time(6, 0), day_end=time(21, 0)), today
    )
    cat_plan = scheduler.generate_plan(
        cat, Constraints(available_minutes=60, day_start=time(6, 0), day_end=time(21, 0)), today
    )

    conflicts = scheduler.find_conflicts([dog_plan, cat_plan])

    assert len(conflicts) == 1
    titles = {conflicts[0].scheduled_a.task.title, conflicts[0].scheduled_b.task.title}
    assert titles == {"Morning walk", "Clean litter box"}


def test_find_conflicts_ignores_non_overlapping_tasks():
    """Verify find_conflicts reports nothing when scheduled tasks don't share any time."""
    dog = Pet(name="Biscuit", species="dog")
    cat = Pet(name="Whiskers", species="cat")
    dog.add_task(
        CareTask(
            title="Morning walk",
            category="exercise",
            duration_minutes=30,
            time_window="06:00",
            is_flexible=False,
        )
    )
    cat.add_task(
        CareTask(
            title="Evening feeding",
            category="feeding",
            duration_minutes=15,
            time_window="17:00",
            is_flexible=False,
        )
    )

    scheduler = Scheduler()
    today = date(2026, 1, 1)
    dog_plan = scheduler.generate_plan(
        dog, Constraints(available_minutes=60, day_start=time(6, 0), day_end=time(21, 0)), today
    )
    cat_plan = scheduler.generate_plan(
        cat, Constraints(available_minutes=60, day_start=time(6, 0), day_end=time(21, 0)), today
    )

    assert scheduler.find_conflicts([dog_plan, cat_plan]) == []


def test_check_for_conflicts_returns_warning_strings():
    """Verify check_for_conflicts turns a real overlap into a human-readable warning message."""
    dog = Pet(name="Biscuit", species="dog")
    cat = Pet(name="Whiskers", species="cat")
    dog.add_task(
        CareTask(
            title="Morning walk",
            category="exercise",
            duration_minutes=30,
            time_window="06:00",
            is_flexible=False,
        )
    )
    cat.add_task(
        CareTask(
            title="Clean litter box",
            category="cleaning",
            duration_minutes=10,
            time_window="06:00",
            is_flexible=False,
        )
    )

    scheduler = Scheduler()
    today = date(2026, 1, 1)
    dog_plan = scheduler.generate_plan(
        dog, Constraints(available_minutes=60, day_start=time(6, 0), day_end=time(21, 0)), today
    )
    cat_plan = scheduler.generate_plan(
        cat, Constraints(available_minutes=60, day_start=time(6, 0), day_end=time(21, 0)), today
    )

    warnings = scheduler.check_for_conflicts([dog_plan, cat_plan])

    assert len(warnings) == 1
    assert warnings[0].startswith("Warning:")
    assert "Morning walk" in warnings[0]
    assert "Clean litter box" in warnings[0]


def test_check_for_conflicts_returns_empty_list_when_clear():
    """Verify check_for_conflicts returns an empty list, not None, when there's nothing to report."""
    scheduler = Scheduler()
    assert scheduler.check_for_conflicts([]) == []


def test_check_for_conflicts_never_raises_on_bad_input():
    """Verify check_for_conflicts reports a warning instead of crashing on malformed input."""
    scheduler = Scheduler()

    warnings = scheduler.check_for_conflicts(None)

    assert len(warnings) == 1
    assert warnings[0].startswith("Warning: could not check for scheduling conflicts")


def test_completed_one_time_task_does_not_roll_over():
    """Verify that a one-time task stays completed and isn't replaced on the next generate_plan call."""
    pet = Pet(name="Whiskers", species="cat")
    task = CareTask(title="Vet visit", category="health", duration_minutes=30)
    pet.add_task(task)
    original_id = task.id

    task.mark_done()

    scheduler = Scheduler()
    constraints = Constraints(available_minutes=60, day_start=time(6, 0), day_end=time(21, 0))
    scheduler.generate_plan(pet, constraints, date(2026, 1, 1))

    tasks = pet.get_tasks()
    assert len(tasks) == 1
    assert tasks[0].id == original_id
    assert tasks[0].completed is True


def test_late_completion_rolls_over_from_completion_date_not_original_due_date():
    """A weekly task due Jan 5 but not marked done until Jan 10 should roll over to
    Jan 17 (completion date + 7), not Jan 12 (original due date + 7)."""
    pet = Pet(name="Whiskers", species="cat")
    task = CareTask(
        title="Grooming",
        category="grooming",
        duration_minutes=30,
        recurrence=Recurrence.WEEKLY,
        due_date=date(2026, 1, 5),
    )
    pet.add_task(task)

    task.mark_done()

    scheduler = Scheduler()
    constraints = Constraints(available_minutes=60, day_start=time(6, 0), day_end=time(21, 0))
    scheduler.generate_plan(pet, constraints, date(2026, 1, 10))

    tasks = pet.get_tasks()
    assert len(tasks) == 1
    assert tasks[0].due_date == date(2026, 1, 17)


def test_same_band_non_flexible_tasks_conflict_even_with_room_for_both():
    """Two non-flexible tasks sharing the same time-window band (e.g. "morning") are
    currently treated as conflicting by conflicts_with, even though the band spans
    hours and both tasks would easily fit without overlapping."""
    pet = Pet(name="Whiskers", species="cat")
    high_priority = CareTask(
        title="Task A",
        category="feeding",
        duration_minutes=30,
        priority=Priority.HIGH,
        time_window="morning",
        is_flexible=False,
    )
    lower_priority = CareTask(
        title="Task B",
        category="feeding",
        duration_minutes=30,
        priority=Priority.MEDIUM,
        time_window="morning",
        is_flexible=False,
    )
    pet.add_task(high_priority)
    pet.add_task(lower_priority)

    scheduler = Scheduler()
    constraints = Constraints(available_minutes=120, day_start=time(6, 0), day_end=time(21, 0))
    plan = scheduler.generate_plan(pet, constraints, date(2026, 1, 1))

    assert len(plan.scheduled_tasks) == 1
    assert plan.scheduled_tasks[0].task.title == "Task A"
    assert lower_priority in plan.skipped_tasks
    assert "conflicts with a higher-priority" in scheduler.explain_choice(lower_priority)


def test_blackout_window_delays_flexible_task_to_next_open_slot():
    """A flexible task whose earliest candidate slot falls inside a blackout window
    should be pushed to the first slot after the blackout ends, not skipped."""
    pet = Pet(name="Whiskers", species="cat")
    task = CareTask(title="Playtime", category="exercise", duration_minutes=15)
    pet.add_task(task)

    scheduler = Scheduler()
    constraints = Constraints(
        available_minutes=60,
        day_start=time(6, 0),
        day_end=time(21, 0),
        blackout_windows=[(time(6, 0), time(6, 30))],
    )
    plan = scheduler.generate_plan(pet, constraints, date(2026, 1, 1))

    assert len(plan.scheduled_tasks) == 1
    assert plan.scheduled_tasks[0].start_time == time(6, 30)


def test_blackout_window_skips_fixed_task_entirely():
    """A non-flexible task whose only allowed start time falls inside a blackout
    window has no alternative slot to try and must be skipped."""
    pet = Pet(name="Whiskers", species="cat")
    task = CareTask(
        title="Medication",
        category="health",
        duration_minutes=10,
        time_window="06:00",
        is_flexible=False,
    )
    pet.add_task(task)

    scheduler = Scheduler()
    constraints = Constraints(
        available_minutes=60,
        day_start=time(6, 0),
        day_end=time(21, 0),
        blackout_windows=[(time(6, 0), time(6, 30))],
    )
    plan = scheduler.generate_plan(pet, constraints, date(2026, 1, 1))

    assert plan.scheduled_tasks == []
    assert task in plan.skipped_tasks
    assert "no open slot" in scheduler.explain_choice(task)


def test_to_summary_lists_tasks_in_chronological_order():
    """Tasks are scheduled internally in priority order (high, medium, low), but
    to_summary() must present them chronologically by start time regardless."""
    pet = Pet(name="Whiskers", species="cat")
    evening_high = CareTask(
        title="Evening High",
        category="feeding",
        duration_minutes=10,
        priority=Priority.HIGH,
        time_window="17:00",
        is_flexible=False,
    )
    midday_medium = CareTask(
        title="Midday Medium",
        category="feeding",
        duration_minutes=10,
        priority=Priority.MEDIUM,
        time_window="12:00",
        is_flexible=False,
    )
    morning_low = CareTask(
        title="Morning Low",
        category="feeding",
        duration_minutes=10,
        priority=Priority.LOW,
        time_window="06:00",
        is_flexible=False,
    )
    pet.add_task(evening_high)
    pet.add_task(midday_medium)
    pet.add_task(morning_low)

    scheduler = Scheduler()
    constraints = Constraints(available_minutes=60, day_start=time(6, 0), day_end=time(21, 0))
    plan = scheduler.generate_plan(pet, constraints, date(2026, 1, 1))

    # Internally, scheduled_tasks is in priority order (high, medium, low) — not chronological.
    assert [st.task.title for st in plan.scheduled_tasks] == [
        "Evening High",
        "Midday Medium",
        "Morning Low",
    ]

    # The rendered summary must reorder them chronologically by start time.
    summary = plan.to_summary()
    positions = {
        title: summary.index(title)
        for title in ("Morning Low", "Midday Medium", "Evening High")
    }
    assert positions["Morning Low"] < positions["Midday Medium"] < positions["Evening High"]


def test_find_conflicts_flags_duplicate_times_for_same_pet():
    """find_conflicts should flag two scheduled tasks with identical (duplicate)
    start/end times even when they belong to the same pet, not just across pets."""
    pet = Pet(name="Whiskers", species="cat")
    task_a = CareTask(title="Feed breakfast", category="feeding", duration_minutes=10)
    task_b = CareTask(title="Give medication", category="health", duration_minutes=10)

    plan = Plan(plan_date=date(2026, 1, 1), pet=pet)
    plan.add(ScheduledTask(task=task_a, start_time=time(6, 0), end_time=time(6, 10)))
    plan.add(ScheduledTask(task=task_b, start_time=time(6, 0), end_time=time(6, 10)))

    scheduler = Scheduler()
    conflicts = scheduler.find_conflicts([plan])

    assert len(conflicts) == 1
    titles = {conflicts[0].scheduled_a.task.title, conflicts[0].scheduled_b.task.title}
    assert titles == {"Feed breakfast", "Give medication"}
