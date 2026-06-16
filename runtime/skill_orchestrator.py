"""Deterministic skill DAG orchestrator."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from runtime.skill_parser import LEVEL_SKILL_DIRS, SkillDefinition, parse_skill_markdown, task_sort_key

ROOT = Path(__file__).resolve().parent.parent
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


class SkillOrchestrator:
    def __init__(self, skills_root: Path | None = None, registry_path: Path | None = None):
        self.skills_root = skills_root or SKILLS_ROOT
        self.registry_path = registry_path or CORE_REGISTRY_PATH
        self._skills: dict[str, SkillDefinition] = {}
        self._registry: dict = {}

    def load_registry(self) -> dict:
        if not self.registry_path.is_file():
            raise FileNotFoundError(f"Skill registry not found: {self.registry_path}")
        self._registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        return self._registry

    def discover_skills(self) -> dict[str, SkillDefinition]:
        skills: dict[str, SkillDefinition] = {}

        for level_dir in LEVEL_SKILL_DIRS.values():
            folder = self.skills_root / level_dir
            if not folder.is_dir():
                continue
            for path in sorted(folder.glob("*.skill.md")):
                skill = parse_skill_markdown(path, ROOT)
                skills[skill.skill_id] = skill

        master = self.skills_root / "run_all_skills.skill.md"
        if master.is_file():
            pipeline = parse_skill_markdown(master, ROOT)
            skills[pipeline.skill_id] = pipeline

        self._skills = skills
        return skills

    def get_skill(self, skill_id: str) -> SkillDefinition:
        if not self._skills:
            self.discover_skills()
        skill = self._skills.get(skill_id.upper())
        if skill is None:
            raise KeyError(f"Unknown skill: {skill_id}")
        return skill

    def dependency_graph(self, skill_ids: list[str] | None = None) -> dict[str, list[str]]:
        if not self._registry:
            self.load_registry()

        registry_skills = self._registry.get("skills", {})
        graph: dict[str, list[str]] = {}

        keys = skill_ids or sorted(registry_skills.keys(), key=task_sort_key)
        for skill_id in keys:
            meta = registry_skills.get(skill_id, {})
            graph[skill_id] = list(meta.get("depends_on", []))

        return graph

    def collect_transitive(self, requested: list[str], graph: dict[str, list[str]]) -> set[str]:
        needed: set[str] = set()

        def collect(skill_id: str) -> None:
            if skill_id in needed:
                return
            if skill_id not in graph:
                raise KeyError(f"Unknown skill in plan: {skill_id}")
            needed.add(skill_id)
            for dep in graph[skill_id]:
                collect(dep)

        for skill_id in requested:
            collect(skill_id.upper())

        return needed

    def detect_cycle(self, graph: dict[str, list[str]]) -> str | None:
        state: dict[str, int] = {node: 0 for node in graph}

        def visit(node: str, stack: list[str]) -> str | None:
            state[node] = 1
            stack.append(node)
            for dep in graph.get(node, []):
                if dep not in state:
                    continue
                if state[dep] == 1:
                    cycle_start = stack.index(dep)
                    return " -> ".join(stack[cycle_start:] + [dep])
                if state[dep] == 0:
                    found = visit(dep, stack)
                    if found:
                        return found
            stack.pop()
            state[node] = 2
            return None

        for node in sorted(graph):
            if state[node] == 0:
                found = visit(node, [])
                if found:
                    return found
        return None

    def topological_sort(self, requested: list[str]) -> list[str]:
        graph = self.dependency_graph()
        needed = self.collect_transitive(requested, graph)

        cycle = self.detect_cycle({k: v for k, v in graph.items() if k in needed})
        if cycle:
            raise ValueError(f"CYCLE_DETECTED: {cycle}")

        in_degree = {skill_id: 0 for skill_id in needed}
        for skill_id in needed:
            for dep in graph[skill_id]:
                if dep in needed:
                    in_degree[skill_id] += 1

        queue = sorted(
            (skill_id for skill_id in needed if in_degree[skill_id] == 0),
            key=task_sort_key,
        )
        order: list[str] = []

        while queue:
            queue.sort(key=task_sort_key)
            skill_id = queue.pop(0)
            order.append(skill_id)
            for other in sorted(needed, key=task_sort_key):
                if skill_id in graph[other]:
                    in_degree[other] -= 1
                    if in_degree[other] == 0:
                        queue.append(other)

        if len(order) != len(needed):
            raise ValueError("CYCLE_DETECTED in skill dependency graph")

        return order

    def parallel_waves(self, execution_order: list[str]) -> list[list[str]]:
        graph = self.dependency_graph()
        completed: set[str] = set()
        remaining = list(execution_order)
        waves: list[list[str]] = []

        while remaining:
            wave = [
                skill_id
                for skill_id in remaining
                if all(dep in completed for dep in graph.get(skill_id, []))
            ]
            if not wave:
                raise ValueError("Unable to schedule parallel wave — dependency deadlock")
            wave = sorted(wave, key=task_sort_key)
            waves.append(wave)
            completed.update(wave)
            remaining = [skill_id for skill_id in remaining if skill_id not in completed]

        return waves

    def skills_for_domain(self, domain: str) -> list[str]:
        domain = domain.upper()
        if domain not in {"B", "I", "A", "D"}:
            raise ValueError(f"Unknown domain: {domain}")

        if not self._registry:
            self.load_registry()

        return sorted(
            (
                skill_id
                for skill_id, meta in self._registry.get("skills", {}).items()
                if meta.get("level_code") == domain
            ),
            key=task_sort_key,
        )

    def full_pipeline_skills(self) -> list[str]:
        if not self._registry:
            self.load_registry()
        return sorted(self._registry.get("skills", {}).keys(), key=task_sort_key)

    def build_plan(
        self,
        run_id: str,
        skill_ids: list[str] | None = None,
        domain: str | None = None,
        full_pipeline: bool = False,
    ) -> ExecutionPlan:
        if full_pipeline:
            requested = self.full_pipeline_skills()
        elif domain:
            requested = self.skills_for_domain(domain)
        elif skill_ids:
            requested = [skill_id.upper() for skill_id in skill_ids]
        else:
            raise ValueError("Provide skill_ids, domain, or full_pipeline=True")

        order = self.topological_sort(requested)
        waves = self.parallel_waves(order)

        if not self._skills:
            self.discover_skills()

        plan_skills = {skill_id: self._skills[skill_id] for skill_id in order if skill_id in self._skills}

        return ExecutionPlan(
            run_id=run_id,
            requested=requested,
            execution_order=order,
            parallel_waves=waves,
            skills=plan_skills,
        )
