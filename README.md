# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Daily plan for Biscuit (Dog) — 2026-07-07:
  06:00 — Morning walk (30 min) [priority: high]
      reason: Priority high: scheduled at the earliest open slot in its morning window.
  08:00 — Give heartworm medicine (5 min) [priority: high]
      reason: Priority high: scheduled at the earliest open slot in its 08:00 window.

Daily plan for Whiskers (Cat) — 2026-07-07:
  17:00 — Evening feeding (15 min) [priority: medium]
      reason: Priority medium: scheduled at the earliest open slot in its evening window.
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
18 passed in 0.03s 
```

**Confidence Level: ⭐⭐⭐⭐☆ (4/5)**

All 18 tests pass, covering the core contracts (task completion, recurrence rollover, priority sorting, time-budget filtering, conflict detection, and chronological display order) as well as edge cases like blackout windows and same-pet duplicate-time conflicts. Confidence isn't a full 5/5 because testing surfaced two behaviors that are technically consistent but not obviously *correct*, and haven't been confirmed as intentional:

- Recurring task rollover schedules the next occurrence relative to the *completion* date, not the original `due_date` — a late completion pushes the next occurrence later than expected.
- Two non-flexible tasks sharing the same time-*band* (e.g. both `"morning"`) are flagged as conflicting even when the band has hours of room for both, since `conflicts_with()` doesn't distinguish bands from literal fixed times.

Both are pinned down by tests (`test_late_completion_rolls_over_from_completion_date_not_original_due_date`, `test_same_band_non_flexible_tasks_conflict_even_with_room_for_both`) so any future fix will show up as an intentional, visible test change rather than a silent regression.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Priority-based sorting | `Scheduler.sort_by_priority()` | Orders tasks by priority tier first, then shortest duration, so urgent short tasks land early. |
| Time-budget filtering | `Scheduler.filter_by_available_time()` | Greedily keeps tasks, in priority order, that still fit within the day's remaining minutes. |
| Same-window conflict resolution | `CareTask.conflicts_with()`, `Scheduler.resolve_conflicts()` | When two fixed-time tasks are pinned to the same window, the lower-priority one is dropped. |
| Slot-finding | `Scheduler._find_slot()`, `Scheduler._resolve_window()` | Searches a task's time window in 5-minute steps for the first open, non-overlapping slot; fixed tasks only try their exact literal time. |
| Cross-pet conflict detection | `Scheduler.find_conflicts()` | Compares every pair of scheduled tasks across one or more pets' plans and flags any that overlap — even tasks belonging to different pets that the owner can't do at once. |
| Safe conflict warnings | `Scheduler.check_for_conflicts()` | Defensive wrapper around `find_conflicts()` that returns printable warning strings and never raises, even on bad input. |
| Recurring task rollover | `CareTask.create_next_occurrence()`, `Scheduler._roll_over_recurring_tasks()` | Completing a daily/weekly task automatically spawns a fresh, incomplete instance due +1 day (daily) or +7 days (weekly) later, instead of disappearing forever. |
| Task filtering/search | `Owner.filter_tasks()` | Query tasks across all of an owner's pets by completion status and/or pet name. |
| Explainability | `Scheduler.explain_choice()` | Returns the human-readable reason a specific task was scheduled or skipped. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
