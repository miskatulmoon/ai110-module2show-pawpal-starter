"""PawPal+ core system classes.

Skeleton generated from diagrams/uml.mmd. No scheduling logic yet —
methods are stubs to be implemented incrementally.
"""

from dataclasses import dataclass, field
from datetime import date, time, timedelta
from enum import Enum
from uuid import uuid4


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Recurrence(Enum):
    ONE_TIME = "one_time"
    DAILY = "daily"
    WEEKLY = "weekly"


def _minutes(t: time) -> int:
    """Minutes since midnight, for simple time-window arithmetic."""
    return t.hour * 60 + t.minute


def _time_from_minutes(total_minutes: int) -> time:
    return time(total_minutes // 60, total_minutes % 60)


def _parse_clock(value: str | None) -> time | None:
    """Parse a literal "HH:MM" string (e.g. a fixed meds time). Returns None for band names like "morning"."""
    if not value:
        return None
    try:
        hour_str, minute_str = value.split(":")
        return time(int(hour_str), int(minute_str))
    except ValueError:
        return None


PRIORITY_ORDER = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}

TIME_WINDOW_BANDS = {
    "morning": (time(6, 0), time(12, 0)),
    "afternoon": (time(12, 0), time(17, 0)),
    "evening": (time(17, 0), time(21, 0)),
}

SLOT_STEP_MINUTES = 5


@dataclass
class CareTask:
    title: str
    category: str
    duration_minutes: int
    priority: Priority = Priority.MEDIUM
    time_window: str | None = None
    recurrence: Recurrence = Recurrence.ONE_TIME
    is_flexible: bool = True
    completed: bool = False
    due_date: date | None = None
    id: str = field(default_factory=lambda: str(uuid4()))

    def conflicts_with(self, other: "CareTask") -> bool:
        """True if both tasks are fixed to the same non-flexible time window."""
        if self.time_window is None or other.time_window is None:
            return False
        if self.time_window != other.time_window:
            return False
        return not self.is_flexible and not other.is_flexible

    def fits_in_window(self, start: time, end: time) -> bool:
        """True if this task's duration fits between start and end."""
        return _minutes(end) - _minutes(start) >= self.duration_minutes

    def mark_done(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def create_next_occurrence(self, today: date) -> "CareTask | None":
        """Return a fresh, incomplete instance due the next occurrence after `today`: +1 day for
        daily tasks, +7 days for weekly tasks. Returns None if the task isn't recurring."""
        if self.recurrence == Recurrence.ONE_TIME:
            return None
        next_due = today + timedelta(days=1 if self.recurrence == Recurrence.DAILY else 7)
        return CareTask(
            title=self.title,
            category=self.category,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            time_window=self.time_window,
            recurrence=self.recurrence,
            is_flexible=self.is_flexible,
            due_date=next_due,
        )


@dataclass
class Pet:
    name: str
    species: str
    breed: str | None = None
    age: int | None = None
    notes: str | None = None
    tasks: list[CareTask] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid4()))

    def add_task(self, task: CareTask) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given id, if present."""
        self.tasks = [task for task in self.tasks if task.id != task_id]

    def get_tasks(self) -> list[CareTask]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)


@dataclass
class Owner:
    name: str
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def set_preference(self, key: str, value) -> None:
        """Set an owner scheduling preference by key."""
        self.preferences[key] = value

    def filter_tasks(self, completed: bool | None = None, pet_name: str | None = None) -> list[CareTask]:
        """Return tasks across pets, optionally filtered by completion status and/or pet name."""
        matched = []
        for pet in self.pets:
            if pet_name is not None and pet.name != pet_name:
                continue
            for task in pet.get_tasks():
                if completed is not None and task.completed != completed:
                    continue
                matched.append(task)
        return matched


@dataclass
class Constraints:
    available_minutes: int
    day_start: time
    day_end: time
    blackout_windows: list[tuple[time, time]] = field(default_factory=list)
    owner_prefs: dict = field(default_factory=dict)
    used_minutes: int = 0

    @classmethod
    def from_owner(cls, owner: "Owner", day_start: time, day_end: time, available_minutes: int) -> "Constraints":
        """Build a Constraints instance seeded with an owner's preferences."""
        return cls(
            available_minutes=available_minutes,
            day_start=day_start,
            day_end=day_end,
            owner_prefs=dict(owner.preferences),
        )

    def is_time_available(self, start: time, end: time) -> bool:
        """True if the given window is within the day and outside any blackout window."""
        if _minutes(start) < _minutes(self.day_start) or _minutes(end) > _minutes(self.day_end):
            return False
        for blackout_start, blackout_end in self.blackout_windows:
            if _minutes(start) < _minutes(blackout_end) and _minutes(end) > _minutes(blackout_start):
                return False
        return True

    def use_minutes(self, minutes: int) -> None:
        """Deduct minutes from the remaining budget, raising if not enough remain."""
        if minutes > self.remaining_minutes():
            raise ValueError(
                f"Not enough time remaining: requested {minutes}, only {self.remaining_minutes()} left"
            )
        self.used_minutes += minutes

    def remaining_minutes(self) -> int:
        """Minutes left in the available time budget."""
        return self.available_minutes - self.used_minutes


