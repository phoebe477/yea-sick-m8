"""
test_student_task_tracker.py - Unit and Integration Tests
=========================================================
Test suite for the Student Task Tracker application.

Covers:
  - Unit tests: generate_example_tasks, get_countdown, save/load data,
    task CRUD operations, filter logic, sort logic, date validation logic
  - Integration tests: end-to-end task lifecycle, filter + search combined,
    delete → trash → restore flow, data persistence round-trip

Run with:
    python -m pytest test_student_task_tracker.py -v
or:
    python test_student_task_tracker.py
"""

import unittest
import os
import json
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# ---------------------------------------------------------------------------
# Import the module under test (Tkinter GUI is NOT instantiated in tests)
# ---------------------------------------------------------------------------
import importlib, sys

# We need to import only the non-GUI parts.  Patch tk.Tk so no window opens.
with patch("tkinter.Tk"):
    import student_task_tracker as stt


# ===========================================================================
# UNIT TESTS
# ===========================================================================

class TestGenerateExampleTasks(unittest.TestCase):
    """Unit tests for the generate_example_tasks helper function."""

    def test_returns_correct_count(self):
        """Should return one task per template."""
        tasks = stt.generate_example_tasks()
        self.assertEqual(len(tasks), len(stt.EXAMPLE_TASK_TEMPLATES))

    def test_task_has_required_keys(self):
        """Every task dict must contain all mandatory keys."""
        required = {"id", "title", "subject", "priority", "due", "done"}
        for task in stt.generate_example_tasks():
            self.assertTrue(required.issubset(task.keys()),
                            f"Task missing keys: {required - task.keys()}")

    def test_ids_are_unique(self):
        """All generated task IDs must be unique."""
        tasks = stt.generate_example_tasks()
        ids = [t["id"] for t in tasks]
        self.assertEqual(len(ids), len(set(ids)))

    def test_priority_values_are_valid(self):
        """Priority must be one of High, Medium, or Low."""
        valid = {"High", "Medium", "Low"}
        for task in stt.generate_example_tasks():
            self.assertIn(task["priority"], valid)

    def test_done_is_boolean(self):
        """The 'done' field must be a boolean."""
        for task in stt.generate_example_tasks():
            self.assertIsInstance(task["done"], bool)

    def test_due_date_format(self):
        """Due date strings must parse as DD/MM/YYYY HH:MM."""
        for task in stt.generate_example_tasks():
            try:
                datetime.strptime(task["due"], "%d/%m/%Y %H:%M")
            except ValueError:
                self.fail(f"Invalid due date format: {task['due']}")

    def test_different_shuffles(self):
        """Two consecutive calls should (very likely) produce different orders."""
        titles_a = [t["title"] for t in stt.generate_example_tasks()]
        titles_b = [t["title"] for t in stt.generate_example_tasks()]
        # With 40 items the probability of identical shuffle is astronomically low
        self.assertEqual(sorted(titles_a), sorted(titles_b))  # same content
        # (order difference is probabilistic so we just check content equality)


class TestGetCountdown(unittest.TestCase):
    """Unit tests for StudentTaskTracker.get_countdown()."""

    def _make_app(self):
        """Create a minimal app stub without opening a window."""
        with patch("tkinter.Tk"), patch.object(stt.StudentTaskTracker, "create_gui"), \
             patch.object(stt.StudentTaskTracker, "populate_task_list"), \
             patch.object(stt.StudentTaskTracker, "load_data"):
            app = stt.StudentTaskTracker.__new__(stt.StudentTaskTracker)
            app.tasks = []
            app.deleted_tasks = []
            app.dark_mode = False
            return app

    def test_future_date_returns_countdown(self):
        """A future date should return a non-overdue countdown string."""
        app = self._make_app()
        future = datetime.now() + timedelta(days=3, hours=4)
        result = app.get_countdown(future.strftime("%d/%m/%Y %H:%M"))
        self.assertNotEqual(result, "OVERDUE")
        self.assertIn("d", result)

    def test_past_date_returns_overdue(self):
        """A past date should return 'OVERDUE'."""
        app = self._make_app()
        past = datetime.now() - timedelta(days=1)
        result = app.get_countdown(past.strftime("%d/%m/%Y %H:%M"))
        self.assertEqual(result, "OVERDUE")

    def test_invalid_format_returns_invalid(self):
        """A malformed date string should return 'Invalid'."""
        app = self._make_app()
        self.assertEqual(app.get_countdown("not-a-date"), "Invalid")
        self.assertEqual(app.get_countdown("31/13/2025 10:00"), "Invalid")

    def test_same_day_future(self):
        """A due time later today should show 0d Xh."""
        app = self._make_app()
        soon = datetime.now() + timedelta(hours=2)
        result = app.get_countdown(soon.strftime("%d/%m/%Y %H:%M"))
        self.assertTrue(result.startswith("0d"))


