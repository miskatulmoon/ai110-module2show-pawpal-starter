from datetime import date, time

import streamlit as st
from pawpal_system import (
    CareTask,
    Constraints,
    Owner,
    Pet,
    Priority,
    Scheduler,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)
    st.session_state.pet = Pet(name=pet_name, species=species)
    st.session_state.owner.add_pet(st.session_state.pet)

owner: Owner = st.session_state.owner
pet: Pet = st.session_state.pet
owner.name = owner_name
pet.name = pet_name
pet.species = species

scheduler = Scheduler()

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    time_window_label = st.selectbox("Time window", ["any", "morning", "afternoon", "evening"])
with col5:
    is_flexible = not st.checkbox("Fixed time (can't be moved)")

if st.button("Add task"):
    pet.add_task(
        CareTask(
            title=task_title,
            category="general",
            duration_minutes=int(duration),
            priority=Priority(priority_label),
            time_window=None if time_window_label == "any" else time_window_label,
            is_flexible=is_flexible,
        )
    )

tasks = scheduler.sort_by_priority(pet.get_tasks())
if tasks:
    st.write("Current tasks (sorted by priority, then shortest duration):")
    header = st.columns([3, 2, 2, 2, 2, 2])
    for col, label in zip(header, ["Title", "Duration", "Priority", "Window", "Flexible", "Status"]):
        col.markdown(f"**{label}**")
    for task in tasks:
        row = st.columns([3, 2, 2, 2, 2, 2])
        row[0].write(task.title)
        row[1].write(f"{task.duration_minutes} min")
        row[2].write(task.priority.value)
        row[3].write(task.time_window or "any")
        row[4].write("yes" if task.is_flexible else "no")
        if task.completed:
            row[5].write("✅ Done")
        elif row[5].button("Mark complete", key=f"complete_{task.id}"):
            task.mark_done()
            st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Runs the Scheduler against the tasks above and shows the resulting plan.")

col6, col7, col8 = st.columns(3)
with col6:
    day_start = st.time_input("Day start", value=time(7, 0))
with col7:
    day_end = st.time_input("Day end", value=time(21, 0))
with col8:
    available_minutes = st.number_input("Available minutes", min_value=1, value=240)

if st.button("Generate schedule"):
    constraints = Constraints.from_owner(
        owner, day_start=day_start, day_end=day_end, available_minutes=int(available_minutes)
    )
    plan = scheduler.generate_plan(pet, constraints, date.today())

    if plan.scheduled_tasks:
        st.success(f"Scheduled {len(plan.scheduled_tasks)} task(s) for {pet.name} on {plan.plan_date.isoformat()}.")
        chronological = sorted(plan.scheduled_tasks, key=lambda st_: st_.start_time)
        st.table(
            [
                {
                    "start": scheduled.start_time.strftime("%H:%M"),
                    "end": scheduled.end_time.strftime("%H:%M"),
                    "title": scheduled.task.title,
                    "priority": scheduled.task.priority.value,
                    "duration_minutes": scheduled.task.duration_minutes,
                }
                for scheduled in chronological
            ]
        )
    else:
        st.warning("No tasks could be scheduled with the current constraints.")

    if plan.skipped_tasks:
        st.warning(f"{len(plan.skipped_tasks)} task(s) were skipped:")
        st.table(
            [
                {
                    "title": task.title,
                    "priority": task.priority.value,
                    "duration_minutes": task.duration_minutes,
                    "reason": scheduler.explain_choice(task),
                }
                for task in plan.skipped_tasks
            ]
        )

    conflict_warnings = scheduler.check_for_conflicts([plan])
    if conflict_warnings:
        for warning in conflict_warnings:
            st.warning(warning)
    else:
        st.success("No scheduling conflicts detected.")
