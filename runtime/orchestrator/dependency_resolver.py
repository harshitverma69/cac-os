"""Skill DAG validation and topological ordering."""

from __future__ import annotations

from runtime.skill_parser import task_sort_key


def detect_cycles(graph: dict[str, list[str]]) -> list[str]:
    cycles: list[str] = []
    state: dict[str, int] = {node: 0 for node in graph}
    stack: list[str] = []

    def visit(node: str) -> None:
        state[node] = 1
        stack.append(node)
        for dep in sorted(graph.get(node, [])):
            if dep not in state:
                continue
            if state[dep] == 1:
                cycle_start = stack.index(dep)
                cycles.append(" -> ".join(stack[cycle_start:] + [dep]))
            elif state[dep] == 0:
                visit(dep)
        stack.pop()
        state[node] = 2

    for node in sorted(graph):
        if state[node] == 0:
            visit(node)

    return cycles


def detect_cycle(graph: dict[str, list[str]]) -> str | None:
    cycles = detect_cycles(graph)
    return cycles[0] if cycles else None


def collect_transitive(requested: list[str], graph: dict[str, list[str]]) -> set[str]:
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


def find_missing_dependencies(graph: dict[str, list[str]]) -> list[dict[str, str]]:
    known = set(graph)
    missing: list[dict[str, str]] = []
    for skill_id in sorted(graph, key=task_sort_key):
        for dep in graph[skill_id]:
            if dep not in known:
                missing.append({"skill_id": skill_id, "missing_dependency": dep})
    return missing


def find_orphan_skills(graph: dict[str, list[str]]) -> list[str]:
    if not graph:
        return []

    reachable: set[str] = set()
    changed = True
    while changed:
        changed = False
        for skill_id in sorted(graph, key=task_sort_key):
            if skill_id in reachable:
                continue
            deps = graph[skill_id]
            if all(dep in reachable for dep in deps):
                reachable.add(skill_id)
                changed = True

    return sorted(set(graph) - reachable, key=task_sort_key)


def topological_sort(requested: list[str], graph: dict[str, list[str]]) -> list[str]:
    needed = collect_transitive(requested, graph)

    cycle = detect_cycle({k: v for k, v in graph.items() if k in needed})
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

    if len(order) != len(needed):  # pragma: no cover - defensive fallback
        raise ValueError("CYCLE_DETECTED in skill dependency graph")

    return order


def parallel_waves(execution_order: list[str], graph: dict[str, list[str]]) -> list[list[str]]:
    completed: set[str] = set()
    remaining = list(execution_order)
    waves: list[list[str]] = []

    while remaining:
        wave = [skill_id for skill_id in remaining if all(dep in completed for dep in graph.get(skill_id, []))]
        if not wave:
            raise ValueError("Unable to schedule parallel wave — dependency deadlock")
        wave = sorted(wave, key=task_sort_key)
        waves.append(wave)
        completed.update(wave)
        remaining = [skill_id for skill_id in remaining if skill_id not in completed]

    return waves
