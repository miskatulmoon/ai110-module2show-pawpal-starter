import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import CareTask, Pet


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
