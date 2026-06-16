"""Render CAC-OS skill JSON outputs as human-readable Markdown reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SKILL_TITLES: dict[str, str] = {
    "B1": "Repo Artifact Inventory",
    "B2": "API Endpoint Map",
    "B3": "Test Discovery",
    "B4": "FastAPI Greenfield",
    "B5": "Node.js Greenfield",
    "B6": "Rust Greenfield CLI",
    "I1": "ER Diagram",
    "I2": "Flow Trace",
    "I3": "Safe Change",
    "I4": "Polyglot FastAPI + Node",
    "I5": "Dockerize",
    "I6": "Bug Diagnosis",
    "A1": "Multi-Worktree Plan",
    "A2": "Parallel Worktrees Execute",
    "A3": "Polyglot Fraud System",
    "A4": "Modernization",
    "A5": "Adversarial Code Review",
    "A6": "Performance Improvement",
    "D1": "Terraform Plan",
    "D2": "Docker Compose Stack",
    "D3": "CI Pipeline",
    "D4": "Kubernetes Manifests",
    "D5": "Reproducible Dev Environment",
    "D6": "Observability Bolt-On",
}


def find_skill_json(skill_dir: Path) -> Path | None:
    """Locate the JSON payload for a skill output directory."""
    if not skill_dir.is_dir():
        return None
    preferred = skill_dir / "output.json"
    if preferred.is_file():
        return preferred
    json_files = sorted(skill_dir.glob("*.json"))
    return json_files[0] if json_files else None


def load_skill_payload(skill_dir: Path) -> tuple[str | None, dict]:
    json_path = find_skill_json(skill_dir)
    if json_path is None:
        return None, {}
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    task_id = payload.get("task_id") or skill_dir.name
    return task_id, payload


def render_report(payload: dict, *, task_id: str | None = None) -> str:
    """Convert a skill JSON payload to Markdown."""
    tid = task_id or str(payload.get("task_id", "unknown"))
    title = SKILL_TITLES.get(tid, tid)
    lines: list[str] = [
        f"# {tid} — {title}",
        "",
        _meta_section(payload).rstrip(),
        "",
    ]

    handler = _TASK_HANDLERS.get(tid, _render_generic)
    body = handler(payload)
    if body.strip():
        lines.append(body.rstrip())
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def export_skill_markdown(skill_dir: Path, *, output_path: Path | None = None) -> Path:
    """Write output.md for a single skill directory. Returns the markdown path."""
    task_id, payload = load_skill_payload(skill_dir)
    if not payload:
        raise FileNotFoundError(f"No JSON output found in {skill_dir}")

    md_path = output_path or (skill_dir / "output.md")
    md_path.write_text(render_report(payload, task_id=task_id), encoding="utf-8")
    return md_path


def export_run_markdown(run_dir: Path) -> list[Path]:
    """Write output.md for every skill subdirectory that has JSON output."""
    written: list[Path] = []
    if not run_dir.is_dir():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")

    for skill_dir in sorted(run_dir.iterdir(), key=lambda p: p.name):
        if not skill_dir.is_dir() or skill_dir.name.startswith("_"):
            continue
        if skill_dir.name == "manifest.json":
            continue
        if find_skill_json(skill_dir) is None:
            continue
        written.append(export_skill_markdown(skill_dir))

    index_path = run_dir / "REPORT.md"
    index_path.write_text(_render_run_index(run_dir, written), encoding="utf-8")
    written.insert(0, index_path)
    return written


def _meta_section(payload: dict) -> str:
    rows: list[tuple[str, str]] = []
    for key in ("level", "generated_at", "scan_complete", "files_scanned", "repository_path"):
        if key in payload and payload[key] is not None:
            rows.append((key.replace("_", " ").title(), str(payload[key])))

    if payload.get("warnings"):
        rows.append(("Warnings", str(len(payload["warnings"]))))
    if payload.get("limitations"):
        rows.append(("Limitations", str(len(payload["limitations"]))))

    lines = ["## Summary", ""]
    if rows:
        lines.extend(_table(["Field", "Value"], rows))
        lines.append("")

    if payload.get("warnings"):
        lines.extend(["### Warnings", ""])
        for warning in payload["warnings"]:
            lines.append(f"- {warning}")
        lines.append("")

    if payload.get("limitations"):
        lines.extend(["### Known Limitations", ""])
        for item in payload["limitations"]:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines).rstrip()


def _render_b1(payload: dict) -> str:
    lines = ["## Modules", ""]
    modules = payload.get("modules") or []
    if modules:
        rows = [(m.get("name", ""), m.get("path", "")) for m in modules]
        lines.extend(_table(["Module", "Path"], rows))
    else:
        lines.append("_No modules discovered._")
    lines.append("")

    artifacts = payload.get("artifacts") or {}
    lines.append("## Artifacts")
    lines.append("")
    for category in sorted(artifacts):
        items = artifacts[category] or []
        if not items:
            continue
        lines.append(f"### {category.replace('_', ' ').title()} ({len(items)})")
        lines.append("")
        rows = [(a.get("name", ""), f"`{a.get('file_path', '')}`") for a in items]
        lines.extend(_table(["Name", "File"], rows))
        lines.append("")

    graph = payload.get("dependency_graph_summary") or {}
    nodes = graph.get("nodes") or []
    edges = graph.get("edges") or []
    lines.extend(
        [
            "## Dependency Graph Summary",
            "",
            f"- **Nodes:** {len(nodes)}",
            f"- **Edges:** {len(edges)}",
            "",
        ]
    )
    if edges:
        lines.append("### Sample Edges (first 25)")
        lines.append("")
        for edge in edges[:25]:
            if "->" in edge:
                source, target = edge.split("->", 1)
                lines.append(f"- `{source}` → `{target}`")
            else:
                lines.append(f"- `{edge}`")
        if len(edges) > 25:
            lines.append(f"- _…and {len(edges) - 25} more edges_")
        lines.append("")
    return "\n".join(lines)


def _render_b2(payload: dict) -> str:
    lines = ["## API Endpoints", ""]
    endpoints = payload.get("endpoints") or []
    if endpoints:
        rows = []
        for ep in endpoints:
            rows.append(
                (
                    ep.get("method", ep.get("id", "")),
                    ep.get("route", ep.get("path", ep.get("full_path", ""))),
                    ep.get("controller", ""),
                    ep.get("handler_method", ep.get("handler", "")),
                    f"`{ep.get('source_file', '')}`",
                )
            )
        lines.extend(_table(["Method", "Route", "Controller", "Handler", "Source"], rows))
    else:
        lines.append("_No endpoints discovered._")
    lines.append("")

    frontend = payload.get("frontend_routes") or []
    if frontend:
        lines.extend(["## Frontend Routes", ""])
        rows = [(r.get("path", ""), f"`{r.get('source_file', '')}`") for r in frontend]
        lines.extend(_table(["Path", "Source"], rows))
        lines.append("")
    return "\n".join(lines)


def _render_b3(payload: dict) -> str:
    lines = ["## Test Framework", ""]
    for key in ("framework", "test_root", "config_file"):
        if key in payload:
            lines.append(f"- **{key.replace('_', ' ').title()}:** `{payload[key]}`")
    lines.append("")

    commands = payload.get("commands") or payload.get("test_commands") or []
    if commands:
        lines.extend(["## Commands", ""])
        for cmd in commands:
            if isinstance(cmd, dict):
                lines.append(f"- `{cmd.get('command', cmd)}`")
            else:
                lines.append(f"- `{cmd}`")
        lines.append("")

    tests = payload.get("test_files") or []
    if tests:
        lines.extend(["## Test Files", ""])
        for test_file in tests[:50]:
            path = test_file if isinstance(test_file, str) else test_file.get("path", "")
            lines.append(f"- `{path}`")
        if len(tests) > 50:
            lines.append(f"- _…and {len(tests) - 50} more_")
        lines.append("")
    return "\n".join(lines)


def _render_issues(payload: dict, *, key: str = "issues") -> str:
    lines = [f"## {key.replace('_', ' ').title()}", ""]
    items = payload.get(key) or []
    if not items:
        lines.append("_None._")
        lines.append("")
        return "\n".join(lines)

    for index, item in enumerate(items, start=1):
        if isinstance(item, dict):
            title = item.get("title") or item.get("id") or item.get("severity") or f"Item {index}"
            lines.append(f"### {index}. {title}")
            lines.append("")
            for field in ("severity", "category", "file_path", "description", "recommendation"):
                if item.get(field):
                    lines.append(f"- **{field.replace('_', ' ').title()}:** {item[field]}")
            lines.append("")
        else:
            lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def _render_i1(payload: dict) -> str:
    lines = ["## Tables / Entities", ""]
    tables = payload.get("tables") or payload.get("entities") or []
    if tables:
        rows = []
        for table in tables:
            if isinstance(table, dict):
                rows.append(
                    (
                        table.get("name", ""),
                        table.get("source_file", ""),
                        ", ".join(table.get("columns", [])[:5]),
                    )
                )
            else:
                rows.append((str(table), "", ""))
        lines.extend(_table(["Name", "Source", "Columns (sample)"], rows))
    else:
        lines.append("_No tables discovered._")
    lines.append("")

    mermaid = payload.get("mermaid_er") or payload.get("mermaid")
    if mermaid:
        lines.extend(["## ER Diagram", "", "```mermaid", mermaid.strip(), "```", ""])
    return "\n".join(lines)


def _render_i2(payload: dict) -> str:
    lines = ["## Flow Trace", ""]
    steps = payload.get("steps") or []
    if steps:
        rows = []
        for step in steps:
            if isinstance(step, dict):
                rows.append(
                    (
                        step.get("order", step.get("step", "")),
                        step.get("layer", step.get("type", "")),
                        step.get("symbol", step.get("name", "")),
                        f"`{step.get('file_path', '')}`",
                    )
                )
        lines.extend(_table(["#", "Layer", "Symbol", "File"], rows))
    else:
        lines.append("_No steps recorded._")
    lines.append("")

    mermaid = payload.get("sequence_diagram_mermaid")
    if mermaid:
        lines.extend(["## Sequence Diagram", "", "```mermaid", mermaid.strip(), "```", ""])
    return "\n".join(lines)


def _render_proof(payload: dict) -> str:
    lines: list[str] = []
    for key in sorted(payload):
        if not key.endswith("_proof") and key not in ("run_proof", "build_proof", "validate_proof", "test_result"):
            continue
        proof = payload[key]
        if not isinstance(proof, dict):
            continue
        lines.extend([f"## {key.replace('_', ' ').title()}", ""])
        for field, value in proof.items():
            lines.append(f"- **{field.replace('_', ' ').title()}:** `{value}`")
        lines.append("")
    return "\n".join(lines)


def _render_generic(payload: dict) -> str:
    skip = {
        "task_id",
        "level",
        "generated_at",
        "scan_complete",
        "warnings",
        "limitations",
        "files_scanned",
        "repository_path",
    }
    lines: list[str] = []
    for key in sorted(payload):
        if key in skip:
            continue
        value = payload[key]
        title = key.replace("_", " ").title()
        lines.extend([f"## {title}", ""])
        lines.append(_render_value(value))
        lines.append("")
    return "\n".join(lines)


def _render_value(value: Any, *, depth: int = 0) -> str:
    if value is None:
        return "_null_"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        if "\n" in value and depth == 0:
            return f"```\n{value.strip()}\n```"
        return value
    if isinstance(value, list):
        if not value:
            return "_Empty list_"
        if all(isinstance(item, dict) for item in value):
            headers = _collect_headers(value)
            if headers:
                rows = [tuple(_stringify(item.get(h, "")) for h in headers) for item in value]
                return "\n".join(_table(headers, rows))
        return "\n".join(f"- {_render_value(item, depth=depth + 1)}" for item in value[:100])
    if isinstance(value, dict):
        if not value:
            return "_Empty object_"
        rows = [(k, _render_value(v, depth=depth + 1)) for k, v in sorted(value.items())]
        return "\n".join(_table(["Key", "Value"], rows))
    return str(value)


def _collect_headers(items: list[dict]) -> list[str]:
    headers: list[str] = []
    for item in items:
        for key in item:
            if key not in headers:
                headers.append(key)
    return headers[:6]


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=True)
    return str(value)


def _table(headers: list[str], rows: list[tuple]) -> list[str]:
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(str(cell).replace("|", "\\|") for cell in row) + " |" for row in rows]
    return [header_line, sep_line, *body]


def _render_run_index(run_dir: Path, skill_reports: list[Path]) -> str:
    manifest_path = run_dir / "manifest.json"
    repo = ""
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        repo = manifest.get("repository_path", "")

    lines = [
        f"# CAC-OS Run Report — `{run_dir.name}`",
        "",
    ]
    if repo:
        lines.extend([f"**Repository:** `{repo}`", ""])

    lines.extend(["## Skills", ""])
    for report_path in skill_reports:
        if report_path.name == "REPORT.md":
            continue
        skill_id = report_path.parent.name
        title = SKILL_TITLES.get(skill_id, skill_id)
        rel = report_path.relative_to(run_dir).as_posix()
        lines.append(f"- [{skill_id} — {title}]({rel})")
    lines.append("")
    return "\n".join(lines)


_TASK_HANDLERS: dict[str, Any] = {
    "B1": _render_b1,
    "B2": _render_b2,
    "B3": _render_b3,
    "I1": _render_i1,
    "I2": _render_i2,
    "A5": lambda p: _render_issues(p, key="issues"),
    "I6": _render_generic,
}
