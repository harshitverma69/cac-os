"""Additional coverage for DAG edge cases and registry validation."""

from __future__ import annotations

import json
from pathlib import Path

from runtime.skill_orchestrator import SkillOrchestrator
from runtime.skill_registry_builder import validate_skill_coverage
from runtime.validate_pipeline import validate_run_outputs

ROOT = Path(__file__).resolve().parent.parent


def test_find_missing_dependencies():
    orch = SkillOrchestrator()
    missing = orch.find_missing_dependencies({"B2": ["B99"]})
    assert missing == [{"skill_id": "B2", "missing_dependency": "B99"}]


def test_find_orphan_when_dependency_missing_from_graph():
    orch = SkillOrchestrator()
    orphans = orch.find_orphan_skills({"B2": ["B1"]})
    assert orphans == ["B2"]


def test_validate_dag_invalid_cycle():
    orch = SkillOrchestrator()
    orch._registry = {
        "skills": {
            "B1": {"depends_on": ["B2"]},
            "B2": {"depends_on": ["B1"]},
        }
    }
    report = orch.validate_dag()
    assert report["dag_status"] == "INVALID"
    assert report["cycles"]


def test_validate_run_outputs_invalid_json(tmp_path: Path):
    run_dir = tmp_path / "bad-json"
    (run_dir / "B1").mkdir(parents=True)
    (run_dir / "B1" / "output.json").write_text("{bad", encoding="utf-8")

    failed, invalid = validate_run_outputs(run_dir, {"B1": {"task_id": "B1"}})
    assert "B1" in failed
    assert invalid[0]["errors"][0].startswith("INVALID_JSON")


def test_coverage_detects_missing_skill():
    coverage = validate_skill_coverage({"skills": {"B1": {"path": "x", "output_file": "y"}}})
    assert coverage["coverage_status"] == "INCOMPLETE"
    assert len(coverage["missing"]) == 23


def test_compare_skill_outputs_detects_mismatch(tmp_path: Path):
    from runtime.validate_pipeline import compare_skill_outputs

    run_a = tmp_path / "a"
    run_b = tmp_path / "b"
    (run_a / "B1").mkdir(parents=True)
    (run_b / "B1").mkdir(parents=True)
    (run_a / "B1" / "output.json").write_text('{"task_id":"B1","a":1}\n', encoding="utf-8")
    (run_b / "B1" / "output.json").write_text('{"task_id":"B1","a":2}\n', encoding="utf-8")

    identical, mismatches = compare_skill_outputs(run_a, run_b)
    assert not identical
    assert mismatches


def test_runner_stop_on_first_failure(tmp_path: Path):
    from runtime.skill_orchestrator import SkillOrchestrator
    from runtime.skill_runner import SkillRunner

    orch = SkillOrchestrator(
        skills_root=ROOT / "skills",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    orch.load_registry()
    orch.discover_skills()
    plan = orch.build_plan("stop", skill_ids=["B1"])

    runner = SkillRunner(
        run_id="stop",
        run_dir=tmp_path / "stop",
        golden_dir=tmp_path / "missing",
        registry_path=ROOT / "core" / "skill_registry.json",
        continue_on_failure=False,
    )
    summary = runner.run_plan(plan)
    assert summary["status"] == "failed"
    assert summary["failed"] == ["B1"]
