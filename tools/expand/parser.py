"""Parse blueprint sections and agent paths."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
GOLDEN_DIR = ROOT / "generated_projects" / "_golden"
TASKS = json.loads((ROOT / "scripts" / "task_registry.json").read_text(encoding="utf-8"))["tasks"]


def _extract_section_text(text: str, heading: str) -> str:
    for prefix in ("###", "##"):
        pattern = rf"^{prefix} {re.escape(heading)}\s*\n(.*?)(?=\n(?:###|##) |\Z)"
        match = re.search(pattern, text, re.DOTALL | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return ""


def _blueprint_text(task_id: str) -> str:
    level = TASKS[task_id]["level"]
    path = ROOT / "eval_blueprints" / level / f"{task_id}_blueprint.md"
    return path.read_text(encoding="utf-8")


def _checklist_lines(section: str) -> str:
    lines: list[str] = []
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("- [ ]"):
            lines.append(f"- {stripped[5:].strip()}")
        elif stripped.startswith("- "):
            lines.append(stripped)
    return "\n".join(lines) if lines else "- See eval blueprint."


def _golden_schema(task_id: str) -> str:
    output_file = TASKS[task_id]["output_file"]
    path = GOLDEN_DIR / task_id / output_file
    payload = json.loads(path.read_text(encoding="utf-8"))
    return json.dumps(payload, indent=2, sort_keys=True)


def _slug(task_id: str) -> str:
    return TASKS[task_id]["slug"]


def _agent_path(task_id: str) -> Path:
    meta = TASKS[task_id]
    folder = meta["folder"]
    slug = meta["slug"]
    return ROOT / "agents" / folder / f"{task_id}_{slug}_agent.md"


def _cursor_name(task_id: str) -> str:
    return f"repo-analyser-{task_id.lower()}-{_slug(task_id).replace('_', '-')}"


# Per-agent procedural phases (title + body markdown)
