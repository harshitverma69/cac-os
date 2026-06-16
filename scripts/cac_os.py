#!/usr/bin/env python3
"""Deterministic CAC-OS validator and task router. No LLM. No runtime agents."""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = Path(__file__).resolve().parent / "task_registry.json"
GOLDEN_DIR = ROOT / "generated_projects" / "_golden"


def load_registry() -> dict:
    with REGISTRY_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def agent_spec_path(task_id: str, meta: dict) -> Path:
    return ROOT / "agents" / meta["folder"] / f"{task_id}_{meta['slug']}_agent.md"


def blueprint_path(task_id: str, meta: dict) -> Path:
    return ROOT / "eval_blueprints" / meta["level"] / f"{task_id}_blueprint.md"


def topological_sort(tasks: dict, requested: list[str]) -> list[str]:
    """Kahn's algorithm on transitive closure of requested tasks."""
    needed: set[str] = set()

    def collect(tid: str) -> None:
        if tid in needed:
            return
        needed.add(tid)
        for dep in tasks[tid]["depends_on"]:
            collect(dep)

    for tid in requested:
        if tid not in tasks:
            raise ValueError(f"Unknown task_id: {tid}")
        collect(tid)

    in_degree = {tid: 0 for tid in needed}
    for tid in needed:
        for dep in tasks[tid]["depends_on"]:
            if dep in needed:
                in_degree[tid] += 1

    queue = deque(sorted(t for t in needed if in_degree[t] == 0))
    order: list[str] = []

    while queue:
        tid = queue.popleft()
        order.append(tid)
        for other in sorted(needed):
            if tid in tasks[other]["depends_on"]:
                in_degree[other] -= 1
                if in_degree[other] == 0:
                    queue.append(other)

    if len(order) != len(needed):
        raise ValueError("CYCLE_DETECTED in task dependency graph")

    return order


def cmd_list(_: argparse.Namespace) -> int:
    reg = load_registry()
    for tid in sorted(reg["tasks"].keys(), key=_task_sort_key):
        meta = reg["tasks"][tid]
        deps = ",".join(meta["depends_on"]) or "-"
        print(f"{tid}\t{meta['level']}\t{deps}\t{meta['output_file']}")
    return 0


def cmd_route(args: argparse.Namespace) -> int:
    reg = load_registry()
    tasks = reg["tasks"]

    intent_map = {
        "discover": ["B1"],
        "map_apis": ["B2"],
        "find_tests": ["B3"],
        "build_fastapi": ["B4"],
        "build_node": ["B5"],
        "build_rust": ["B6"],
        "er_diagram": ["I1"],
        "trace_flow": ["I2"],
        "safe_change": ["I3"],
        "polyglot_pair": ["I4"],
        "dockerize": ["I5"],
        "fix_bug": ["I6"],
        "worktree_plan": ["A1"],
        "worktree_execute": ["A2"],
        "fraud_system": ["A3"],
        "modernize": ["A4"],
        "review_pr": ["A5"],
        "perf_improve": ["A6"],
        "terraform": ["D1"],
        "compose_stack": ["D2"],
        "ci_pipeline": ["D3"],
        "kubernetes": ["D4"],
        "bootstrap": ["D5"],
        "observability": ["D6"],
        "full_eval": list(tasks.keys()),
    }

    if args.tasks:
        requested = [t.strip() for t in args.tasks.split(",")]
    elif args.intent:
        if args.intent not in intent_map:
            print(f"Unknown intent: {args.intent}", file=sys.stderr)
            return 1
        requested = intent_map[args.intent]
    else:
        print("Provide --intent or --tasks", file=sys.stderr)
        return 1

    order = topological_sort(tasks, requested)
    plan = {
        "run_id": args.run_id or "planned-run",
        "intent": args.intent or "custom",
        "eval_source": reg["eval_source"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tasks": order,
        "execution_order": order,
        "agent_specs": [str(agent_spec_path(t, tasks[t]).relative_to(ROOT)) for t in order],
    }
    print(json.dumps(plan, indent=2))
    return 0


def cmd_validate_registry(_: argparse.Namespace) -> int:
    reg = load_registry()
    tasks = reg["tasks"]
    errors: list[str] = []

    # cycle check
    try:
        topological_sort(tasks, list(tasks.keys()))
    except ValueError as e:
        errors.append(str(e))

    for tid, meta in tasks.items():
        spec = agent_spec_path(tid, meta)
        bp = blueprint_path(tid, meta)
        golden = GOLDEN_DIR / tid / meta["output_file"]

        if not spec.is_file():
            errors.append(f"MISSING agent spec: {spec.relative_to(ROOT)}")
        if not bp.is_file():
            errors.append(f"MISSING blueprint: {bp.relative_to(ROOT)}")
        if not golden.is_file():
            errors.append(f"MISSING golden example: {golden.relative_to(ROOT)}")

        if golden.is_file():
            try:
                data = json.loads(golden.read_text(encoding="utf-8"))
                if data.get("task_id") != tid:
                    errors.append(f"GOLDEN task_id mismatch: {tid}")
            except json.JSONDecodeError as e:
                errors.append(f"GOLDEN invalid JSON {tid}: {e}")

    if errors:
        print("VALIDATION FAILED", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"OK: {len(tasks)} tasks, all specs/blueprints/golden examples present, DAG acyclic")
    return 0


def cmd_validate_run(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    if not run_dir.is_dir():
        print(f"Run dir not found: {run_dir}", file=sys.stderr)
        return 1

    manifest_path = run_dir / "manifest.json"
    if not manifest_path.is_file():
        print(f"MISSING manifest.json in {run_dir}", file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    reg = load_registry()
    tasks = reg["tasks"]
    errors: list[str] = []

    for entry in manifest.get("tasks", []):
        tid = entry.get("task_id")
        status = entry.get("status")
        if tid not in tasks:
            errors.append(f"Unknown task in manifest: {tid}")
            continue
        if status == "complete":
            out = run_dir / tid / tasks[tid]["output_file"]
            if not out.is_file():
                errors.append(f"MISSING_OUTPUT: {out.relative_to(run_dir)}")

    if errors:
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"OK: run manifest valid at {run_dir}")
    return 0


def _task_sort_key(tid: str) -> tuple:
    return (tid[0], int(tid[1:]))


def main() -> int:
    parser = argparse.ArgumentParser(description="CAC-OS deterministic tooling")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List all tasks")
    p_list.set_defaults(func=cmd_list)

    p_route = sub.add_parser("route", help="Compute execution plan")
    p_route.add_argument("--intent", help="Intent from task_router.md")
    p_route.add_argument("--tasks", help="Comma-separated task IDs")
    p_route.add_argument("--run-id", help="Run UUID")
    p_route.set_defaults(func=cmd_route)

    p_val = sub.add_parser("validate-registry", help="Validate specs, blueprints, golden examples, DAG")
    p_val.set_defaults(func=cmd_validate_registry)

    p_run = sub.add_parser("validate-run", help="Validate a generated_projects run folder")
    p_run.add_argument("run_dir", help="Path to run directory")
    p_run.set_defaults(func=cmd_validate_run)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