@dataclass
class ScheduledTask:
    task: CareTask
    start_time: time
    end_time: time
    reason: str = ""

    def overlaps_with(self, other: "ScheduledTask") -> bool:
        """True if this scheduled task's time range overlaps another's."""
        return _minutes(self.start_time) < _minutes(other.end_time) and _minutes(self.end_time) > _minutes(
            other.start_time
        )


@dataclass
class Plan:
    plan_date: date
    pet: Pet
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    skipped_tasks: list[CareTask] = field(default_factory=list)

    def add(self, scheduled_task: ScheduledTask) -> None:
        """Add a scheduled task to this plan."""
        self.scheduled_tasks.append(scheduled_task)

    def to_summary(self) -> str:
        """Render this plan as a human-readable, time-ordered summary."""
        lines = [f"Daily plan for {self.pet.name} ({self.pet.species}) — {self.plan_date.isoformat()}:"]

        ordered = sorted(self.scheduled_tasks, key=lambda st: _minutes(st.start_time))
        for scheduled in ordered:
            lines.append(
                f"  {scheduled.start_time.strftime('%H:%M')} — {scheduled.task.title} "
                f"({scheduled.task.duration_minutes} min) [priority: {scheduled.task.priority.value}]"
            )
            if scheduled.reason:
                lines.append(f"      reason: {scheduled.reason}")

        if self.skipped_tasks:
            lines.append("Skipped:")
            for task in self.skipped_tasks:
                lines.append(f"  - {task.title} ({task.duration_minutes} min)")

        return "\n".join(lines)

    def total_duration(self) -> int:
        """Total minutes occupied by all scheduled tasks in this plan."""
        return sum(_minutes(st.end_time) - _minutes(st.start_time) for st in self.scheduled_tasks)


@dataclass
class SchedulingConflict:
    pet_a: Pet
    scheduled_a: ScheduledTask
    pet_b: Pet
    scheduled_b: ScheduledTask

    def describe(self) -> str:
        """Human-readable summary of the two overlapping tasks."""
        a = self.scheduled_a
        b = self.scheduled_b
        return (
            f"{self.pet_a.name}'s '{a.task.title}' ({a.start_time.strftime('%H:%M')}-{a.end_time.strftime('%H:%M')}) "
            f"overlaps {self.pet_b.name}'s '{b.task.title}' ({b.start_time.strftime('%H:%M')}-{b.end_time.strftime('%H:%M')})"
        )


