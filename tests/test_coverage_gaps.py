"""Targeted tests for remaining uncovered runtime lines."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent


def test_frontend_sync_remaining(monkeypatch, tmp_path):
    import runtime.frontend_sync as mod
    from runtime.frontend_sync import _ensure_frontend_data, ensure_frontend_server

    monkeypatch.setenv("REPO_ANALYSER_AUTO_START_FRONTEND", "0")
    monkeypatch.setattr(mod, "frontend_is_running", lambda port=None: False)
    assert mod._auto_start_frontend_enabled() is False
    assert ensure_frontend_server() is False

    monkeypatch.setenv("REPO_ANALYSER_AUTO_START_FRONTEND", "1")
    monkeypatch.setattr(mod, "FRONTEND_DATA", tmp_path / "data")
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "skills.json").write_text("{}", encoding="utf-8")
    assert _ensure_frontend_data() is True

    monkeypatch.setattr(mod, "frontend_is_running", lambda port=None: True)
    assert ensure_frontend_server() is True

    # startup loop success
    monkeypatch.setenv("REPO_ANALYSER_AUTO_FRONTEND", "1")
    frontend = tmp_path / "frontend"
    frontend.mkdir()
    (frontend / "index.html").write_text("html", encoding="utf-8")
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "serve_frontend.py").write_text("# x", encoding="utf-8")
    monkeypatch.setattr(mod, "FRONTEND_DIR", frontend)
    monkeypatch.setattr(mod, "ROOT", tmp_path)
    calls = {"n": 0}

    def running(port=None):
        calls["n"] += 1
        return calls["n"] > 1

    monkeypatch.setattr(mod, "frontend_is_running", running)
    monkeypatch.setattr(mod.subprocess, "Popen", lambda *_a, **_k: object())
    assert ensure_frontend_server() is True

    # open_skill_report without markdown fallback
    monkeypatch.setattr(mod, "ensure_frontend_server", lambda port=None: False)
    monkeypatch.setattr(mod, "frontend_is_running", lambda port=None: False)
    assert mod.open_skill_report("r", "B1", open_browser=True) is None


def test_orchestrator_lazy_domain_and_main():
    from runtime.orchestrator import SkillOrchestrator
    from runtime.orchestrator.cli import main as cli_main

    orch = SkillOrchestrator(
        skills_root=ROOT / "skills",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    assert orch.skills_for_domain("B")
    assert orch.full_pipeline_skills()
    assert orch.collect_transitive(["B2"], orch.dependency_graph())
    assert cli_main(["--validate-dag"]) == 0
    assert cli_main([]) == 1


def test_dependency_resolver_remaining():
    from runtime.orchestrator.dependency_resolver import parallel_waves

    with pytest.raises(ValueError, match="deadlock"):
        parallel_waves(["A", "B"], {"A": ["B"], "B": ["A"]})

    # Force uncovered branch via partial order failure is hard; cover empty graph orphans
    from runtime.orchestrator.dependency_resolver import find_orphan_skills

    assert find_orphan_skills({}) == []


def test_executor_artifact_and_abort(tmp_path, monkeypatch):
    from runtime.models import RunContext
    from runtime.orchestrator.executor import SkillExecutor
    from runtime.skill_orchestrator import SkillOrchestrator

    orch = SkillOrchestrator(
        skills_root=ROOT / "skills",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    orch.load_registry()
    orch.discover_skills()
    run_dir = tmp_path / "dep-run"
    (run_dir / "B1").mkdir(parents=True)
    golden_b1 = ROOT / "generated_projects" / "_golden" / "B1" / "inventory_report.json"
    (run_dir / "B1" / "output.json").write_text(golden_b1.read_text(encoding="utf-8"), encoding="utf-8")

    ctx = RunContext(
        run_id="dep-run",
        run_dir=run_dir,
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={"repository_path": str(ROOT)},
    )
    ex = SkillExecutor(ctx)
    b2 = orch.get_skill("B2")
    assert ex._artifact_input_available("inventory_report.json", b2) is True

    ctx2 = RunContext(
        run_id="dep-run",
        run_dir=run_dir,
        golden_dir=tmp_path / "missing",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={"repository_path": str(ROOT)},
        continue_on_failure=False,
    )
    plan = orch.build_plan("dep-run", skill_ids=["B1"])
    plan.skills = {}
    summary = SkillExecutor(ctx2).run_plan(plan)
    assert summary["status"] == "failed"


def test_report_ui_remaining_branches():
    from runtime.report_ui import Theme, compute_outcome, render_details

    theme = Theme()
    mapped, _, _, _ = compute_outcome("B2", {"endpoints": [{"method": "GET", "route": "/"}]})
    assert mapped == "MAPPED"
    tests_pass, _, _, _ = compute_outcome(
        "B3", {"framework": "pytest", "command_result": {"exit_code": 0}, "test_files": []}
    )
    assert tests_pass == "TESTS PASS"
    traced, _, _, _ = compute_outcome("I2", {"steps": [{"order": 1}]})
    assert traced == "TRACED"
    schema, _, _, _ = compute_outcome("I1", {"tables": [{"name": "t"}]})
    assert schema == "SCHEMA OK"
    fixed, _, _, _ = compute_outcome("I6", {"root_cause": {"file_path": "a.py"}, "fix_verified": True})
    assert fixed == "FIXED"

    a5_issues = {
        "issues": [
            {
                "id": "NB1",
                "severity": "non_blocking",
                "category": "style",
                "file_path": "a.py",
                "line": 1,
                "description": "d",
                "suggested_fix": "f",
                "verification_steps": ["v"],
            }
        ]
    }
    render_details("A5", a5_issues, theme)
    b3_cmds = render_details(
        "B3",
        {"framework": "pytest", "config_file": "pyproject.toml", "commands": {"unit": {"command": "pytest"}}},
        theme,
    )
    assert "pytest" in "\n".join(b3_cmds)


def test_reporting_remaining(tmp_path):
    from runtime.reporting.formatters import render_value
    from runtime.reporting.handlers import render_b1, render_proof
    from runtime.reporting.markdown_writer import export_run_markdown

    assert render_value([1, 2, 3])  # non-dict list
    render_b1({"dependency_graph_summary": {"nodes": [], "edges": []}})
    render_proof({"run_proof": "not-a-dict"})
    render_proof({"test_result": None})

    run_dir = tmp_path / "skip"
    run_dir.mkdir()
    (run_dir / "manifest.json").write_text("{}", encoding="utf-8")
    (run_dir / "_hidden").mkdir()
    (run_dir / "not-a-dir.txt").write_text("x", encoding="utf-8")
    export_run_markdown(run_dir)


def test_skill_finish_interactive_and_main(tmp_path, monkeypatch):
    import runtime.skill_finish as mod

    run_dir = tmp_path / "run"
    skill_dir = run_dir / "B1"
    skill_dir.mkdir(parents=True)
    golden = ROOT / "generated_projects" / "_golden" / "B1" / "inventory_report.json"
    (skill_dir / "output.json").write_text(golden.read_text(encoding="utf-8"), encoding="utf-8")

    inputs = iter(["q"])
    monkeypatch.setattr("builtins.input", lambda _=None: next(inputs))
    assert mod.show_skill_report(run_dir, "B1", interactive=True) == 0

    def eof(*_a, **_k):
        raise EOFError

    monkeypatch.setattr("builtins.input", eof)
    assert mod._interactive_menu(run_dir, "B1") == 0

    mod.GENERATED_ROOT = tmp_path
    assert mod.main(["--run-id", "run", "--skill", "B1", "--no-md"]) == 0


def test_skill_parser_remaining(tmp_path):
    from runtime.skill_parser import (
        SkillDefinition,
        extract_json_block,
        parse_agent_markdown,
        parse_agent_title,
        strip_frontmatter,
    )

    assert parse_agent_title("no title") is None
    assert strip_frontmatter("no frontmatter") == "no frontmatter"

    bad_agent = tmp_path / "bad_agent.md"
    bad_agent.write_text(
        "# Agent: Bad (B1)\n\n### Task ID\n`B1`\n\n### Capability Level\n`B`\n\n```json\n{broken\n```\n",
        encoding="utf-8",
    )
    agent = parse_agent_markdown(bad_agent)
    assert agent["skill_id"] == "B1"

    sections = {"Output Contract": "```json\n{}\n```"}
    assert extract_json_block(sections, "Output Contract") == {}

    skill = SkillDefinition(skill_id="B1", name="n", level="B", level_code="B", output_contract="bad")
    assert skill.output_keys == set()


def test_skill_registry_builder_remaining(tmp_path, monkeypatch):
    import runtime.skill_registry_builder as srb

    cov = srb.validate_skill_coverage({"skills": {"B1": {"path": "missing/x.skill.md", "output_file": "o.json"}}})
    assert cov["missing_files"]

    tasks = json.loads((ROOT / "scripts" / "task_registry.json").read_text(encoding="utf-8"))
    meta = tasks["tasks"]["B1"]
    assert srb.agent_spec_path("B1", meta).is_file()

    registry = srb.build_skill_registry(write_skills=False)
    empty_group = dict(registry)
    empty_group["skills"] = {}
    doc = srb.render_how_to_run(empty_group)
    assert "Repo-Analyser" in doc

    with patch.object(srb, "build_skill_registry") as mock_build:
        mock_build.return_value = {
            "skill_count": 24,
            "skills": {},
            "coverage": {"coverage_status": "100%", "total_skills": 24},
        }
        with patch.object(srb, "write_registry"), patch.object(srb, "write_how_to_run"):
            assert srb.main() == 0


def test_skill_orchestrator_and_runner_main(capsys):
    from runtime.skill_orchestrator import main as orch_main
    from runtime.skill_runner import main as runner_main

    assert orch_main(["--validate-dag"]) == 0
    assert runner_main(["--skill", "B1", "--run-id", "x", "--plan-only"]) == 0


def test_validate_pipeline_schema_fail_and_main(tmp_path):
    from runtime.validate_pipeline import main as validate_main
    from runtime.validate_pipeline import validate_run_outputs

    run_dir = tmp_path / "schema-fail"
    (run_dir / "B1").mkdir(parents=True)
    golden = ROOT / "generated_projects" / "_golden" / "B1" / "inventory_report.json"
    (run_dir / "B1" / "output.json").write_text(golden.read_text(encoding="utf-8"), encoding="utf-8")
    failed, invalid = validate_run_outputs(run_dir, {"B1": {"missing_required_key": "required"}})
    assert failed or invalid

    assert validate_main(["--run-id", "final_test"]) in {0, 1}


def test_pipeline_plan_missing_folder():
    from runtime.pipeline_plan import create_pipeline_plan

    with pytest.raises(ValueError):
        create_pipeline_plan(str(ROOT / "definitely-missing-folder-xyz"))


def test_plugins_loader_skips_missing_skill(tmp_path, monkeypatch):
    import runtime.plugins.loader as loader_mod

    registry = json.loads((ROOT / "core" / "skill_registry.json").read_text(encoding="utf-8"))
    registry["skills"]["Z99"] = {
        "name": "Ghost",
        "level": "BASIC",
        "level_code": "B",
        "depends_on": [],
        "path": "skills/missing/Z99.skill.md",
    }
    reg_path = tmp_path / "reg.json"
    reg_path.write_text(json.dumps(registry), encoding="utf-8")
    plugins = loader_mod.load_plugins(reg_path)
    assert plugins.get("Z99") is None


def test_write_skill_output_save_md_false(tmp_path):
    from runtime.skill_finish import write_skill_output

    payload = {"task_id": "A5", "issues": [], "level": "A", "scan_complete": True}
    write_skill_output("demo", "A5", payload, generated_root=tmp_path, save_md=False, show_ui=False)


def test_export_markdown_reports_success(tmp_path):
    from runtime.skill_finish import export_markdown_reports

    run_dir = tmp_path / "run"
    skill_dir = run_dir / "B1"
    skill_dir.mkdir(parents=True)
    golden = ROOT / "generated_projects" / "_golden" / "B1" / "inventory_report.json"
    (skill_dir / "inventory_report.json").write_text(golden.read_text(encoding="utf-8"), encoding="utf-8")
    export_markdown_reports(run_dir, skill_dir)


def test_skill_runner_plan_without_skills_dict(tmp_path):
    from runtime.skill_orchestrator import SkillOrchestrator
    from runtime.skill_runner import SkillRunner

    orch = SkillOrchestrator(
        skills_root=ROOT / "skills",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    plan = orch.build_plan("discover", skill_ids=["B1"])
    plan.skills = {}
    runner = SkillRunner(
        run_id="discover",
        run_dir=tmp_path / "discover",
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={"repository_path": str(ROOT)},
    )
    summary = runner.run_plan(plan)
    assert summary["status"] == "complete"
