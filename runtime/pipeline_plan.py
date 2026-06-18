"""Build full-pipeline execution plans for the frontend wizard."""

from __future__ import annotations

import re
from pathlib import Path

from runtime.skill_constants import cursor_slash_command
from runtime.skill_orchestrator import SkillOrchestrator
from runtime.skill_parser import task_sort_key


def run_id_from_path(repository_path: str) -> str:
    """Derive a stable run_id from the target folder name."""
    name = Path(repository_path).expanduser().resolve().name
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", name).strip("-").lower()
    return slug or "target-repo"


def create_pipeline_plan(repository_path: str) -> dict:
    """Validate target folder and return DAG-ordered skill list for all 24 agents."""
    path = Path(repository_path).expanduser().resolve()
    if not path.is_dir():
        raise ValueError(f"Folder not found: {path}")

    orchestrator = SkillOrchestrator()
    orchestrator.load_registry()
    all_skills = orchestrator.full_pipeline_skills()
    order = orchestrator.topological_sort(all_skills)
    registry = orchestrator._registry.get("skills", {})

    skills = []
    for skill_id in order:
        meta = registry.get(skill_id, {})
        skills.append(
            {
                "task_id": skill_id,
                "name": meta.get("name", skill_id),
                "level": meta.get("level", ""),
                "level_code": meta.get("level_code", skill_id[0]),
                "slash_command": cursor_slash_command(skill_id),
                "depends_on": sorted(meta.get("depends_on", []), key=task_sort_key),
            }
        )

    run_id = run_id_from_path(str(path))
    return {
        "ok": True,
        "run_id": run_id,
        "repository_path": str(path),
        "execution_order": order,
        "skills": skills,
        "total": len(order),
    }