class Scheduler:
    """Pure scheduling logic — no UI, no I/O."""

    def __init__(self, strategy: str = "priority_then_duration"):
        """Create a scheduler using the given ordering strategy."""
        self.strategy = strategy
        self._explanations: dict[str, str] = {}

    def generate_plan(self, pet: Pet, constraints: Constraints, plan_date: date) -> Plan:
        """Build a full day plan for a pet's tasks under the given constraints."""
        self._explanations = {}
        plan = Plan(plan_date=plan_date, pet=pet)

        self._roll_over_recurring_tasks(pet, plan_date)

        active_tasks = [
            task
            for task in pet.get_tasks()
            if not task.completed and (task.due_date is None or task.due_date <= plan_date)
        ]
        prioritized = self.sort_by_priority(active_tasks)

        conflict_free = self.resolve_conflicts(prioritized)
        for task in prioritized:
            if task not in conflict_free:
                plan.skipped_tasks.append(task)
                self._explanations[task.id] = (
                    "Skipped: conflicts with a higher-priority fixed task in the same time window."
                )

        within_budget = self.filter_by_available_time(conflict_free, constraints)
        for task in conflict_free:
            if task not in within_budget:
                plan.skipped_tasks.append(task)
                self._explanations[task.id] = (
                    f"Skipped: not enough time left in the {constraints.available_minutes}-minute budget."
                )

        for task in within_budget:
            slot = self._find_slot(task, constraints, plan)
            if slot is None:
                plan.skipped_tasks.append(task)
                self._explanations[task.id] = "Skipped: no open slot found in its time window before day end."
                continue

            start, end = slot
            constraints.use_minutes(task.duration_minutes)
            reason = (
                f"Priority {task.priority.value}: scheduled at the earliest open slot "
                f"in its {task.time_window or 'any'} window."
            )
            plan.add(ScheduledTask(task=task, start_time=start, end_time=end, reason=reason))
            self._explanations[task.id] = reason

        return plan

    def find_conflicts(self, plans: list[Plan]) -> list[SchedulingConflict]:
        """Detect scheduled tasks that overlap in time, whether for the same pet or different
        pets — e.g. two pets each needing the owner's attention at 06:00."""
        entries = [(plan.pet, scheduled) for plan in plans for scheduled in plan.scheduled_tasks]
        conflicts = []
        for i, (pet_a, scheduled_a) in enumerate(entries):
            for pet_b, scheduled_b in entries[i + 1 :]:
                if scheduled_a.overlaps_with(scheduled_b):
                    conflicts.append(SchedulingConflict(pet_a, scheduled_a, pet_b, scheduled_b))
        return conflicts

    def check_for_conflicts(self, plans: list[Plan]) -> list[str]:
        """Lightweight, defensive wrapper around find_conflicts: returns ready-to-display
        warning strings instead of SchedulingConflict objects, and never raises — any
        unexpected error during the check is reported as a warning instead of crashing
        the program."""
        try:
            conflicts = self.find_conflicts(plans)
        except Exception as exc:
            return [f"Warning: could not check for scheduling conflicts ({exc})."]
        return [f"Warning: {conflict.describe()}" for conflict in conflicts]

    def _roll_over_recurring_tasks(self, pet: Pet, today: date) -> None:
        """Replace each completed daily/weekly task with a fresh instance due on its next occurrence."""
        for task in pet.get_tasks():
            if not task.completed:
                continue
            next_task = task.create_next_occurrence(today)
            if next_task is not None:
                pet.remove_task(task.id)
                pet.add_task(next_task)

    def sort_by_priority(self, tasks: list[CareTask]) -> list[CareTask]:
        """Order tasks by priority, then by shortest duration first."""
        return sorted(tasks, key=lambda task: (PRIORITY_ORDER[task.priority], task.duration_minutes))

    def filter_by_available_time(self, tasks: list[CareTask], constraints: Constraints) -> list[CareTask]:
        """Keep only as many tasks, in order, as fit within the remaining time budget."""
        kept = []
        running_total = 0
        for task in tasks:
            if running_total + task.duration_minutes <= constraints.remaining_minutes():
                kept.append(task)
                running_total += task.duration_minutes
        return kept

    def resolve_conflicts(self, tasks: list[CareTask]) -> list[CareTask]:
        """Assumes `tasks` is already priority-ordered; the earlier (higher-priority) task in any
        conflicting pair wins and the later one is dropped."""
        accepted: list[CareTask] = []
        for task in tasks:
            if any(task.conflicts_with(other) for other in accepted):
                continue
            accepted.append(task)
        return accepted

    def explain_choice(self, task: CareTask) -> str:
        """Return the human-readable reason a task was scheduled or skipped."""
        return self._explanations.get(
            task.id, "No explanation available (task was not part of the most recently generated plan)."
        )

    def _resolve_window(self, task: CareTask, constraints: Constraints) -> tuple[time, time, bool]:
        """Returns (search_start, search_end, single_slot). single_slot means the task has a fixed,
        non-negotiable start time and only that one slot should be tried."""
        literal = _parse_clock(task.time_window)
        if literal is not None:
            if not task.is_flexible:
                return literal, literal, True
            return literal, constraints.day_end, False

        band = TIME_WINDOW_BANDS.get(task.time_window)
        if band is None:
            return constraints.day_start, constraints.day_end, False

        band_start, band_end = band
        start = band_start if _minutes(band_start) > _minutes(constraints.day_start) else constraints.day_start
        end = band_end if _minutes(band_end) < _minutes(constraints.day_end) else constraints.day_end
        return start, end, False

    def _find_slot(self, task: CareTask, constraints: Constraints, plan: Plan) -> tuple[time, time] | None:
        """Find the earliest open, non-overlapping slot for a task within its window."""
        window_start, window_end, single_slot = self._resolve_window(task, constraints)
        bound_minutes = _minutes(constraints.day_end) if single_slot else _minutes(window_end)
        candidate_starts = (
            [_minutes(window_start)]
            if single_slot
            else range(_minutes(window_start), _minutes(window_end) + 1, SLOT_STEP_MINUTES)
        )

        for start_minutes in candidate_starts:
            end_minutes = start_minutes + task.duration_minutes
            if end_minutes > bound_minutes:
                break

            start = _time_from_minutes(start_minutes)
            end = _time_from_minutes(end_minutes)
            if not constraints.is_time_available(start, end):
                continue

            candidate = ScheduledTask(task=task, start_time=start, end_time=end)
            if any(candidate.overlaps_with(existing) for existing in plan.scheduled_tasks):
                continue

            return start, end

        return None
