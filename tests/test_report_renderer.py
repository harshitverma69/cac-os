"""Tests for Markdown report rendering."""

from __future__ import annotations

import json
from pathlib import Path

from runtime.report_renderer import export_run_markdown, export_skill_markdown, render_report

ROOT = Path(__file__).resolve().parent.parent


def test_render_b1_golden():
    golden = ROOT / "generated_projects" / "_golden" / "B1" / "inventory_report.json"
    payload = json.loads(golden.read_text(encoding="utf-8"))
    md = render_report(payload, task_id="B1")
    assert "# B1 — Repo Artifact Inventory" in md
    assert "## Summary" in md
    assert "OrderService" in md


def test_export_master_mapping_run():
    run_dir = ROOT / "generated_projects" / "master-mapping"
    if not (run_dir / "B1" / "output.json").is_file():
        return

    paths = export_run_markdown(run_dir)
    assert (run_dir / "REPORT.md").is_file()
    assert (run_dir / "B1" / "output.md").is_file()
    assert any(p.name == "output.md" for p in paths)

    md = (run_dir / "B1" / "output.md").read_text(encoding="utf-8")
    assert "MasterMappingController" in md
    assert "## Artifacts" in md


def test_export_skill_markdown(tmp_path: Path):
    skill_dir = tmp_path / "B1"
    skill_dir.mkdir()
    payload = {
        "task_id": "B1",
        "level": "B",
        "files_scanned": 1,
        "modules": [{"name": "app", "path": "app/"}],
        "artifacts": {
            "controllers": [{"name": "HealthController", "file_path": "app/Health.java"}],
            "classes": [],
            "interfaces": [],
            "services": [],
            "models": [],
            "repositories": [],
            "jobs": [],
            "consumers": [],
            "configurations": [],
            "utilities": [],
        },
        "dependency_graph_summary": {"nodes": ["app"], "edges": []},
        "limitations": [],
    }
    (skill_dir / "output.json").write_text(json.dumps(payload), encoding="utf-8")
    md_path = export_skill_markdown(skill_dir)
    assert md_path.name == "output.md"
    assert "HealthController" in md_path.read_text(encoding="utf-8")
