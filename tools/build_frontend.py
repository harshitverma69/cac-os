#!/usr/bin/env python3
"""Generate frontend/data/skills.json from Repo-Analyser registry."""

from __future__ import annotations

import json
from pathlib import Path

from runtime.skill_constants import cursor_slash_command

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "core" / "skill_registry.json"
TASKS_PATH = ROOT / "scripts" / "task_registry.json"
OUT_PATH = ROOT / "frontend" / "data" / "skills.json"

LEVEL_ORDER = {"B": 0, "I": 1, "A": 2, "D": 3}
LEVEL_LABELS = {
    "B": "Basic",
    "I": "Intermediate",
    "A": "Advanced",
    "D": "Infra / DevOps",
}


def sort_key(task_id: str) -> tuple[int, int]:
    return (LEVEL_ORDER.get(task_id[0], 9), int(task_id[1:]))


def run_steps(task_id: str) -> list[dict[str, str]]:
    return [
        {
            "title": "Open in Cursor",
            "body": f"Type `{cursor_slash_command(task_id)}` in chat, or read the agent spec manually.",
        },
        {
            "title": "Read specs (in order)",
            "body": "Agent spec → Skill spec → Eval blueprint → docs/HOW_TO_RUN.md",
        },
        {
            "title": "Execute the task",
            "body": "Follow phases in the agent spec. For repo tasks, set `repository_path`. "
            "For build tasks, produce code + tests + README with real command proofs.",
        },
        {
            "title": "Write output JSON + report",
            "body": (
                f"`python3 -m runtime.skill_finish write --run-id <run_id> --skill {task_id} "
                f"--payload-file payload.json`"
            ),
        },
        {
            "title": "Verify (optional)",
            "body": (f"`make skill-done RUN_ID=<run_id> SKILL={task_id}` — re-opens terminal + browser report"),
        },
    ]


def make_entry(task_id: str, meta: dict, task_meta: dict) -> dict:
    deps = meta.get("depends_on") or task_meta.get("depends_on") or []
    output_file = meta.get("output_file") or task_meta.get("output_file", "output.json")
    return {
        "task_id": task_id,
        "name": meta.get("name", task_id),
        "level": meta.get("level", LEVEL_LABELS.get(task_id[0], task_id[0])),
        "level_code": task_id[0],
        "description": meta.get("description", ""),
        "depends_on": sorted(deps, key=sort_key),
        "agent_spec": meta.get("agent_source", ""),
        "skill_spec": meta.get("path", ""),
        "blueprint": meta.get("blueprint", f"eval_blueprints/{task_meta['level']}/{task_id}_blueprint.md"),
        "slash_command": cursor_slash_command(task_id),
        "output_json": f"generated_projects/{{run_id}}/{task_id}/output.json",
        "golden_json": f"generated_projects/_golden/{task_id}/{output_file}",
        "make_run": f"make run-skill SKILL={task_id} RUN_ID=<run_id>",
        "finish_command": (
            f"python3 -m runtime.skill_finish write --run-id <run_id> --skill {task_id} " f"--payload-file payload.json"
        ),
        "run_steps": run_steps(task_id),
    }


def main() -> int:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    tasks = json.loads(TASKS_PATH.read_text(encoding="utf-8"))["tasks"]
    skills = registry.get("skills", {})

    entries = [make_entry(task_id, skills[task_id], tasks[task_id]) for task_id in sorted(skills.keys(), key=sort_key)]

    payload = {
        "project": "Repo-Analyser",
        "skill_count": len(entries),
        "levels": [{"code": code, "label": LEVEL_LABELS[code]} for code in ("B", "I", "A", "D")],
        "setup": {
            "title": "First-time setup",
            "steps": [
                "git clone https://github.com/harshitverma69/Repo-Analyser.git",
                "cd Repo-Analyser",
                "make build-skills",
                "make install-cursor-skills",
                "make build-frontend",
                "Restart Cursor completely",
                "In chat: / then pick a /repo-analyser-* command",
            ],
            "note": "Shortcut: make setup runs the three make targets above plus validate. After each skill, reports auto-open in the browser (Live runs tab).",
        },
        "skills": entries,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"OK: wrote {OUT_PATH.relative_to(ROOT)} ({len(entries)} skills)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
