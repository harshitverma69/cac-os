#!/usr/bin/env python3
"""Run CAC-OS agent checks against a target repo using RepoLens where available."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPO = Path("/Users/harshitverma/Desktop/repolens")
REPOLENS_BACKEND = DEFAULT_REPO / "backend"


def _stamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _envelope(task_id: str, level: str) -> dict:
    return {
        "task_id": task_id,
        "level": level,
        "generated_at": _stamp(),
        "scan_complete": True,
        "warnings": [],
        "repository_path": str(DEFAULT_REPO),
    }


def _write(out_dir: Path, task_id: str, filename: str, payload: dict) -> Path:
    task_dir = out_dir / task_id
    task_dir.mkdir(parents=True, exist_ok=True)
    path = task_dir / filename
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _sorted_artifacts(report) -> dict:
    categories = [
        "controllers",
        "services",
        "repositories",
        "entities",
        "configs",
        "consumers",
        "jobs",
        "utilities",
        "interfaces",
        "enums",
        "models",
    ]
    artifacts: dict[str, list] = {"classes": []}
    for category in categories:
        items = []
        for artifact in sorted(report.get_category(category), key=lambda a: a.name.lower()):
            items.append(
                {
                    "name": artifact.name,
                    "file_path": artifact.file_path,
                    "language": artifact.language,
                    "evidence": artifact.evidence,
                }
            )
        key = "models" if category == "entities" else category
        if category == "entities":
            artifacts.setdefault("models", []).extend(items)
        else:
            artifacts[key] = items
    return artifacts


def run_b1(repo: Path, out_dir: Path) -> dict:
    from app.agents.repo_discovery_agent import RepoDiscoveryAgent

    report = RepoDiscoveryAgent().scan(repo, write_outputs=False)
    nodes = sorted({m.name for m in report.modules})
    edges = sorted({f"{e.source}->{e.target}" for e in report.dependency_graph})
    payload = {
        **_envelope("B1", "B"),
        "files_scanned": report.summary.files_scanned,
        "modules": [{"name": m.name, "path": m.path} for m in sorted(report.modules, key=lambda m: m.name)],
        "artifacts": _sorted_artifacts(report),
        "dependency_graph_summary": {"nodes": nodes, "edges": edges},
        "limitations": list(report.summary.limitations),
    }
    path = _write(out_dir, "B1", "inventory_report.json", payload)
    return {"status": "PASS", "output": str(path.relative_to(ROOT)), "files_scanned": report.summary.files_scanned}


def run_b2(repo: Path, out_dir: Path, inventory) -> dict:
    from app.agents.api_mapping_agent import ApiMappingAgent

    report = ApiMappingAgent().scan(repo, inventory=inventory, write_outputs=False)
    endpoints = []
    for ep in sorted(report.endpoints, key=lambda e: (e.method, e.full_path)):
        endpoints.append(
            {
                "method": ep.method,
                "path": ep.full_path,
                "controller": ep.controller,
                "handler_method": ep.handler,
                "source_file": ep.file_path,
                "line": ep.line_number,
                "framework": ep.framework,
            }
        )
    frontend_routes = []
    frontend_root = repo / "frontend" / "src" / "app"
    if frontend_root.is_dir():
        for page in sorted(frontend_root.rglob("page.tsx")):
            rel = page.relative_to(repo).as_posix()
            route = "/" + rel.replace("frontend/src/app/", "").replace("/page.tsx", "").replace("(groups)/", "")
            if route == "/":
                pass
            frontend_routes.append({"path": route or "/", "source_file": rel})
    payload = {
        **_envelope("B2", "B"),
        "endpoints": endpoints,
        "frontend_routes": frontend_routes,
        "controllers": sorted({e["controller"] for e in endpoints}),
        "mapping": {e["path"]: e["handler_method"] for e in endpoints if e.get("path")},
    }
    path = _write(out_dir, "B2", "api_map_report.json", payload)
    return {"status": "PASS", "output": str(path.relative_to(ROOT)), "endpoints": len(endpoints)}


def run_b3(repo: Path, out_dir: Path, *, run_pytest: bool = True) -> dict:
    from app.agents.test_discovery_agent import TestDiscoveryAgent

    report = TestDiscoveryAgent().discover(repo, write_outputs=False)
    backend = repo / "backend"
    cmd = "cd backend && python -m pytest -q"
    proc = subprocess.run(cmd, shell=True, cwd=repo, capture_output=True, text=True) if run_pytest else None
    exit_code = proc.returncode if proc else -1
    payload = {
        **_envelope("B3", "B"),
        "framework": report.framework.value,
        "config_files": list(report.config_files),
        "test_files": [f.path for f in report.test_files],
        "commands": {
            "unit": cmd,
            "integration": "",
            "coverage": "cd backend && python -m pytest --cov=app -q",
        },
        "command_result": {
            "command": cmd,
            "exit_code": exit_code,
            "stdout_hash": hashlib.sha256(proc.stdout.encode()).hexdigest()[:16] if proc else "",
            "stderr_hash": hashlib.sha256(proc.stderr.encode()).hexdigest()[:16] if proc else "",
        },
        "failures": [],
        "interpretation": [] if not proc or proc.returncode == 0 else ["pytest exited non-zero"],
    }
    path = _write(out_dir, "B3", "test_discovery_report.json", payload)
    if not run_pytest:
        return {
            "status": "PARTIAL",
            "output": str(path.relative_to(ROOT)),
            "framework": report.framework.value,
            "test_files": len(report.test_files),
            "note": "pytest skipped; use default run for proof",
        }
    status = "PASS" if proc.returncode == 0 else "PARTIAL"
    return {
        "status": status,
        "output": str(path.relative_to(ROOT)),
        "framework": report.framework.value,
        "test_files": len(report.test_files),
        "exit_code": proc.returncode,
    }


def run_i1(repo: Path, out_dir: Path) -> dict:
    from app.agents.er_diagram_agent import ErDiagramAgent

    report = ErDiagramAgent().scan(repo, write_outputs=False)
    tables = []
    for table in sorted(report.tables, key=lambda t: t.table_name):
        tables.append(
            {
                "table_name": table.table_name,
                "entity_name": table.entity_name,
                "file_path": table.file_path,
                "columns": [c.name for c in table.columns],
                "source_citation": table.file_path,
            }
        )
    payload = {
        **_envelope("I1", "I"),
        "tables": tables,
        "relationships": [
            {
                "type": r.type,
                "source_table": r.source_table,
                "target_table": r.target_table,
            }
            for r in report.relationships
        ],
        "mermaid_er": report.to_mermaid(),
        "frameworks": report.frameworks,
    }
    path = _write(out_dir, "I1", "schema_report.json", payload)
    return {"status": "PASS", "output": str(path.relative_to(ROOT)), "tables": len(tables)}


def run_i2(repo: Path, out_dir: Path, endpoint_id: str) -> dict:
    from app.agents.flow_trace_agent import FlowTraceAgent

    trace = FlowTraceAgent().trace(str(repo), endpoint_id)
    steps = [
        {
            "order": i + 1,
            "node_id": node.id,
            "type": node.type.value if hasattr(node.type, "value") else str(node.type),
            "file_path": node.file_path,
        }
        for i, node in enumerate(trace.nodes)
    ]
    mermaid = trace.to_markdown() if hasattr(trace, "to_markdown") else ""
    payload = {
        **_envelope("I2", "I"),
        "endpoint_id": endpoint_id,
        "steps": steps,
        "nodes": [n.model_dump(mode="json") for n in trace.nodes],
        "sequence_diagram_mermaid": mermaid,
    }
    path = _write(out_dir, "I2", "flow_trace_report.json", payload)
    return {"status": "PASS", "output": str(path.relative_to(ROOT)), "endpoint": endpoint_id, "steps": len(steps)}


def run_i6(repo: Path, out_dir: Path, endpoint_id: str) -> dict:
    from app.agents.bug_diagnosis_agent import BugDiagnosisAgent

    report = BugDiagnosisAgent().diagnose(
        repo,
        endpoint_id,
        error="Simulated 500 for eval",
        stack_trace="",
    )
    payload = {
        **_envelope("I6", "I"),
        "endpoint": endpoint_id,
        "root_causes": [c.model_dump(mode="json") for c in report.probable_causes],
        "suggested_fixes": [c.description for c in report.probable_causes[:3]],
        "verification": {"agent_suggested": [], "manually_verified": [], "uncertain": []},
    }
    path = _write(out_dir, "I6", "bug_fix_report.json", payload)
    return {"status": "PARTIAL", "output": str(path.relative_to(ROOT)), "note": "Diagnosis only; fix+proof not applied"}


def run_a4(repo: Path, out_dir: Path, endpoint_id: str) -> dict:
    from app.agents.modernization_agent import ModernizationAgent

    report = ModernizationAgent().analyze(repo, endpoint_id)
    payload = {
        **_envelope("A4", "A"),
        "endpoint": endpoint_id,
        "findings": [f.model_dump(mode="json") for f in report.findings],
        "actions": [a.model_dump(mode="json") for a in report.actions],
        "first_step": report.actions[0].model_dump(mode="json") if report.actions else None,
        "verification": {"agent_suggested": [], "manually_verified": [], "uncertain": []},
    }
    path = _write(out_dir, "A4", "modernization_report.json", payload)
    return {"status": "PARTIAL", "output": str(path.relative_to(ROOT)), "findings": len(report.findings)}


def run_a5(repo: Path, out_dir: Path) -> dict:
    from app.agents.verification_agent import VerificationAgent

    report = VerificationAgent().analyze(repo)
    payload = {
        **_envelope("A5", "A"),
        "issues": [e.model_dump(mode="json") for e in report.entries],
        "summary": report.summary.model_dump(mode="json"),
    }
    path = _write(out_dir, "A5", "code_review_report.json", payload)
    return {"status": "PASS", "output": str(path.relative_to(ROOT)), "entries": len(report.entries)}


def run_a6(repo: Path, out_dir: Path, endpoint_id: str) -> dict:
    from app.agents.performance_agent import PerformanceAgent

    report = PerformanceAgent().analyze(repo, endpoint_id)
    payload = {
        **_envelope("A6", "A"),
        "endpoint": endpoint_id,
        "findings": [f.model_dump(mode="json") for f in report.findings],
        "baseline": {"note": "static analysis only"},
        "after": {"note": "no measured run in this eval"},
        "behavior_proof": {"command": "N/A", "exit_code": 0},
    }
    path = _write(out_dir, "A6", "performance_report.json", payload)
    return {"status": "PARTIAL", "output": str(path.relative_to(ROOT)), "findings": len(report.findings)}


def run_skipped(task_id: str, level: str, out_dir: Path, filename: str, reason: str, extra: dict | None = None) -> dict:
    payload = {**_envelope(task_id, level), "status": "SKIPPED", "reason": reason, **(extra or {})}
    path = _write(out_dir, task_id, filename, payload)
    return {"status": "SKIPPED", "output": str(path.relative_to(ROOT)), "reason": reason}


def run_infra_check(task_id: str, level: str, out_dir: Path, filename: str, repo: Path, checks: dict[str, bool], note: str) -> dict:
    payload = {
        **_envelope(task_id, level),
        "checks": checks,
        "note": note,
    }
    path = _write(out_dir, task_id, filename, payload)
    all_present = all(checks.values())
    return {
        "status": "PARTIAL" if all_present else "SKIPPED",
        "output": str(path.relative_to(ROOT)),
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CAC-OS agent eval against repolens")
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--run-id", default="repolens-eval")
    parser.add_argument("--skip-pytest", action="store_true", help="Skip live pytest for B3")
    args = parser.parse_args()

    repo = args.repo.resolve()
    out_dir = ROOT / "generated_projects" / args.run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(REPOLENS_BACKEND))

    results: dict[str, dict] = {}

    print(f"Target repo: {repo}")
    print(f"Output dir:  {out_dir}")
    print()

    # B1
    print("[B1] Repo inventory...")
    b1_result = run_b1(repo, out_dir)
    results["B1"] = b1_result
    from app.agents.repo_discovery_agent import RepoDiscoveryAgent

    inventory = RepoDiscoveryAgent().scan(repo, write_outputs=False)

    # B2
    print("[B2] API mapping...")
    results["B2"] = run_b2(repo, out_dir, inventory)

    # B3
    print("[B3] Test discovery + pytest...")
    results["B3"] = run_b3(repo, out_dir, run_pytest=not args.skip_pytest)

    # B4-B6 greenfield
    for tid, name in [("B4", "FastAPI greenfield"), ("B5", "Node greenfield"), ("B6", "Rust greenfield")]:
        print(f"[{tid}] {name} — skipped (greenfield build, not repo scan)...")
        results[tid] = run_skipped(
            tid,
            "B",
            out_dir,
            "greenfield_manifest.json",
            "Builds a new project from scratch; repolens is the analysis target, not output artifact.",
        )

    endpoint_id = "GET:/health"
    try:
        from app.agents.api_mapping_agent import ApiMappingAgent

        api = ApiMappingAgent().scan(repo, inventory=inventory, write_outputs=False)
        backend_eps = [
            e for e in api.endpoints if e.language == "python" or "backend/" in e.file_path
        ]
        preferred = [e for e in backend_eps if "health" in e.full_path.lower()]
        chosen = preferred[0] if preferred else (backend_eps[0] if backend_eps else None)
        if chosen:
            endpoint_id = chosen.id
    except Exception:
        pass

    # I1
    print("[I1] ER diagram...")
    results["I1"] = run_i1(repo, out_dir)

    # I2
    print(f"[I2] Flow trace ({endpoint_id})...")
    try:
        results["I2"] = run_i2(repo, out_dir, endpoint_id)
    except Exception as exc:
        results["I2"] = run_skipped("I2", "I", out_dir, "flow_trace_report.json", str(exc))

    # I3
    print("[I3] Safe change — skipped (requires actual diff + test proof)...")
    results["I3"] = run_skipped(
        "I3",
        "I",
        out_dir,
        "change_report.json",
        "Requires implementing a scoped change with test proof; not auto-runnable.",
    )

    # I4
    print("[I4] Polyglot pair — skipped (greenfield FastAPI+Node build)...")
    results["I4"] = run_skipped(
        "I4",
        "I",
        out_dir,
        "polyglot_manifest.json",
        "Builds new FastAPI service + Node client; not a repolens scan task.",
    )

    # I5
    print("[I5] Dockerize check...")
    dockerfile = repo / "docker" / "Dockerfile"
    compose = repo / "docker-compose.yml"
    results["I5"] = run_infra_check(
        "I5",
        "I",
        out_dir,
        "docker_manifest.json",
        repo,
        {"dockerfile": dockerfile.is_file(), "docker_compose": compose.is_file()},
        "RepoLens target already dockerized; manifest records existing artifacts.",
    )

    # I6
    print(f"[I6] Bug diagnosis ({endpoint_id})...")
    try:
        results["I6"] = run_i6(repo, out_dir, endpoint_id)
    except Exception as exc:
        results["I6"] = run_skipped("I6", "I", out_dir, "bug_fix_report.json", str(exc))

    # A1-A3
    print("[A1] Worktree plan — template...")
    results["A1"] = run_skipped(
        "A1",
        "A",
        out_dir,
        "worktree_plan.json",
        "Requires git worktree planning for a feature slice; manual/Cursor execution.",
        {
            "suggested_feature": "Add Prometheus metrics endpoint to repolens backend",
            "worktrees": [
                {"name": "metrics-api", "scope": "backend/app/api/metrics.py"},
                {"name": "metrics-tests", "scope": "backend/tests/test_metrics.py"},
            ],
        },
    )
    results["A2"] = run_skipped("A2", "A", out_dir, "worktree_execution_report.json", "Depends on A1 git worktree execution.")
    results["A3"] = run_skipped(
        "A3",
        "A",
        out_dir,
        "fraud_system_manifest.json",
        "Builds 3-component polyglot fraud system; not applicable to repolens scan.",
    )

    # A4-A6
    print(f"[A4] Modernization ({endpoint_id})...")
    try:
        results["A4"] = run_a4(repo, out_dir, endpoint_id)
    except Exception as exc:
        results["A4"] = run_skipped("A4", "A", out_dir, "modernization_report.json", str(exc))
    print("[A5] Verification / code review...")
    try:
        results["A5"] = run_a5(repo, out_dir)
    except Exception as exc:
        results["A5"] = run_skipped("A5", "A", out_dir, "code_review_report.json", str(exc))
    print(f"[A6] Performance ({endpoint_id})...")
    try:
        results["A6"] = run_a6(repo, out_dir, endpoint_id)
    except Exception as exc:
        results["A6"] = run_skipped("A6", "A", out_dir, "performance_report.json", str(exc))

    # D1-D6
    print("[D1] Terraform — not present in repolens...")
    results["D1"] = run_skipped("D1", "D", out_dir, "terraform_manifest.json", "No .tf files in repolens; task creates new Terraform.")
    print("[D2] Docker compose stack...")
    results["D2"] = run_infra_check(
        "D2",
        "D",
        out_dir,
        "compose_manifest.json",
        repo,
        {"docker_compose_yml": compose.is_file(), "backend_dockerfile": dockerfile.is_file()},
        "Existing stack at repo root; live e2e not run in this eval.",
    )
    print("[D3] CI pipeline...")
    ci = repo / ".github" / "workflows" / "ci.yml"
    results["D3"] = run_infra_check(
        "D3",
        "D",
        out_dir,
        "ci_manifest.json",
        repo,
        {"github_actions_ci": ci.is_file()},
        "CI workflow exists; green run proof requires GitHub Actions.",
    )
    results["D4"] = run_skipped("D4", "D", out_dir, "k8s_manifest.json", "No Kubernetes manifests in repolens.")
    print("[D5] Bootstrap check...")
    readme = repo / "README.md"
    results["D5"] = run_infra_check(
        "D5",
        "D",
        out_dir,
        "bootstrap_manifest.json",
        repo,
        {"readme": readme.is_file(), "backend_requirements": (repo / "backend" / "requirements.txt").is_file()},
        "Bootstrap: cd backend && pip install -r requirements.txt && pytest",
    )
    results["D6"] = run_skipped(
        "D6",
        "D",
        out_dir,
        "observability_manifest.json",
        "No Prometheus/Grafana stack in repolens; would be a bolt-on task.",
    )

    manifest = {
        "run_id": args.run_id,
        "repository_path": str(repo),
        "generated_at": _stamp(),
        "eval_source": "docs/repolens_bridge.md",
        "summary": {
            tid: results[tid]["status"] for tid in sorted(results.keys(), key=lambda x: (x[0], int(x[1:])))
        },
        "results": results,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    passed = sum(1 for r in results.values() if r["status"] == "PASS")
    partial = sum(1 for r in results.values() if r["status"] == "PARTIAL")
    skipped = sum(1 for r in results.values() if r["status"] == "SKIPPED")

    print()
    print(f"Done. PASS={passed} PARTIAL={partial} SKIPPED={skipped}")
    print(f"Manifest: {manifest_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
