"""Runner edge-case coverage tests."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from runtime.skill_orchestrator import SkillOrchestrator
from runtime.skill_runner import SkillRunner, main as run_main

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


def test_missing_golden_output_fails(tmp_path: Path, orchestrator: SkillOrchestrator):
    runner = SkillRunner(
        run_id="no-golden",
        run_dir=tmp_path / "no-golden",
        golden_dir=tmp_path / "empty-golden",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={"repository_path": str(ROOT)},
    )
    result = runner.run_skill(orchestrator.get_skill("B1"))
    assert result.status == "failed"
    assert any("Golden output missing" in err for err in result.errors)


def test_output_schema_violation_fails(tmp_path: Path, orchestrator: SkillOrchestrator):
    runner = SkillRunner(
        run_id="schema-fail",
        run_dir=tmp_path / "schema-fail",
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={"repository_path": str(ROOT)},
    )

    with patch.object(runner, "load_golden_output", return_value={"unexpected": True}):
        result = runner.run_skill(orchestrator.get_skill("B1"))

    assert result.status == "failed"
    assert any("MISSING_OUTPUT_KEY" in err for err in result.errors)


def test_runner_cli_domain(capsys):
    rc = run_main(["--domain", "B", "--run-id", "domain-b", "--plan-only"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["requested"] == ["B1", "B2", "B3", "B4", "B5", "B6"]


def test_artifact_input_explicit_path(tmp_path: Path, orchestrator: SkillOrchestrator):
    run_id = "artifact-input"
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True)

    runner = SkillRunner(
        run_id=run_id,
        run_dir=run_dir,
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={
            "repository_path": str(ROOT),
            "inventory_report.json": str(ROOT / "generated_projects" / "_golden" / "B1" / "inventory_report.json"),
        },
    )
    assert runner._artifact_input_available("inventory_report.json", orchestrator.get_skill("B2")) is True


def test_missing_non_json_input_fails(tmp_path: Path, orchestrator: SkillOrchestrator):
    runner = SkillRunner(
        run_id="missing-project-name",
        run_dir=tmp_path / "missing-project-name",
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={"repository_path": str(ROOT), "output_dir": str(tmp_path), "project_name": None},
    )
    runner.inputs.pop("project_name", None)
    result = runner.run_skill(orchestrator.get_skill("B4"))
    assert result.status == "failed"
    assert any("MISSING_INPUT: project_name" in err for err in result.errors)


def test_runner_aborted_pipeline(tmp_path: Path, orchestrator: SkillOrchestrator):
    run_id = "aborted"
    run_dir = tmp_path / run_id
    plan = orchestrator.build_plan(run_id, skill_ids=["B1", "B2"])

    runner = SkillRunner(
        run_id=run_id,
        run_dir=run_dir,
        golden_dir=tmp_path / "missing",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={"repository_path": str(ROOT)},
    )
    summary = runner.run_plan(plan)
    assert summary["status"] == "failed"
    assert summary["completed"] == []
    assert summary["failed"] == ["B1", "B2"]

    log = json.loads((run_dir / "execution_log.json").read_text(encoding="utf-8"))
    assert log["aborted"] is True
