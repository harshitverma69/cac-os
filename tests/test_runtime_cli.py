"""Additional runtime coverage tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.skill_orchestrator import SkillOrchestrator
from runtime.skill_parser import parse_skill_markdown
from runtime.skill_registry_builder import main as build_main
from runtime.skill_runner import main as run_main

ROOT = Path(__file__).resolve().parent.parent


def test_parse_run_all_skills_master():
    skill = parse_skill_markdown(ROOT / "skills" / "run_all_skills.skill.md", ROOT)
    assert skill.skill_id == "ALL"
    assert "Full Pipeline" in skill.name
    assert len(skill.execution_steps) >= 3


def test_orchestrator_build_plan_domain():
    orch = SkillOrchestrator(
        skills_root=ROOT / "skills",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    orch.load_registry()
    orch.discover_skills()
    plan = orch.build_plan("demo", domain="D")
    assert plan.requested == ["D1", "D2", "D3", "D4", "D5", "D6"]
    assert len(plan.execution_order) == 8
    assert plan.execution_order[-1] == "D6"


def test_orchestrator_build_plan_requires_args():
    orch = SkillOrchestrator(
        skills_root=ROOT / "skills",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    orch.load_registry()
    with pytest.raises(ValueError):
        orch.build_plan("demo")


def test_orchestrator_invalid_domain():
    orch = SkillOrchestrator(
        skills_root=ROOT / "skills",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    orch.load_registry()
    with pytest.raises(ValueError):
        orch.skills_for_domain("X")


def test_orchestrator_missing_registry(tmp_path: Path):
    orch = SkillOrchestrator(registry_path=tmp_path / "missing.json")
    with pytest.raises(FileNotFoundError):
        orch.load_registry()


def test_registry_builder_main():
    assert build_main() == 0
    assert (ROOT / "core" / "skill_registry.json").is_file()
    assert (ROOT / "docs" / "SKILL_CATALOG.md").is_file()


def test_runner_cli_plan_only(capsys):
    rc = run_main(["--plan-only", "--skill", "B1", "--run-id", "cli-test"])
    assert rc == 0
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["execution_order"] == ["B1"]


def test_runner_cli_missing_args():
    assert run_main([]) == 1


def test_runner_cli_full_pipeline(tmp_path: Path, monkeypatch):
    run_id = "cli-full-pipeline"
    run_dir = tmp_path / run_id
    monkeypatch.setattr("runtime.skill_runner.GENERATED_ROOT", tmp_path)
    rc = run_main(
        [
            "--full-pipeline",
            "--run-id",
            run_id,
            "--repository-path",
            str(ROOT),
        ]
    )
    assert rc == 0
    assert (run_dir / "final_report.json").is_file()
    final = json.loads((run_dir / "final_report.json").read_text(encoding="utf-8"))
    assert final["completed_count"] == 24


def test_runner_missing_input_fails(tmp_path: Path):
    from runtime.skill_runner import SkillRunner

    run_id = "missing-input"
    runner = SkillRunner(
        run_id=run_id,
        run_dir=tmp_path / run_id,
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={"repository_path": str(tmp_path / "does-not-exist")},
    )
    orch = SkillOrchestrator(
        skills_root=ROOT / "skills",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    orch.discover_skills()
    result = runner.run_skill(orch.get_skill("B1"))
    assert result.status == "failed"
    assert any("INPUT_CONTRACT_VIOLATION" in err for err in result.errors)
