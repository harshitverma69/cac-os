"""Build execution plans from registry and skill definitions."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

from runtime.orchestrator.dependency_resolver import (
    detect_cycles,
    find_missing_dependencies,
    find_orphan_skills,
    parallel_waves,
    topological_sort,
)
from runtime.skill_parser import LEVEL_SKILL_DIRS, SkillDefinition, parse_skill_markdown, task_sort_key

ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_ROOT = ROOT / "skills"
CORE_REGISTRY_PATH = ROOT / "core" / "skill_registry.json"


@dataclass
class ExecutionPlan:
    run_id: str
    requested: list[str]
    execution_order: list[str]
    parallel_waves: list[list[str]]
    skills: dict[str, SkillDefinition] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "run_id": self.run_id,
            "requested": self.requested,
            "execution_order": self.execution_order,
            "parallel_waves": self.parallel_waves,
            "skill_paths": {sid: skill.source_path for sid, skill in self.skills.items()},
        }


def load_registry(registry_path: Path = CORE_REGISTRY_PATH) -> dict[str, Any]:
    if not registry_path.is_file():
        raise FileNotFoundError(f"Skill registry not found: {registry_path}")
    return cast(dict[str, Any], json.loads(registry_path.read_text(encoding="utf-8")))


def discover_skills(skills_root: Path = SKILLS_ROOT) -> dict[str, SkillDefinition]:
    skills: dict[str, SkillDefinition] = {}

    for level_dir in LEVEL_SKILL_DIRS.values():
        folder = skills_root / level_dir
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.skill.md")):
            skill = parse_skill_markdown(path, ROOT)
            skills[skill.skill_id] = skill

    master = skills_root / "run_all_skills.skill.md"
    if master.is_file():
        pipeline = parse_skill_markdown(master, ROOT)
        skills[pipeline.skill_id] = pipeline

    return skills


def dependency_graph(registry: dict, skill_ids: list[str] | None = None) -> dict[str, list[str]]:
    registry_skills = registry.get("skills", {})
    graph: dict[str, list[str]] = {}

    keys = skill_ids or sorted(registry_skills.keys(), key=task_sort_key)
    for skill_id in keys:
        meta = registry_skills.get(skill_id, {})
        graph[skill_id] = list(meta.get("depends_on", []))

    return graph


def skills_for_domain(registry: dict, domain: str) -> list[str]:
    domain = domain.upper()
    if domain not in {"B", "I", "A", "D"}:
        raise ValueError(f"Unknown domain: {domain}")

    return sorted(
        (skill_id for skill_id, meta in registry.get("skills", {}).items() if meta.get("level_code") == domain),
        key=task_sort_key,
    )


def full_pipeline_skills(registry: dict) -> list[str]:
    return sorted(registry.get("skills", {}).keys(), key=task_sort_key)


def build_plan(
    run_id: str,
    registry: dict,
    skills: dict[str, SkillDefinition],
    skill_ids: list[str] | None = None,
    domain: str | None = None,
    full_pipeline: bool = False,
) -> ExecutionPlan:
    if full_pipeline:
        requested = full_pipeline_skills(registry)
    elif domain:
        requested = skills_for_domain(registry, domain)
    elif skill_ids:
        requested = [skill_id.upper() for skill_id in skill_ids]
    else:
        raise ValueError("Provide skill_ids, domain, or full_pipeline=True")

    graph = dependency_graph(registry)
    order = topological_sort(requested, graph)
    waves = parallel_waves(order, graph)
    plan_skills = {skill_id: skills[skill_id] for skill_id in order if skill_id in skills}

    return ExecutionPlan(
        run_id=run_id,
        requested=requested,
        execution_order=order,
        parallel_waves=waves,
        skills=plan_skills,
    )


def validate_dag(registry: dict) -> dict:
    graph = dependency_graph(registry)
    cycles = detect_cycles(graph)
    missing = find_missing_dependencies(graph)
    orphans = find_orphan_skills(graph)

    all_skill_ids = sorted(graph.keys(), key=task_sort_key)
    order_a = topological_sort(all_skill_ids, graph) if not cycles and not missing else []
    order_b = topological_sort(all_skill_ids, graph) if not cycles and not missing else []
    order_stable = order_a == order_b
    valid = not cycles and not missing and not orphans and order_stable

    return {
        "dag_status": "VALID" if valid else "INVALID",
        "cycles": cycles,
        "missing_dependencies": missing,
        "orphan_skills": orphans,
        "topological_order_stable": order_stable,
        "execution_order": order_a,
    }
