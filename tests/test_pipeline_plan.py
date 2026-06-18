"""Tests for frontend pipeline plan API."""

from __future__ import annotations

import pytest

from runtime.pipeline_plan import create_pipeline_plan, run_id_from_path


def test_run_id_from_path_slugifies_name():
    assert run_id_from_path("/tmp/My Repo") == "my-repo"


def test_create_pipeline_plan_orders_all_skills(tmp_path):
    repo = tmp_path / "sample-app"
    repo.mkdir()
    plan = create_pipeline_plan(str(repo))

    assert plan["ok"] is True
    assert plan["run_id"] == "sample-app"
    assert plan["total"] == 24
    assert len(plan["execution_order"]) == 24
    assert plan["execution_order"][0] == "B1"
    assert plan["skills"][0]["slash_command"].startswith("/repo-analyser-")


def test_create_pipeline_plan_rejects_missing_folder():
    with pytest.raises(ValueError, match="Folder not found"):
        create_pipeline_plan("/path/that/does/not/exist")
