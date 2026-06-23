"""Full coverage for runtime.reporting submodules."""

from __future__ import annotations

from pathlib import Path

from runtime.reporting.formatters import collect_headers, render_value, stringify, table
from runtime.reporting.handlers import (
    TASK_HANDLERS,
    render_b1,
    render_b2,
    render_b3,
    render_generic,
    render_i1,
    render_i2,
    render_issues,
    render_proof,
)
from runtime.reporting.loader import find_skill_json, load_skill_payload
from runtime.reporting.markdown_writer import export_run_markdown, export_skill_markdown
from runtime.reporting.meta import meta_section
from runtime.reporting.renderer import render_report

ROOT = Path(__file__).resolve().parent.parent


def test_formatters_all_types():
    assert stringify(None) == ""
    assert stringify([1, 2]) == "[1, 2]"
    assert render_value(None) == "_null_"
    assert render_value(True) == "true"
    assert render_value(42) == "42"
    assert render_value("line1\nline2").startswith("```")
    assert render_value([]) == "_Empty list_"
    assert render_value([{"a": 1, "b": 2}])
    assert render_value({}) == "_Empty object_"
    assert render_value({"k": "v"})
    assert collect_headers([{"a": 1}, {"b": 2}]) == ["a", "b"]
    assert table(["H"], [("c",)])


def test_meta_section_with_warnings_and_limitations():
    payload = {
        "level": "B",
        "warnings": ["w1"],
        "limitations": ["l1"],
    }
    md = meta_section(payload)
    assert "Warnings" in md
    assert "Known Limitations" in md


def test_loader_branches(tmp_path: Path):
    assert find_skill_json(tmp_path / "missing") is None
    empty = tmp_path / "empty"
    empty.mkdir()
    assert find_skill_json(empty) is None
    (empty / "custom.json").write_text('{"task_id": "X1"}', encoding="utf-8")
    assert find_skill_json(empty).name == "custom.json"
    task_id, payload = load_skill_payload(empty)
    assert task_id == "X1"
    assert payload


def test_handlers_b1_empty_and_edges():
    assert "No modules" in render_b1({"modules": [], "artifacts": {}})
    b1 = render_b1(
        {
            "modules": [{"name": "m", "path": "p"}],
            "artifacts": {"services": [{"name": "s", "file_path": "s.py"}]},
            "dependency_graph_summary": {"nodes": [], "edges": ["A->B", "C"]},
        }
    )
    assert "A" in b1


def test_handlers_b2_b3_i1_i2():
    assert "No endpoints" in render_b2({})
    assert render_b2(
        {"endpoints": [{"method": "GET", "route": "/x"}], "frontend_routes": [{"path": "/f", "source_file": "f.ts"}]}
    )
    assert render_b3({"framework": "pytest", "commands": ["pytest"], "test_files": ["t.py"] * 60})
    assert render_b3({"framework": "pytest", "test_commands": [{"command": "pytest"}]})
    assert "No tables" in render_i1({})
    assert render_i1({"tables": ["plain"], "mermaid_er": "erDiagram\n  A {}"})
    assert render_i1({"entities": [{"name": "t", "source_file": "a.py", "columns": [{"name": "id"}]}]})
    assert "No steps" in render_i2({})
    assert render_i2(
        {
            "steps": [{"order": 1, "layer": "ctrl", "symbol": "h", "file_path": "a.py"}],
            "sequence_diagram_mermaid": "sequenceDiagram\n  A->>B: hi",
        }
    )


def test_handlers_issues_and_proof_and_generic():
    assert "None" in render_issues({})
    assert render_issues({"issues": [{"title": "t", "severity": "low", "description": "d"}]})
    assert render_issues({"issues": ["plain"]})
    assert render_proof({"build_proof": {"cmd": "make"}})
    assert render_generic({"task_id": "X", "custom_field": "value"})


def test_all_task_handlers_callable():
    for handler in TASK_HANDLERS.values():
        assert callable(handler)


def test_markdown_writer_run_index(tmp_path: Path):
    run_dir = tmp_path / "run"
    skill_dir = run_dir / "B1"
    skill_dir.mkdir(parents=True)
    golden = ROOT / "generated_projects" / "_golden" / "B1" / "inventory_report.json"
    (skill_dir / "inventory_report.json").write_text(golden.read_text(encoding="utf-8"), encoding="utf-8")
    (run_dir / "manifest.json").write_text('{"repository_path": "/repo"}', encoding="utf-8")
    written = export_run_markdown(run_dir)
    assert (run_dir / "REPORT.md").is_file()
    assert written


def test_render_report_empty_body():
    md = render_report({"task_id": "D1", "scan_complete": True}, task_id="D1")
    assert "D1" in md


def test_export_skill_markdown_custom_path(tmp_path: Path):
    skill_dir = tmp_path / "B1"
    skill_dir.mkdir()
    golden = ROOT / "generated_projects" / "_golden" / "B1" / "inventory_report.json"
    (skill_dir / "inventory_report.json").write_text(golden.read_text(encoding="utf-8"), encoding="utf-8")
    out = tmp_path / "custom.md"
    path = export_skill_markdown(skill_dir, output_path=out)
    assert path == out
