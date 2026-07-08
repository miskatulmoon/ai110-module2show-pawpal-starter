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

## ✨ Features

- **Priority-based sorting** — orders tasks by priority tier (high → medium → low), then by shortest duration first, so urgent quick tasks land early in the day.
- **Time-window slot-finding** — searches each task's allowed window in 5-minute increments for the first open, non-overlapping slot; fixed-time tasks only try their exact literal time.
- **Time-budget filtering** — keeps only as many tasks, in priority order, as fit within the day's remaining available minutes.
- **Blackout window support** — respects owner-defined no-schedule windows (e.g. nap time) when searching for an open slot.
- **Same-window conflict resolution** — when two non-flexible tasks are pinned to the same fixed time or band, the lower-priority one is automatically dropped.
- **Cross-pet conflict detection** — compares every pair of scheduled tasks across one or more pets' plans and flags overlaps, even between different pets.
- **Conflict warnings** — safe, human-readable warning strings for any detected overlap; never raises, even on malformed input.
- **Daily & weekly recurrence** — completing a recurring task automatically spawns a fresh, incomplete instance due 1 or 7 days later instead of disappearing for good.
- **Task filtering/search** — query an owner's tasks across all pets by completion status and/or pet name.
- **Explainability** — every scheduled or skipped task comes with a plain-language reason via `explain_choice()`.
- **Chronological plan display** — the daily summary always reads in time order, regardless of the priority order tasks were scheduled in.

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

## 🎬 Demo Walkthrough

`main.py` builds an owner with two pets (a dog and a cat), each with a handful of care tasks — including two deliberately pinned to the same 08:00 slot so the conflict detector has something real to catch. Running it end-to-end demonstrates every algorithm in the [Features](#-features) list:

1. **Generate today's schedule** for each pet with `Scheduler.generate_plan()` — tasks are sorted by priority, filtered to fit the time budget, and slotted into their time windows.
2. **Check for cross-pet conflicts** with `check_for_conflicts()` — flags the two medication tasks fixed to the same 08:00 slot, plus the dog's 30-minute morning walk overlapping the cat's litter box and play session.
3. **Show priority sorting** directly via `sort_by_priority()`, independent of the order tasks were added.
4. **Filter tasks** by completion status and by pet using `Owner.filter_tasks()`.
5. **Mark a daily recurring task done** ("Refill water bowl") and regenerate the plan — the completed task rolls over into a fresh instance due the next day, absent from today's plan but present in tomorrow's.

Run it yourself with:

```bash
python main.py
```

Sample output:

```
Today's Schedule
========================================
Daily plan for Biscuit (Dog) — 2026-07-07:
  06:00 — Morning walk (30 min) [priority: high]
      reason: Priority high: scheduled at the earliest open slot in its morning window.
  06:30 — Refill water bowl (5 min) [priority: medium]
      reason: Priority medium: scheduled at the earliest open slot in its any window.
  08:00 — Give heartworm medicine (5 min) [priority: high]
      reason: Priority high: scheduled at the earliest open slot in its 08:00 window.

Daily plan for Whiskers (Cat) — 2026-07-07:
  06:00 — Clean litter box (10 min) [priority: high]
      reason: Priority high: scheduled at the earliest open slot in its any window.
  06:10 — Play session (15 min) [priority: low]
      reason: Priority low: scheduled at the earliest open slot in its any window.
  08:00 — Give cat medication (5 min) [priority: high]
      reason: Priority high: scheduled at the earliest open slot in its 08:00 window.
  17:00 — Evening feeding (15 min) [priority: medium]
      reason: Priority medium: scheduled at the earliest open slot in its evening window.

Cross-Pet Conflict Check
========================================
  Warning: Biscuit's 'Give heartworm medicine' (08:00-08:05) overlaps Whiskers's 'Give cat medication' (08:00-08:05)
  Warning: Biscuit's 'Morning walk' (06:00-06:30) overlaps Whiskers's 'Clean litter box' (06:00-06:10)
  Warning: Biscuit's 'Morning walk' (06:00-06:30) overlaps Whiskers's 'Play session' (06:10-06:25)
  -> VERIFIED: Scheduler correctly detected the same-time conflict.

Tasks Sorted by Priority
========================================
Biscuit:
  [  high] Give heartworm medicine (5 min)
  [  high] Morning walk (30 min)
  [medium] Refill water bowl (5 min)
  [   low] Brush coat (10 min)
Whiskers:
  [  high] Give cat medication (5 min)
  [  high] Clean litter box (10 min)
  [medium] Evening feeding (15 min)
  [   low] Play session (15 min)

Filtered Tasks
========================================
Completed tasks (all pets):
  - Brush coat
Incomplete tasks (all pets):
  - Morning walk
  - Refill water bowl
  - Give heartworm medicine
  - Evening feeding
  - Clean litter box
  - Play session
  - Give cat medication
All tasks for Biscuit only:
  - Brush coat
  - Morning walk
  - Refill water bowl
  - Give heartworm medicine
Incomplete tasks for Whiskers only:
  - Evening feeding
  - Clean litter box
  - Play session
  - Give cat medication

Recurring Task Rollover Demo
========================================
Marking 'Refill water bowl' done (recurrence=daily, id=a1409c88)
Biscuit's tasks after rollover:
  - Brush coat [done] due=n/a (id=07945f82)
  - Morning walk [open] due=n/a (id=d561f646)
  - Give heartworm medicine [open] due=n/a (id=7f50c3f5)
  - Refill water bowl [open] due=2026-07-08 (id=f4c21239)

Biscuit's plan for today (rolled-over task should be absent):
Give heartworm medicine, Morning walk
Biscuit's plan for tomorrow (2026-07-08) (rolled-over task should be present):
Give heartworm medicine, Morning walk, Refill water bowl
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
