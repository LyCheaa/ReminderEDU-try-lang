import pytest
import os
from datetime import datetime
from core_logic import Assignment, ScheduleManager, CsvStorage, IStorage

def test_assignment_validation():
    a = Assignment("Task 1", "CS", "2023-12-25")
    assert a.name == "Task 1"

    with pytest.raises(ValueError):
        Assignment("Task 2", "CS", "25-12-2023")

def test_csv_save_and_load():
    filename = "test_schedule.csv"

    if os.path.exists(filename):
        os.remove(filename)

    storage = CsvStorage(filename)

    a = Assignment("Test Task", "Math", "2025-12-31", "10:00")

    storage.save([a])

    assert os.path.exists(filename)

    loaded_items = storage.load()

    assert len(loaded_items) == 1
    assert loaded_items[0].name == "Test Task"

    os.remove(filename)

def test_manager_discard():
    filename = "test_manager.csv"
    if os.path.exists(filename): os.remove(filename)

    storage = CsvStorage(filename)
    manager = ScheduleManager(storage)

    a = Assignment("Delete Me", "Science", "2025-01-01")
    manager._assignments.append(a)
    manager._storage.save(manager._assignments)

    assert len(manager.process_and_sort()) == 1

    manager.discard_assignment(a.id)

    assert len(manager.process_and_sort()) == 0

    loaded = storage.load()
    assert len(loaded) == 0

    os.remove(filename)
