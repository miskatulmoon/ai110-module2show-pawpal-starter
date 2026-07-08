"""PawPal+ core system classes.

Skeleton generated from diagrams/uml.mmd. No scheduling logic yet —
methods are stubs to be implemented incrementally.
"""

from dataclasses import dataclass, field
from datetime import date, time
from enum import Enum


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Recurrence(Enum):
    ONE_TIME = "one_time"
    DAILY = "daily"
    WEEKLY = "weekly"


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

    def conflicts_with(self, other: "CareTask") -> bool:
        raise NotImplementedError

    def fits_in_window(self, start: time, end: time) -> bool:
        raise NotImplementedError

    def mark_done(self) -> None:
        raise NotImplementedError


@dataclass
class Pet:
    name: str
    species: str
    breed: str | None = None
    age: int | None = None
    notes: str | None = None
    tasks: list[CareTask] = field(default_factory=list)

    def add_task(self, task: CareTask) -> None:
        raise NotImplementedError

    def remove_task(self, task_id: str) -> None:
        raise NotImplementedError

    def get_tasks(self) -> list[CareTask]:
        raise NotImplementedError


@dataclass
class Owner:
    name: str
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def set_preference(self, key: str, value) -> None:
        raise NotImplementedError


@dataclass
class Constraints:
    available_minutes: int
    day_start: time
    day_end: time
    blackout_windows: list[tuple[time, time]] = field(default_factory=list)
    owner_prefs: dict = field(default_factory=dict)

    def is_time_available(self, start: time, end: time) -> bool:
        raise NotImplementedError

    def remaining_minutes(self) -> int:
        raise NotImplementedError


@dataclass
class ScheduledTask:
    task: CareTask
    start_time: time
    end_time: time
    reason: str = ""

    def overlaps_with(self, other: "ScheduledTask") -> bool:
        raise NotImplementedError


@dataclass
class Plan:
    plan_date: date
    pet: Pet
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    skipped_tasks: list[CareTask] = field(default_factory=list)

    def add(self, scheduled_task: ScheduledTask) -> None:
        raise NotImplementedError

    def to_summary(self) -> str:
        raise NotImplementedError

    def total_duration(self) -> int:
        raise NotImplementedError


class Scheduler:
    """Pure scheduling logic — no UI, no I/O."""

    def __init__(self, strategy: str = "priority_then_duration"):
        self.strategy = strategy

    def generate_plan(self, tasks: list[CareTask], constraints: Constraints, pet: Pet, plan_date: date) -> Plan:
        raise NotImplementedError

    def sort_by_priority(self, tasks: list[CareTask]) -> list[CareTask]:
        raise NotImplementedError

    def filter_by_available_time(self, tasks: list[CareTask], constraints: Constraints) -> list[CareTask]:
        raise NotImplementedError

    def resolve_conflicts(self, tasks: list[CareTask]) -> list[CareTask]:
        raise NotImplementedError

    def explain_choice(self, task: CareTask) -> str:
        raise NotImplementedError
