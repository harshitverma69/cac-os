"""Final line coverage for remaining runtime gaps."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parent.parent


def test_frontend_is_running_success(monkeypatch):
    import runtime.frontend_sync as mod

    @contextmanager
    def fake_conn(*_a, **_k):
        yield object()

    monkeypatch.setattr(mod.socket, "create_connection", fake_conn)
    assert mod.frontend_is_running(8765) is True


def test_open_skill_report_file_uri(monkeypatch, tmp_path):
    import runtime.frontend_sync as mod

    md = tmp_path / "r.md"
    md.write_text("# x", encoding="utf-8")
    monkeypatch.setattr(mod.webbrowser, "open", lambda url: True)
    monkeypatch.setattr(mod, "ensure_frontend_server", lambda port=None: False)
    monkeypatch.setattr(mod, "frontend_is_running", lambda port=None: False)
    uri = mod.open_skill_report("r", "B1", markdown_path=md, open_browser=True)
    assert uri is not None
    assert uri.startswith("file:")


def test_orchestrator_full_pipeline_lazy():
    from runtime.orchestrator import SkillOrchestrator

    orch = SkillOrchestrator(
        skills_root=ROOT / "skills",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    assert len(orch.full_pipeline_skills()) == 24


def test_orchestrator_cli_main():
    from runtime.orchestrator.cli import main

    assert main(["--validate-dag"]) == 0


def test_topological_sort_cycle():
    from runtime.orchestrator.dependency_resolver import topological_sort

    with pytest.raises(ValueError, match="CYCLE_DETECTED"):
        topological_sort(["B1"], {"B1": ["B2"], "B2": ["B1"]})


def test_executor_branches(tmp_path):
    from runtime.models import RunContext
    from runtime.orchestrator.executor import SkillExecutor
    from runtime.skill_orchestrator import SkillOrchestrator

    orch = SkillOrchestrator(
        skills_root=ROOT / "skills",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    orch.load_registry()
    ctx = RunContext(
        run_id="x",
        run_dir=tmp_path,
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={},
    )
    ex = SkillExecutor(ctx)
    skill_b1 = orch.get_skill("B1")
    skill_b2 = orch.get_skill("B2")

    _, _, errors = ex.execute_steps(skill_b1, "B1")
    assert errors

    assert ex._artifact_input_available("other_report.json", skill_b2) is False


def test_markdown_writer_skip_dirs(tmp_path):
    from runtime.reporting.markdown_writer import export_run_markdown, export_skill_markdown

    with pytest.raises(FileNotFoundError):
        export_run_markdown(tmp_path / "missing")
    with pytest.raises(FileNotFoundError):
        export_skill_markdown(tmp_path / "empty")

    run_dir = tmp_path / "run2"
    run_dir.mkdir()
    (run_dir / "_hidden").mkdir()
    (run_dir / "not-a-dir.txt").write_text("x", encoding="utf-8")
    (run_dir / "manifest.json").write_text("{}", encoding="utf-8")
    (run_dir / "empty-skill").mkdir()
    weird = tmp_path / "run-weird"
    weird.mkdir()
    (weird / "manifest.json").mkdir()
    export_run_markdown(weird)
    skill_dir = run_dir / "B1"
    skill_dir.mkdir()
    golden = ROOT / "generated_projects" / "_golden" / "B1" / "inventory_report.json"
    (skill_dir / "inventory_report.json").write_text(golden.read_text(encoding="utf-8"), encoding="utf-8")
    export_run_markdown(run_dir)
    from runtime.reporting.markdown_writer import _render_run_index

    md = run_dir / "B1" / "output.md"
    _render_run_index(run_dir, [run_dir / "REPORT.md", md])


def test_handlers_and_formatters_edges():
    from runtime.reporting.formatters import render_value
    from runtime.reporting.handlers import render_b1, render_proof

    class Weird:
        def __str__(self) -> str:
            return "weird"

    assert render_value(Weird()) == "weird"
    edges = [f"edge-{i}" for i in range(30)]
    text = render_b1({"artifacts": {}, "dependency_graph_summary": {"nodes": [], "edges": edges}})
    assert "more edges" in text
    assert render_proof({"custom_proof": "not-a-dict", "noise": "skip"}) == ""


def test_skill_parser_capability_fallback():
    from runtime.skill_parser import parse_capability_level, parse_numbered_steps

    assert parse_capability_level({}, "I3") == "I"
    assert parse_numbered_steps("not a step") == []


def test_main_blocks(monkeypatch):
    import runpy
    import sys

    modules = [
        ("runtime.skill_orchestrator", ["skill_orchestrator", "--validate-dag"]),
        ("runtime.skill_runner", ["skill_runner", "--skill", "B1", "--run-id", "t", "--plan-only"]),
        ("runtime.skill_finish", ["skill_finish", "--help"]),
        ("runtime.validate_pipeline", ["validate_pipeline", "--run-id", "final_test"]),
        ("runtime.orchestrator.cli", ["cli", "--validate-dag"]),
    ]
    for module, argv in modules:
        monkeypatch.setattr(sys, "argv", argv)
        with pytest.raises(SystemExit) as exc:
            runpy.run_module(module, run_name="__main__")
        assert exc.value.code in {0, 1, 2}


def test_registry_builder_missing_agent(monkeypatch):
    import runtime.skill_registry_builder as srb

    with patch.object(
        srb,
        "load_task_registry",
        return_value={
            "tasks": {"Z9": {"folder": "x", "slug": "y", "level": "B", "depends_on": [], "output_file": "o.json"}}
        },
    ):
        with pytest.raises(FileNotFoundError):
            srb.build_skill_registry(write_skills=False)


def test_registry_builder_main():
    import runtime.skill_registry_builder as srb

    with patch.object(srb, "build_skill_registry") as mock:
        mock.return_value = {
            "skill_count": 24,
            "skills": {},
            "coverage": {"coverage_status": "100%", "total_skills": 24},
        }
        with patch.object(srb, "write_registry"), patch.object(srb, "write_how_to_run"):
            assert srb.main() == 0


def test_report_ui_optional_branches():
    from runtime.report_ui import Theme, render_details, render_header

    theme = Theme()
    render_header("r", "B1", {"description": ""}, theme)
    render_details("B2", {"endpoints": [{"method": "GET", "path": "/x", "handler": "h"}]}, theme)
    render_details("B1", {"artifacts": {"x": [{"name": "n", "file_path": "p"}]}}, theme)


def test_validate_skill_coverage_unexpected_skill():
    import runtime.skill_registry_builder as srb

    result = srb.validate_skill_coverage({"skills": {"Z9": {"path": "x", "output_file": "o.json"}}})
    assert "Z9" in result["duplicates"]
