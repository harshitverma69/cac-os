"""Coverage for validate_pipeline and deterministic helpers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.deterministic import stable_sort
from runtime.validate_pipeline import main as validate_main, validate_pipeline

ROOT = Path(__file__).resolve().parent.parent


def test_stable_sort_orders_values():
    assert stable_sort([{"b": 2}, {"a": 1}]) == [{"a": 1}, {"b": 2}]


def test_validate_pipeline_missing_run(tmp_path: Path, monkeypatch):
    monkeypatch.setattr("runtime.validate_pipeline.GENERATED_ROOT", tmp_path)
    report = validate_pipeline("missing-run")
    assert report["pipeline_status"] == "FAIL"
    assert report["failed_skills"]


def test_validate_pipeline_cli_pass(capsys):
    run_dir = ROOT / "generated_projects" / "final_test"
    if not run_dir.is_dir():
        pytest.skip("Run make harden first")

    rc = validate_main(["--run-id", "final_test", "--compare-run-id", "final_test_2"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["pipeline_status"] == "PASS"


def test_orchestrator_cli_missing_flag(capsys):
    from runtime.skill_orchestrator import main as orchestrator_main

    assert orchestrator_main([]) == 1
