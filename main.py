"""Demo entry point for PawPal+.

Builds an Owner with two Pets, gives each pet a few CareTasks (added out of
priority order), generates a schedule for the day, and prints it to the
terminal along with the sorted and filtered task views.
"""

from datetime import date, time, timedelta

from pawpal_system import (
    CareTask,
    Constraints,
    Owner,
    Pet,
    Priority,
    Recurrence,
    Scheduler,
)


def main() -> None:
    owner = Owner(name="Alex")

    dog = Pet(name="Biscuit", species="Dog", breed="Beagle", age=4)
    cat = Pet(name="Whiskers", species="Cat", breed="Tabby", age=2)
    owner.add_pet(dog)
    owner.add_pet(cat)

    # Tasks are added out of priority order on purpose, to prove sorting
    # doesn't depend on insertion order.
    dog.add_task(
        CareTask(
            title="Brush coat",
            category="grooming",
            duration_minutes=10,
            priority=Priority.LOW,
        )
    )
    dog.add_task(
        CareTask(
            title="Morning walk",
            category="exercise",
            duration_minutes=30,
            priority=Priority.HIGH,
            time_window="morning",
        )
    )
    dog.add_task(
        CareTask(
            title="Refill water bowl",
            category="feeding",
            duration_minutes=5,
            priority=Priority.MEDIUM,
            recurrence=Recurrence.DAILY,
        )
    )
    dog.add_task(
        CareTask(
            title="Give heartworm medicine",
            category="medication",
            duration_minutes=5,
            priority=Priority.HIGH,
            time_window="08:00",
            is_flexible=False,
        )
    )

    cat.add_task(
        CareTask(
            title="Evening feeding",
            category="feeding",
            duration_minutes=15,
            priority=Priority.MEDIUM,
            time_window="evening",
        )
    )
    cat.add_task(
        CareTask(
            title="Clean litter box",
            category="cleaning",
            duration_minutes=10,
            priority=Priority.HIGH,
        )
    )
    cat.add_task(
        CareTask(
            title="Play session",
            category="enrichment",
            duration_minutes=15,
            priority=Priority.LOW,
        )
    )
    # Deliberately fixed to the exact same time as the dog's "Give heartworm
    # medicine" task, so the schedule is guaranteed to contain a real
    # same-time conflict for the Scheduler to catch.
    cat.add_task(
        CareTask(
            title="Give cat medication",
            category="medication",
            duration_minutes=5,
            priority=Priority.HIGH,
            time_window="08:00",
            is_flexible=False,
        )
    )

    # Mark one task done ahead of time so the completion filter has
    # something to show below.
    dog.get_tasks()[0].mark_done()

    scheduler = Scheduler()
    today = date.today()

    print("Today's Schedule")
    print("=" * 40)

    todays_plans = []
    for pet in owner.pets:
        constraints = Constraints.from_owner(
            owner,
            day_start=time(6, 0),
            day_end=time(21, 0),
            available_minutes=120,
        )
        plan = scheduler.generate_plan(pet, constraints, today)
        todays_plans.append(plan)
        print(plan.to_summary())
        print()

    print("Cross-Pet Conflict Check")
    print("=" * 40)
    warnings = scheduler.check_for_conflicts(todays_plans)
    if warnings:
        for warning in warnings:
            print(f"  {warning}")
    else:
        print("  No overlapping tasks found.")

    same_time_conflict_detected = any(
        "Give heartworm medicine" in warning and "Give cat medication" in warning for warning in warnings
    )
    print(
        "  -> VERIFIED: Scheduler correctly detected the same-time conflict."
        if same_time_conflict_detected
        else "  -> FAILED: expected same-time conflict was NOT detected!"
    )
    print()

    print("Tasks Sorted by Priority")
    print("=" * 40)
    for pet in owner.pets:
        print(f"{pet.name}:")
        for task in scheduler.sort_by_priority(pet.get_tasks()):
            print(f"  [{task.priority.value:>6}] {task.title} ({task.duration_minutes} min)")
    print()

    print("Filtered Tasks")
    print("=" * 40)

    print("Completed tasks (all pets):")
    for task in owner.filter_tasks(completed=True):
        print(f"  - {task.title}")

    print("Incomplete tasks (all pets):")
    for task in owner.filter_tasks(completed=False):
        print(f"  - {task.title}")

    print(f"All tasks for {dog.name} only:")
    for task in owner.filter_tasks(pet_name=dog.name):
        print(f"  - {task.title}")

    print(f"Incomplete tasks for {cat.name} only:")
    for task in owner.filter_tasks(completed=False, pet_name=cat.name):
        print(f"  - {task.title}")
    print()

    print("Recurring Task Rollover Demo")
    print("=" * 40)
    water_bowl = next(task for task in dog.get_tasks() if task.title == "Refill water bowl")
    print(f"Marking '{water_bowl.title}' done (recurrence={water_bowl.recurrence.value}, id={water_bowl.id[:8]})")
    water_bowl.mark_done()

    # generate_plan automatically rolls completed daily/weekly tasks over into
    # a fresh, incomplete instance for their next occurrence.
    rollover_constraints = Constraints.from_owner(
        owner, day_start=time(6, 0), day_end=time(21, 0), available_minutes=120
    )
    scheduler.generate_plan(dog, rollover_constraints, today)

    print(f"{dog.name}'s tasks after rollover:")
    for task in dog.get_tasks():
        status = "done" if task.completed else "open"
        due = task.due_date.isoformat() if task.due_date else "n/a"
        print(f"  - {task.title} [{status}] due={due} (id={task.id[:8]})")

    print(f"\n{dog.name}'s plan for today (rolled-over task should be absent):")
    plan_today = scheduler.generate_plan(dog, rollover_constraints, today)
    print(", ".join(st.task.title for st in plan_today.scheduled_tasks) or "(none)")

    tomorrow = today + timedelta(days=1)
    tomorrow_constraints = Constraints.from_owner(
        owner, day_start=time(6, 0), day_end=time(21, 0), available_minutes=120
    )
    plan_tomorrow = scheduler.generate_plan(dog, tomorrow_constraints, tomorrow)
    print(f"{dog.name}'s plan for tomorrow ({tomorrow}) (rolled-over task should be present):")
    print(", ".join(st.task.title for st in plan_tomorrow.scheduled_tasks))


if __name__ == "__main__":
    main()
