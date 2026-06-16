"""Production hardening acceptance tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from runtime.deterministic import canonical_json_dumps
from runtime.skill_orchestrator import SkillOrchestrator
from runtime.skill_registry_builder import EXPECTED_SKILL_COUNT, validate_skill_coverage
from runtime.skill_runner import SkillRunner
from runtime.validate_pipeline import compare_skill_outputs, validate_pipeline

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def orchestrator() -> SkillOrchestrator:
    orch = SkillOrchestrator(
        skills_root=ROOT / "skills",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    orch.load_registry()
    orch.discover_skills()
    return orch


def test_dag_validation_valid(orchestrator: SkillOrchestrator):
    report = orchestrator.validate_dag()
    assert report["dag_status"] == "VALID"
    assert report["cycles"] == []
    assert report["missing_dependencies"] == []
    assert report["orphan_skills"] == []
    assert report["topological_order_stable"] is True
    assert len(report["execution_order"]) == 24


def test_skill_coverage_24_of_24():
    registry = json.loads((ROOT / "core" / "skill_registry.json").read_text(encoding="utf-8"))
    coverage = validate_skill_coverage(registry, ROOT / "skills")
    assert coverage["total_skills"] == EXPECTED_SKILL_COUNT
    assert coverage["missing"] == []
    assert coverage["duplicates"] == []
    assert coverage["coverage_status"] == "100%"


def test_deterministic_rerun_identical_outputs(tmp_path: Path, orchestrator: SkillOrchestrator):
    run_a = tmp_path / "run_a"
    run_b = tmp_path / "run_b"
    plan = orchestrator.build_plan("determinism", full_pipeline=True)

    runner_a = SkillRunner(
        run_id="run_a",
        run_dir=run_a,
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    runner_b = SkillRunner(
        run_id="run_b",
        run_dir=run_b,
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
    )

    summary_a = runner_a.run_plan(plan)
    summary_b = runner_b.run_plan(plan)
    assert summary_a["status"] == "complete"
    assert summary_b["status"] == "complete"

    identical, mismatches = compare_skill_outputs(run_a, run_b)
    assert identical, mismatches

    for skill_id in summary_a["completed"]:
        bytes_a = (run_a / skill_id / "output.json").read_bytes()
        bytes_b = (run_b / skill_id / "output.json").read_bytes()
        assert bytes_a == bytes_b


def test_pipeline_validator_passes_after_full_run(tmp_path: Path, monkeypatch):
    run_id = "validator-run"
    run_dir = tmp_path / run_id
    monkeypatch.setattr("runtime.skill_runner.GENERATED_ROOT", tmp_path)
    monkeypatch.setattr("runtime.validate_pipeline.GENERATED_ROOT", tmp_path)

    orchestrator = SkillOrchestrator(
        skills_root=ROOT / "skills",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    orchestrator.load_registry()
    orchestrator.discover_skills()
    plan = orchestrator.build_plan(run_id, full_pipeline=True)

    runner = SkillRunner(
        run_id=run_id,
        run_dir=run_dir,
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    assert runner.run_plan(plan)["status"] == "complete"

    report = validate_pipeline(run_id)
    assert report["pipeline_status"] == "PASS"
    assert report["dag_valid"] is True
    assert report["deterministic"] is True
    assert report["failed_skills"] == []


def test_orchestrator_cli_validate_dag():
    import os

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)
    result = subprocess.run(
        [sys.executable, "-m", "runtime.skill_orchestrator", "--validate-dag"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["dag_status"] == "VALID"


def test_no_timestamp_in_skill_output(tmp_path: Path, orchestrator: SkillOrchestrator):
    run_dir = tmp_path / "no-ts"
    plan = orchestrator.build_plan("no-ts", skill_ids=["B1"])
    runner = SkillRunner(
        run_id="no-ts",
        run_dir=run_dir,
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    runner.run_plan(plan)
    payload = json.loads((run_dir / "B1" / "output.json").read_text(encoding="utf-8"))
    assert "generated_at" not in payload
    assert "run_id" not in payload
