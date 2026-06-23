"""Full coverage for models, skill_parser, registry builder, validate_pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

from runtime.models import ExecutionPlanModel, SkillDependency, SkillResult, SkillSpec
from runtime.skill_orchestrator import SkillOrchestrator
from runtime.skill_parser import (
    extract_json_block,
    parse_agent_markdown,
    parse_agent_title,
    parse_bullet_list,
    parse_capability_level,
    parse_depends_on,
    parse_numbered_steps,
    parse_skill_markdown,
    parse_task_id,
    split_sections,
    strip_frontmatter,
    validate_output_schema,
)
from runtime.skill_registry_builder import (
    agent_spec_path,
    blueprint_path,
    build_skill_registry,
    discover_blueprint_steps,
    render_how_to_run,
    validate_skill_coverage,
    write_how_to_run,
)
from runtime.skill_registry_builder import (
    main as registry_main,
)
from runtime.validate_pipeline import (
    compare_skill_outputs,
    expected_skill_ids,
    load_skill_contracts,
    validate_pipeline,
    validate_run_outputs,
)
from runtime.validate_pipeline import (
    main as validate_main,
)

ROOT = Path(__file__).resolve().parent.parent


def test_models_all_methods():
    orch = SkillOrchestrator(
        skills_root=ROOT / "skills",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    orch.discover_skills()
    skill = orch.get_skill("B1")
    spec = SkillSpec.from_definition(skill, output_file="inventory_report.json")
    assert spec.skill_id == "B1"

    dep = SkillDependency("B2", "B1")
    assert dep.to_dict() == {"skill_id": "B2", "depends_on": "B1"}

    @dataclass
    class Legacy:
        skill_id = "B1"
        status = "complete"
        output_path = "p"
        started_at = "t0"
        completed_at = "t1"
        steps_executed = []
        errors = []

    assert SkillResult.from_legacy(Legacy()).skill_id == "B1"

    plan = ExecutionPlanModel("r", ["B1"], ["B1"], [["B1"]], ["B1"])
    assert plan.to_dict()["run_id"] == "r"


def test_skill_parser_branches():
    assert parse_bullet_list("- none\n- real") == ["real"]
    assert parse_bullet_list("- —") == []

    sections = split_sections("### Task ID\n`B3`\n")
    assert parse_task_id(sections, "B1") == "B3"
    sections = split_sections("### Task ID\nnot-id\n")
    assert parse_task_id(sections, "B2") == "B2"

    deps = parse_depends_on(split_sections("### Depends On\nB1, B2\n"))
    assert "B1" in deps and "B2" in deps

    bad_json = split_sections("### Output Contract\n```json\n{bad\n```\n")
    assert extract_json_block(bad_json, "Output Contract") is None

    assert parse_numbered_steps("1. first\n2. second") == ["first", "second"]

    fm = strip_frontmatter("---\nmeta: x\n---\n# Title\n")
    assert fm.startswith("# Title")

    assert parse_agent_title("# Agent: Foo (B1)\n") is not None
    assert parse_capability_level({"Capability Level": "`I`"}, "I1") == "I"

    assert validate_output_schema({}, "not-a-dict") == []

    agent = parse_agent_markdown(ROOT / "agents" / "basics" / "B1_repo_artifact_inventory_agent.md")
    assert agent["skill_id"] == "B1"

    skill = parse_skill_markdown(ROOT / "skills" / "basics" / "B1_repo_artifact_inventory.skill.md", ROOT)
    assert skill.output_keys


def test_registry_builder_branches(tmp_path, monkeypatch):
    incomplete = validate_skill_coverage({"skills": {"B1": {"path": "missing.skill.md", "output_file": ""}}})
    assert incomplete["coverage_status"] == "INCOMPLETE"

    dup = validate_skill_coverage({"skills": {"Z9": {"path": "z", "output_file": "o.json"}}})
    assert "Z9" in dup["duplicates"]

    tasks = json.loads((ROOT / "scripts" / "task_registry.json").read_text(encoding="utf-8"))
    meta = tasks["tasks"]["B1"]
    assert agent_spec_path("B1", meta).is_file()
    assert blueprint_path("B1", meta).is_file()
    assert discover_blueprint_steps(tmp_path / "missing.md") == []

    import runtime.skill_registry_builder as srb

    monkeypatch.setattr(srb, "CORE_REGISTRY_PATH", tmp_path / "registry.json")
    registry = build_skill_registry(write_skills=False)
    assert registry["skill_count"] == 24
    doc = render_how_to_run(registry)
    assert "Repo-Analyser" in doc
    write_how_to_run(registry)


def test_registry_main_and_validate_pipeline(tmp_path, capsys):
    with patch("runtime.skill_registry_builder.build_skill_registry") as mock_build:
        mock_build.return_value = {
            "skill_count": 24,
            "skills": {},
            "coverage": {"coverage_status": "100%", "total_skills": 24},
        }
        with (
            patch("runtime.skill_registry_builder.write_registry"),
            patch("runtime.skill_registry_builder.write_how_to_run"),
        ):
            assert registry_main() == 0

    assert len(expected_skill_ids()) == 24

    orch = SkillOrchestrator(
        skills_root=ROOT / "skills",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    contracts = load_skill_contracts(orch)
    assert "B1" in contracts

    failed, invalid = validate_run_outputs(tmp_path / "missing", contracts)
    assert failed

    run_a = tmp_path / "a"
    run_b = tmp_path / "b"
    (run_a / "B1").mkdir(parents=True)
    (run_b / "B1").mkdir(parents=True)
    (run_a / "B1" / "output.json").write_text('{"task_id":"B1"}', encoding="utf-8")
    (run_b / "B1" / "output.json").write_text('{"task_id":"B1","x":1}', encoding="utf-8")
    ok, mismatches = compare_skill_outputs(run_a, run_b)
    assert not ok
    assert mismatches

    bad_run = tmp_path / "bad"
    (bad_run / "B1").mkdir(parents=True)
    (bad_run / "B1" / "output.json").write_text("{bad", encoding="utf-8")
    failed2, invalid2 = validate_run_outputs(bad_run, {"B1": {"task_id": "required"}})
    assert "B1" in failed2
    assert invalid2

    report = validate_pipeline("final_test", compare_run_id="final_test_2")
    assert "pipeline_status" in report

    rc = validate_main(["--run-id", "final_test"])
    assert rc in {0, 1}


def test_validate_pipeline_module_main():
    rc = validate_main(["--run-id", "final_test"])
    assert rc in {0, 1}


def test_skill_runner_module_main(capsys):
    from runtime.skill_runner import main as skill_runner_main

    rc = skill_runner_main(["--skill", "B1", "--run-id", "cli-run", "--plan-only"])
    assert rc == 0