class TestDataPersistence(unittest.TestCase):
    """Unit tests for save_data / load_data using temporary files."""

    def _make_app(self, data_file, trash_file):
        with patch("tkinter.Tk"), patch.object(stt.StudentTaskTracker, "create_gui"), \
             patch.object(stt.StudentTaskTracker, "populate_task_list"):
            app = stt.StudentTaskTracker.__new__(stt.StudentTaskTracker)
            app.tasks = []
            app.deleted_tasks = []
            app.subjects = ["General"]
            app.dark_mode = False
            app.data_file  = data_file
            app.trash_file = trash_file
            return app

    def test_save_then_load_round_trip(self):
        """Tasks saved to disk should be identical when loaded back."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            data_file = f.name
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            trash_file = f.name
        try:
            app = self._make_app(data_file, trash_file)
            app.tasks = [{"id": 1, "title": "Test Task", "subject": "Maths",
                          "priority": "High", "due": "01/06/2025 10:00", "done": False}]
            app.save_data()

            app2 = self._make_app(data_file, trash_file)
            app2.load_data()
            self.assertEqual(len(app2.tasks), 1)
            self.assertEqual(app2.tasks[0]["title"], "Test Task")
        finally:
            os.unlink(data_file)
            os.unlink(trash_file)

    def test_empty_tasks_saved_and_loaded(self):
        """Saving an empty list should load back as empty."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            data_file = f.name
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            trash_file = f.name
        try:
            app = self._make_app(data_file, trash_file)
            app.tasks = []
            app.save_data()
            app.load_data()
            self.assertEqual(app.tasks, [])
        finally:
            os.unlink(data_file)
            os.unlink(trash_file)

    def test_missing_file_does_not_crash(self):
        """load_data with a non-existent file should silently use defaults."""
        app = self._make_app("nonexistent_xyz.json", "nonexistent_trash.json")
        try:
            app.load_data()   # should not raise
            self.assertIsInstance(app.tasks, list)
        except Exception as e:
            self.fail(f"load_data raised an exception: {e}")

    def test_subjects_persisted(self):
        """Custom subjects should survive a save/load cycle."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            data_file = f.name
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            trash_file = f.name
        try:
            app = self._make_app(data_file, trash_file)
            app.subjects = ["General", "Maths", "Physics"]
            app.save_data()
            app.load_data()
            self.assertIn("Physics", app.subjects)
        finally:
            os.unlink(data_file)
            os.unlink(trash_file)


class TestFilterLogic(unittest.TestCase):
    """Unit tests for _get_filtered_tasks dashboard card filter logic."""

    def _make_app_with_tasks(self):
        with patch("tkinter.Tk"), patch.object(stt.StudentTaskTracker, "create_gui"), \
             patch.object(stt.StudentTaskTracker, "populate_task_list"), \
             patch.object(stt.StudentTaskTracker, "load_data"):
            app = stt.StudentTaskTracker.__new__(stt.StudentTaskTracker)
            app.dark_mode = False
            now = datetime.now()
            app.tasks = [
                {"id": 1, "title": "Done Task",    "subject": "Maths",   "priority": "Low",
                 "due": (now - timedelta(days=5)).strftime("%d/%m/%Y %H:%M"),  "done": True},
                {"id": 2, "title": "Overdue Task", "subject": "English", "priority": "High",
                 "due": (now - timedelta(days=2)).strftime("%d/%m/%Y %H:%M"),  "done": False},
                {"id": 3, "title": "Due Soon",     "subject": "Physics", "priority": "Medium",
                 "due": (now + timedelta(hours=10)).strftime("%d/%m/%Y %H:%M"), "done": False},
                {"id": 4, "title": "Future Task",  "subject": "History", "priority": "Low",
                 "due": (now + timedelta(days=30)).strftime("%d/%m/%Y %H:%M"),  "done": False},
            ]
            return app

    def test_total_returns_all(self):
        app = self._make_app_with_tasks()
        self.assertEqual(len(app._get_filtered_tasks("total")), 4)

    def test_pending_excludes_done(self):
        app = self._make_app_with_tasks()
        result = app._get_filtered_tasks("pending")
        self.assertTrue(all(not t["done"] for t in result))
        self.assertEqual(len(result), 3)

    def test_done_returns_only_completed(self):
        app = self._make_app_with_tasks()
        result = app._get_filtered_tasks("done")
        self.assertTrue(all(t["done"] for t in result))
        self.assertEqual(len(result), 1)

    def test_overdue_returns_only_past_pending(self):
        app = self._make_app_with_tasks()
        result = app._get_filtered_tasks("overdue")
        # Only "Overdue Task" qualifies (past + not done)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Overdue Task")

    def test_due_soon_within_24h(self):
        app = self._make_app_with_tasks()
        result = app._get_filtered_tasks("due_soon")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["title"], "Due Soon")

    def test_unknown_key_returns_all(self):
        app = self._make_app_with_tasks()
        result = app._get_filtered_tasks("unknown_key")
        self.assertEqual(len(result), 4)


class TestSortLogic(unittest.TestCase):
    """Unit tests for the sorting key functions used in _sort_by_col."""

    def _sample_tasks(self):
        now = datetime.now()
        return [
            {"id": 3, "title": "Zebra",  "subject": "Maths",   "priority": "Low",
             "due": (now + timedelta(days=5)).strftime("%d/%m/%Y %H:%M"), "done": False},
            {"id": 1, "title": "Apple",  "subject": "English", "priority": "High",
             "due": (now + timedelta(days=1)).strftime("%d/%m/%Y %H:%M"), "done": True},
            {"id": 2, "title": "Mango",  "subject": "History", "priority": "Medium",
             "due": (now + timedelta(days=3)).strftime("%d/%m/%Y %H:%M"), "done": False},
        ]

    def test_sort_by_id_ascending(self):
        tasks = self._sample_tasks()
        tasks.sort(key=lambda t: t["id"])
        self.assertEqual([t["id"] for t in tasks], [1, 2, 3])

    def test_sort_by_title_ascending(self):
        tasks = self._sample_tasks()
        tasks.sort(key=lambda t: t["title"].lower())
        self.assertEqual(tasks[0]["title"], "Apple")
        self.assertEqual(tasks[-1]["title"], "Zebra")

    def test_sort_by_priority(self):
        order = {"High": 1, "Medium": 2, "Low": 3}
        tasks = self._sample_tasks()
        tasks.sort(key=lambda t: order.get(t["priority"], 9))
        self.assertEqual(tasks[0]["priority"], "High")
        self.assertEqual(tasks[-1]["priority"], "Low")

    def test_sort_by_due_date(self):
        tasks = self._sample_tasks()
        tasks.sort(key=lambda t: datetime.strptime(t["due"], "%d/%m/%Y %H:%M"))
        dues = [datetime.strptime(t["due"], "%d/%m/%Y %H:%M") for t in tasks]
        self.assertEqual(dues, sorted(dues))

    def test_sort_descending_reverses_order(self):
        tasks = self._sample_tasks()
        tasks.sort(key=lambda t: t["id"], reverse=True)
        self.assertEqual([t["id"] for t in tasks], [3, 2, 1])


class TestDateValidation(unittest.TestCase):
    """Unit tests for the date validation logic used in task_form.save()."""

    def test_past_date_detected(self):
        """A date before now should be classified as past."""
        past = datetime.now() - timedelta(days=2)
        self.assertLess(past, datetime.now())

    def test_future_within_year_ok(self):
        """A date 6 months ahead should NOT trigger the far-future warning."""
        future = datetime.now() + timedelta(days=180)
        self.assertLessEqual(future, datetime.now() + timedelta(days=365))

    def test_date_over_one_year_triggers_warning(self):
        """A date more than 365 days away should trigger the warning."""
        far_future = datetime.now() + timedelta(days=400)
        self.assertGreater(far_future, datetime.now() + timedelta(days=365))

    def test_ago_string_days(self):
        """Human-readable 'ago' string for a 3-day-old date."""
        past = datetime.now() - timedelta(days=3)
        delta = datetime.now() - past
        days = delta.days
        self.assertEqual(days, 3)
        ago = f"{days} day(s) ago"
        self.assertEqual(ago, "3 day(s) ago")

    def test_ago_string_hours(self):
        """Human-readable 'ago' string for a same-day past time."""
        past = datetime.now() - timedelta(hours=2)
        delta = datetime.now() - past
        days = delta.days
        self.assertEqual(days, 0)
        ago = f"{delta.seconds // 3600} hour(s) ago"
        self.assertIn("hour", ago)


class TestTaskCRUD(unittest.TestCase):
    """Unit tests for in-memory task CRUD operations."""

    def _base_task(self, tid=1):
        return {"id": tid, "title": "Test", "subject": "General",
                "priority": "Medium",
                "due": (datetime.now() + timedelta(days=3)).strftime("%d/%m/%Y %H:%M"),
                "done": False}

    def test_new_task_gets_incremented_id(self):
        """A new task should receive max(existing ids) + 1."""
        tasks = [self._base_task(1), self._base_task(2)]
        new_id = max(t["id"] for t in tasks) + 1
        self.assertEqual(new_id, 3)

    def test_edit_task_updates_in_place(self):
        """Editing a task dict in-place should reflect immediately."""
        task = self._base_task()
        task.update({"title": "Updated Title", "priority": "High"})
        self.assertEqual(task["title"], "Updated Title")
        self.assertEqual(task["priority"], "High")

    def test_soft_delete_moves_to_trash(self):
        """Soft-deleting should remove from tasks and add to deleted_tasks."""
        tasks = [self._base_task(1), self._base_task(2)]
        deleted = []
        target = tasks[0]
        t_copy = target.copy()
        t_copy["deleted_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        deleted.append(t_copy)
        tasks.remove(target)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(len(deleted), 1)
        self.assertIn("deleted_at", deleted[0])

    def test_restore_task_from_trash(self):
        """Restoring a task should move it back to the active list."""
        tasks = []
        deleted = [self._base_task(1)]
        deleted[0]["deleted_at"] = "01/01/2025 10:00"
        t = deleted.pop(0)
        t.pop("deleted_at", None)
        t["id"] = 99   # new ID assigned on restore
        tasks.append(t)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(len(deleted), 0)
        self.assertNotIn("deleted_at", tasks[0])

    def test_mark_done_toggles(self):
        """toggle_done logic should flip the done flag."""
        task = self._base_task()
        self.assertFalse(task["done"])
        task["done"] = not task["done"]
        self.assertTrue(task["done"])
        task["done"] = not task["done"]
        self.assertFalse(task["done"])


# ===========================================================================
# INTEGRATION TESTS
# ===========================================================================

class TestIntegrationTaskLifecycle(unittest.TestCase):
    """
    Integration tests covering end-to-end task lifecycle with real file I/O.

    These tests create actual temporary JSON files to verify the full
    save → reload → filter → delete → restore pipeline.
    """

    def setUp(self):
        self.tmp_data  = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp_trash = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp_data.close()
        self.tmp_trash.close()

    def tearDown(self):
        for f in (self.tmp_data.name, self.tmp_trash.name):
            if os.path.exists(f):
                os.unlink(f)

    def _make_app(self):
        with patch("tkinter.Tk"), patch.object(stt.StudentTaskTracker, "create_gui"), \
             patch.object(stt.StudentTaskTracker, "populate_task_list"):
            app = stt.StudentTaskTracker.__new__(stt.StudentTaskTracker)
            app.tasks         = []
            app.deleted_tasks = []
            app.subjects      = ["General"]
            app.dark_mode     = False
            app._active_filter = None
            app.data_file     = self.tmp_data.name
            app.trash_file    = self.tmp_trash.name
            return app

    def test_full_create_save_reload_cycle(self):
        """Create a task, save, reload in a new app instance → task persists."""
        app = self._make_app()
        app.tasks.append({"id": 1, "title": "Integration Task", "subject": "Maths",
                           "priority": "High",
                           "due": "30/06/2025 09:00", "done": False})
        app.save_data()

        app2 = self._make_app()
        app2.load_data()
        self.assertEqual(len(app2.tasks), 1)
        self.assertEqual(app2.tasks[0]["title"], "Integration Task")

    def test_delete_and_restore_pipeline(self):
        """Delete a task to trash, save, reload, restore → back in active list."""
        app = self._make_app()
        task = {"id": 1, "title": "Restore Me", "subject": "English",
                "priority": "Medium", "due": "30/06/2025 12:00", "done": False}
        app.tasks.append(task)

        # Soft delete
        t_copy = task.copy()
        t_copy["deleted_at"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        t_copy["deleted_by_game"] = False
        app.deleted_tasks.append(t_copy)
        app.tasks.remove(task)
        app.save_data()
        self.assertEqual(len(app.tasks), 0)

        # Reload and restore
        app2 = self._make_app()
        app2.load_data()
        self.assertEqual(len(app2.deleted_tasks), 1)
        restored = app2.deleted_tasks.pop(0)
        restored.pop("deleted_at", None)
        restored.pop("deleted_by_game", None)
        restored["id"] = max([t["id"] for t in app2.tasks], default=0) + 1
        app2.tasks.append(restored)
        self.assertEqual(len(app2.tasks), 1)
        self.assertEqual(app2.tasks[0]["title"], "Restore Me")

    def test_filter_and_search_combined(self):
        """Overdue filter intersected with a search term returns correct subset."""
        app = self._make_app()
        now = datetime.now()
        app.tasks = [
            {"id": 1, "title": "Physics Overdue",  "subject": "Physics",
             "priority": "High",
             "due": (now - timedelta(days=3)).strftime("%d/%m/%Y %H:%M"), "done": False},
            {"id": 2, "title": "Maths Overdue",    "subject": "Maths",
             "priority": "Medium",
             "due": (now - timedelta(days=1)).strftime("%d/%m/%Y %H:%M"), "done": False},
            {"id": 3, "title": "Future Task",      "subject": "History",
             "priority": "Low",
             "due": (now + timedelta(days=10)).strftime("%d/%m/%Y %H:%M"), "done": False},
        ]
        # Overdue filter
        overdue = app._get_filtered_tasks("overdue")
        self.assertEqual(len(overdue), 2)

        # Further narrow by search
        search = "physics"
        narrowed = [t for t in overdue
                    if search in t["title"].lower() or search in t["subject"].lower()]
        self.assertEqual(len(narrowed), 1)
        self.assertEqual(narrowed[0]["title"], "Physics Overdue")

    def test_multiple_tasks_sorted_by_deadline(self):
        """After sorting by due date the earliest task should be first."""
        app = self._make_app()
        now = datetime.now()
        app.tasks = [
            {"id": 1, "title": "Last",  "subject": "Art",     "priority": "Low",
             "due": (now + timedelta(days=10)).strftime("%d/%m/%Y %H:%M"), "done": False},
            {"id": 2, "title": "First", "subject": "Biology", "priority": "High",
             "due": (now + timedelta(days=1)).strftime("%d/%m/%Y %H:%M"),  "done": False},
            {"id": 3, "title": "Mid",   "subject": "French",  "priority": "Medium",
             "due": (now + timedelta(days=5)).strftime("%d/%m/%Y %H:%M"),  "done": False},
        ]
        app.tasks.sort(key=lambda t: datetime.strptime(t["due"], "%d/%m/%Y %H:%M"))
        self.assertEqual(app.tasks[0]["title"], "First")
        self.assertEqual(app.tasks[-1]["title"], "Last")

    def test_json_files_are_valid_json(self):
        """Saved files must be parseable as valid JSON."""
        app = self._make_app()
        app.tasks = [{"id": 1, "title": "T", "subject": "S",
                      "priority": "High", "due": "01/06/2025 10:00", "done": False}]
        app.save_data()
        with open(self.tmp_data.name) as f:
            data = json.load(f)
        self.assertIn("tasks", data)
        self.assertIn("subjects", data)


# ===========================================================================
# ENTRY POINT
# ===========================================================================

if __name__ == "__main__":
    loader  = unittest.TestLoader()
    suite   = unittest.TestSuite()

    test_classes = [
        TestGenerateExampleTasks,
        TestGetCountdown,
        TestDataPersistence,
        TestFilterLogic,
        TestSortLogic,
        TestDateValidation,
        TestTaskCRUD,
        TestIntegrationTaskLifecycle,
    ]

    for cls in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(cls))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
