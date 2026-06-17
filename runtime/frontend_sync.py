"""Publish skill run results to the local frontend (no deploy)."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from runtime.deterministic import canonical_json_dumps
from runtime.report_renderer import SKILL_TITLES, render_report
from runtime.report_ui import compute_outcome, load_skill_meta
from runtime.skill_constants import cursor_slash_command

ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT / "frontend"
FRONTEND_DATA = FRONTEND_DIR / "data"
DEFAULT_PORT = 8765
MAX_HISTORY = 50
_STARTUP_TIMEOUT_S = 5.0


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _frontend_port() -> int:
    raw = os.environ.get("REPO_ANALYSER_FRONTEND_PORT", str(DEFAULT_PORT))
    try:
        return int(raw)
    except ValueError:
        return DEFAULT_PORT


def frontend_is_running(port: int | None = None) -> bool:
    port = port or _frontend_port()
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.25):
            return True
    except OSError:
        return False


def _auto_frontend_enabled() -> bool:
    return os.environ.get("REPO_ANALYSER_AUTO_FRONTEND", "1") != "0"


def _auto_start_frontend_enabled() -> bool:
    return os.environ.get("REPO_ANALYSER_AUTO_START_FRONTEND", "1") != "0"


def _ensure_frontend_data() -> bool:
    """Build frontend/data/skills.json when missing."""
    skills_json = FRONTEND_DATA / "skills.json"
    if skills_json.is_file():
        return True
    build_script = ROOT / "tools" / "build_frontend.py"
    if not build_script.is_file():
        return False
    try:
        subprocess.run(
            [sys.executable, str(build_script)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return False
    return skills_json.is_file()


def ensure_frontend_server(port: int | None = None) -> bool:
    """Start the local frontend server in the background when it is not already running."""
    port = port or _frontend_port()
    if frontend_is_running(port):
        return True
    if not _auto_frontend_enabled() or not _auto_start_frontend_enabled():
        return False
    if not (FRONTEND_DIR / "index.html").is_file():
        return False
    if not _ensure_frontend_data():
        return False

    serve_script = ROOT / "tools" / "serve_frontend.py"
    if not serve_script.is_file():
        return False

    try:
        subprocess.Popen(
            [sys.executable, str(serve_script), "--no-open", "--port", str(port)],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        return False

    deadline = time.monotonic() + _STARTUP_TIMEOUT_S
    while time.monotonic() < deadline:
        if frontend_is_running(port):
            return True
        time.sleep(0.1)
    return False


def report_url(run_id: str, skill_id: str, port: int | None = None) -> str:
    port = port or _frontend_port()
    skill_id = skill_id.upper()
    return f"http://127.0.0.1:{port}/?run={run_id}&skill={skill_id}&live=1"


def open_skill_report(
    run_id: str,
    skill_id: str,
    *,
    markdown_path: Path | None = None,
    open_browser: bool | None = None,
) -> str | None:
    """Open the live report in the browser, starting the frontend server if needed."""
    if open_browser is None:
        open_browser = _auto_frontend_enabled()
    if not open_browser:
        return None

    port = _frontend_port()
    if ensure_frontend_server(port) and frontend_is_running(port):
        url = report_url(run_id, skill_id, port)
        webbrowser.open(url)
        return url

    if markdown_path and markdown_path.is_file():
        uri = markdown_path.resolve().as_uri()
        webbrowser.open(uri)
        return uri
    return None


def _runs_dir() -> Path:
    path = FRONTEND_DATA / "runs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _load_index() -> dict[str, Any]:
    path = FRONTEND_DATA / "runs_index.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"runs": {}}


def _save_index(doc: dict[str, Any]) -> None:
    (FRONTEND_DATA / "runs_index.json").write_text(
        canonical_json_dumps(doc),
        encoding="utf-8",
    )


def _load_live() -> dict[str, Any]:
    path = FRONTEND_DATA / "live.json"
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"latest": None, "history": []}


def publish_skill_run(
    run_id: str,
    skill_id: str,
    payload: dict[str, Any],
    *,
    open_browser: bool | None = None,
) -> Path:
    """Copy skill output into frontend/data for the local UI."""
    FRONTEND_DATA.mkdir(parents=True, exist_ok=True)
    skill_id = skill_id.upper()
    meta = load_skill_meta(skill_id)
    status_label, tone, headline, metrics = compute_outcome(skill_id, payload)

    run_skill_dir = _runs_dir() / run_id
    run_skill_dir.mkdir(parents=True, exist_ok=True)

    json_rel = f"data/runs/{run_id}/{skill_id}.json"
    md_rel = f"data/runs/{run_id}/{skill_id}.md"
    json_path = FRONTEND_DATA / "runs" / run_id / f"{skill_id}.json"
    md_path = FRONTEND_DATA / "runs" / run_id / f"{skill_id}.md"

    json_path.write_text(canonical_json_dumps(payload), encoding="utf-8")
    md_path.write_text(render_report(payload, task_id=skill_id), encoding="utf-8")

    entry = {
        "run_id": run_id,
        "skill_id": skill_id,
        "skill_name": meta.get("name") or SKILL_TITLES.get(skill_id, skill_id),
        "level": meta.get("level", ""),
        "slash_command": cursor_slash_command(skill_id),
        "updated_at": payload.get("generated_at") or _now_iso(),
        "published_at": _now_iso(),
        "status_label": status_label,
        "status_tone": tone,
        "headline": headline,
        "metrics": [{"label": k, "value": v} for k, v in metrics],
        "json_url": json_rel,
        "markdown_url": md_rel,
        "output_path": f"generated_projects/{run_id}/{skill_id}/output.json",
    }

    live = _load_live()
    live["latest"] = entry
    history = [item for item in live.get("history", []) if not (
        item.get("run_id") == run_id and item.get("skill_id") == skill_id
    )]
    history.insert(0, entry)
    live["history"] = history[:MAX_HISTORY]
    (FRONTEND_DATA / "live.json").write_text(canonical_json_dumps(live), encoding="utf-8")

    index = _load_index()
    runs = index.setdefault("runs", {})
    run_entry = runs.setdefault(run_id, {"skills": [], "updated_at": entry["published_at"]})
    skills = [s for s in run_entry.get("skills", []) if s != skill_id]
    skills.append(skill_id)
    run_entry["skills"] = sorted(skills)
    run_entry["updated_at"] = entry["published_at"]
    _save_index(index)

    opened = open_skill_report(
        run_id,
        skill_id,
        markdown_path=md_path,
        open_browser=open_browser,
    )
    if opened:
        print(f"Opened report → {opened}", flush=True)

    return json_path


def sync_from_skill_dir(run_dir: Path, skill_id: str, *, open_browser: bool | None = None) -> Path | None:
    """Load output.json from a skill directory and publish to frontend."""
    from runtime.report_renderer import load_skill_payload

    skill_dir = run_dir / skill_id.upper()
    task_id, payload = load_skill_payload(skill_dir)
    if not payload:
        return None
    return publish_skill_run(run_dir.name, task_id or skill_id, payload, open_browser=open_browser)
