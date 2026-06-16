"""Tests for CAC-OS skill runner."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.skill_orchestrator import SkillOrchestrator
from runtime.skill_runner import SkillRunner

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


def test_run_single_skill(tmp_path: Path, orchestrator: SkillOrchestrator):
    run_id = "test-single-b1"
    run_dir = tmp_path / run_id
    plan = orchestrator.build_plan(run_id, skill_ids=["B1"])

    runner = SkillRunner(
        run_id=run_id,
        run_dir=run_dir,
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={"repository_path": str(ROOT)},
    )
    summary = runner.run_plan(plan)

    assert summary["status"] == "complete"
    assert summary["completed"] == ["B1"]
    output_path = run_dir / "B1" / "output.json"
    assert output_path.is_file()
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["task_id"] == "B1"
    assert (run_dir / "execution_log.json").is_file()
    assert (run_dir / "final_report.json").is_file()


def test_missing_dependency_fails(tmp_path: Path, orchestrator: SkillOrchestrator):
    run_id = "test-missing-dep"
    run_dir = tmp_path / run_id
    run_dir.mkdir(parents=True)

    runner = SkillRunner(
        run_id=run_id,
        run_dir=run_dir,
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={"repository_path": str(ROOT)},
    )
    result = runner.run_skill(orchestrator.get_skill("B2"))

    assert result.status == "failed"
    assert any("MISSING_DEPENDENCY_OUTPUT" in err for err in result.errors)


def test_dependency_chain_executes_in_order(tmp_path: Path, orchestrator: SkillOrchestrator):
    run_id = "test-chain"
    run_dir = tmp_path / run_id
    plan = orchestrator.build_plan(run_id, skill_ids=["B2"])

    runner = SkillRunner(
        run_id=run_id,
        run_dir=run_dir,
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={"repository_path": str(ROOT)},
    )
    summary = runner.run_plan(plan)

    assert summary["status"] == "complete"
    assert summary["completed"] == ["B1", "B2"]


def test_full_pipeline_execution(tmp_path: Path, orchestrator: SkillOrchestrator):
    run_id = "test-full-pipeline"
    run_dir = tmp_path / run_id
    plan = orchestrator.build_plan(run_id, full_pipeline=True)

    runner = SkillRunner(
        run_id=run_id,
        run_dir=run_dir,
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={"repository_path": str(ROOT)},
    )
    summary = runner.run_plan(plan)

    assert summary["status"] == "complete"
    assert len(summary["completed"]) == 24
    final_report = json.loads((run_dir / "final_report.json").read_text(encoding="utf-8"))
    assert final_report["total_skills"] == 24
    assert final_report["failed_count"] == 0
