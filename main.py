"""Demo entry point for PawPal+.

Builds an Owner with two Pets, gives each pet a few CareTasks, generates a
schedule for the day, and prints it to the terminal.
"""

from datetime import date, time

from pawpal_system import (
    CareTask,
    Constraints,
    Owner,
    Pet,
    Priority,
    Scheduler,
)


def main() -> None:
    owner = Owner(name="Alex")

    dog = Pet(name="Biscuit", species="Dog", breed="Beagle", age=4)
    cat = Pet(name="Whiskers", species="Cat", breed="Tabby", age=2)
    owner.add_pet(dog)
    owner.add_pet(cat)

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

    scheduler = Scheduler()
    today = date.today()

    print("Today's Schedule")
    print("=" * 40)

    for pet in owner.pets:
        constraints = Constraints.from_owner(
            owner,
            day_start=time(6, 0),
            day_end=time(21, 0),
            available_minutes=120,
        )
        plan = scheduler.generate_plan(pet, constraints, today)
        print(plan.to_summary())
        print()


if __name__ == "__main__":
    main()
