"""Tests for envforge.schedule module."""

import json
import time
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from envforge.schedule import (
    set_schedule,
    remove_schedule,
    list_schedules,
    get_due_schedules,
    mark_ran,
    load_schedule,
    _get_schedule_path,
)


@pytest.fixture
def sched_dir(tmp_path):
    return str(tmp_path)


class TestSetSchedule:
    def test_creates_entry(self, sched_dir):
        entry = set_schedule("nightly", 86400, base_dir=sched_dir)
        assert entry["interval_seconds"] == 86400
        assert entry["label_prefix"] == "auto"
        assert entry["last_run"] is None

    def test_custom_prefix(self, sched_dir):
        entry = set_schedule("prod", 3600, label_prefix="prod-snap", base_dir=sched_dir)
        assert entry["label_prefix"] == "prod-snap"

    def test_persists_to_file(self, sched_dir):
        set_schedule("ci", 600, base_dir=sched_dir)
        data = load_schedule(sched_dir)
        assert "ci" in data

    def test_overwrite_existing(self, sched_dir):
        set_schedule("ci", 600, base_dir=sched_dir)
        set_schedule("ci", 1200, base_dir=sched_dir)
        data = load_schedule(sched_dir)
        assert data["ci"]["interval_seconds"] == 1200


class TestRemoveSchedule:
    def test_removes_existing(self, sched_dir):
        set_schedule("temp", 60, base_dir=sched_dir)
        result = remove_schedule("temp", base_dir=sched_dir)
        assert result is True
        assert "temp" not in load_schedule(sched_dir)

    def test_returns_false_if_not_found(self, sched_dir):
        result = remove_schedule("ghost", base_dir=sched_dir)
        assert result is False


class TestGetDueSchedules:
    def test_new_schedule_is_due(self, sched_dir):
        set_schedule("fresh", 3600, base_dir=sched_dir)
        due = get_due_schedules(base_dir=sched_dir)
        assert "fresh" in due

    def test_recently_run_is_not_due(self, sched_dir):
        set_schedule("recent", 3600, base_dir=sched_dir)
        mark_ran("recent", base_dir=sched_dir)
        due = get_due_schedules(base_dir=sched_dir)
        assert "recent" not in due

    def test_overdue_schedule_is_due(self, sched_dir):
        set_schedule("old", 1, base_dir=sched_dir)
        sched = load_schedule(sched_dir)
        past = (datetime.utcnow() - timedelta(seconds=10)).isoformat()
        sched["old"]["last_run"] = past
        path = _get_schedule_path(sched_dir)
        with open(path, "w") as f:
            json.dump(sched, f)
        due = get_due_schedules(base_dir=sched_dir)
        assert "old" in due


class TestMarkRan:
    def test_updates_last_run(self, sched_dir):
        set_schedule("check", 300, base_dir=sched_dir)
        mark_ran("check", base_dir=sched_dir)
        data = load_schedule(sched_dir)
        assert data["check"]["last_run"] is not None

    def test_no_error_if_name_missing(self, sched_dir):
        mark_ran("nonexistent", base_dir=sched_dir)  # should not raise


def test_list_schedules_empty(sched_dir):
    result = list_schedules(base_dir=sched_dir)
    assert result == {}


def test_list_schedules_multiple(sched_dir):
    set_schedule("a", 60, base_dir=sched_dir)
    set_schedule("b", 120, base_dir=sched_dir)
    result = list_schedules(base_dir=sched_dir)
    assert set(result.keys()) == {"a", "b"}
