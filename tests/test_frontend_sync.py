"""Tests for frontend_sync publish hook."""

from __future__ import annotations

import json
from pathlib import Path

from runtime.frontend_sync import (
    ensure_frontend_server,
    open_skill_report,
    publish_skill_run,
    report_url,
)

ROOT = Path(__file__).resolve().parent.parent


def test_publish_skill_run_writes_live_and_run_files(tmp_path, monkeypatch):
    monkeypatch.setenv("REPO_ANALYSER_AUTO_FRONTEND", "0")
    import runtime.frontend_sync as mod

    monkeypatch.setattr(mod, "FRONTEND_DATA", tmp_path)

    payload = {
        "task_id": "I1",
        "level": "I",
        "generated_at": "2026-06-17T12:00:00Z",
        "scan_complete": True,
        "tables": [{"name": "t", "source_file": "a.py", "columns": [], "primary_keys": ["id"], "entity": "T"}],
        "relationships": [],
        "mermaid_er": "erDiagram\n  t {}",
        "warnings": [],
    }

    path = publish_skill_run("demo-run", "I1", payload)
    assert path.is_file()

    live = json.loads((tmp_path / "live.json").read_text(encoding="utf-8"))
    assert live["latest"]["skill_id"] == "I1"
    assert live["latest"]["run_id"] == "demo-run"
    assert (tmp_path / "runs" / "demo-run" / "I1.json").is_file()
    assert (tmp_path / "runs" / "demo-run" / "I1.md").is_file()


def test_report_url_includes_live_tab_params():
    url = report_url("repolens", "i1", port=8765)
    assert url == "http://127.0.0.1:8765/?run=repolens&skill=I1&live=1"


def test_open_skill_report_starts_server_and_opens_browser(monkeypatch):
    import runtime.frontend_sync as mod

    monkeypatch.setenv("REPO_ANALYSER_AUTO_FRONTEND", "1")
    monkeypatch.setenv("REPO_ANALYSER_AUTO_START_FRONTEND", "1")
    monkeypatch.setattr(mod, "ensure_frontend_server", lambda port=None: True)
    monkeypatch.setattr(mod, "frontend_is_running", lambda port=None: True)

    opened: list[str] = []
    monkeypatch.setattr(mod.webbrowser, "open", lambda url: opened.append(url) or True)

    url = open_skill_report("repolens", "I1")
    assert url == "http://127.0.0.1:8765/?run=repolens&skill=I1&live=1"
    assert opened == [url]


def test_ensure_frontend_server_skips_when_disabled(monkeypatch):
    import runtime.frontend_sync as mod

    monkeypatch.setenv("REPO_ANALYSER_AUTO_FRONTEND", "0")
    monkeypatch.setattr(mod, "frontend_is_running", lambda port=None: False)
    assert ensure_frontend_server() is False
