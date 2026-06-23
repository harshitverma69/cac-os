"""Task-specific Markdown body renderers."""

from __future__ import annotations

from collections.abc import Callable

from runtime.reporting.formatters import render_value, table


def render_b1(payload: dict) -> str:
    lines = ["## Modules", ""]
    modules = payload.get("modules") or []
    if modules:
        rows = [(module.get("name", ""), module.get("path", "")) for module in modules]
        lines.extend(table(["Module", "Path"], rows))
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
        rows = [(item.get("name", ""), f"`{item.get('file_path', '')}`") for item in items]
        lines.extend(table(["Name", "File"], rows))
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


def render_b2(payload: dict) -> str:
    lines = ["## API Endpoints", ""]
    endpoints = payload.get("endpoints") or []
    if endpoints:
        rows = []
        for endpoint in endpoints:
            rows.append(
                (
                    endpoint.get("method", endpoint.get("id", "")),
                    endpoint.get("route", endpoint.get("path", endpoint.get("full_path", ""))),
                    endpoint.get("controller", ""),
                    endpoint.get("handler_method", endpoint.get("handler", "")),
                    f"`{endpoint.get('source_file', '')}`",
                )
            )
        lines.extend(table(["Method", "Route", "Controller", "Handler", "Source"], rows))
    else:
        lines.append("_No endpoints discovered._")
    lines.append("")

    frontend = payload.get("frontend_routes") or []
    if frontend:
        lines.extend(["## Frontend Routes", ""])
        frontend_rows: list[tuple[str, str]] = [
            (str(route.get("path", "")), f"`{route.get('source_file', '')}`") for route in frontend
        ]
        lines.extend(table(["Path", "Source"], frontend_rows))
        lines.append("")
    return "\n".join(lines)


def render_b3(payload: dict) -> str:
    lines = ["## Test Framework", ""]
    for key in ("framework", "test_root", "config_file"):
        if key in payload:
            lines.append(f"- **{key.replace('_', ' ').title()}:** `{payload[key]}`")
    lines.append("")

    commands = payload.get("commands") or payload.get("test_commands") or []
    if commands:
        lines.extend(["## Commands", ""])
        for command in commands:
            if isinstance(command, dict):
                lines.append(f"- `{command.get('command', command)}`")
            else:
                lines.append(f"- `{command}`")
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


def render_issues(payload: dict, *, key: str = "issues") -> str:
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
            for field in (
                "severity",
                "category",
                "file_path",
                "line",
                "description",
                "suggested_fix",
                "recommendation",
            ):
                if item.get(field):
                    lines.append(f"- **{field.replace('_', ' ').title()}:** {item[field]}")
            steps = item.get("verification_steps") or []
            if steps:
                lines.append("- **Verification Steps:**")
                for step in steps:
                    lines.append(f"  - {step}")
            lines.append("")
        else:
            lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


def render_i1(payload: dict) -> str:
    lines = ["## Tables / Entities", ""]
    tables = payload.get("tables") or payload.get("entities") or []
    if tables:
        rows = []
        for table_row in tables:
            if isinstance(table_row, dict):
                columns = table_row.get("columns", [])[:5]
                col_text = ", ".join(col if isinstance(col, str) else str(col.get("name", col)) for col in columns)
                rows.append(
                    (
                        table_row.get("name", table_row.get("table_name", "")),
                        table_row.get("source_file", table_row.get("file_path", "")),
                        col_text,
                    )
                )
            else:
                rows.append((str(table_row), "", ""))
        lines.extend(table(["Name", "Source", "Columns (sample)"], rows))
    else:
        lines.append("_No tables discovered._")
    lines.append("")

    mermaid = payload.get("mermaid_er") or payload.get("mermaid")
    if mermaid:
        lines.extend(["## ER Diagram", "", "```mermaid", mermaid.strip(), "```", ""])
    return "\n".join(lines)


def render_i2(payload: dict) -> str:
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
        lines.extend(table(["#", "Layer", "Symbol", "File"], rows))
    else:
        lines.append("_No steps recorded._")
    lines.append("")

    mermaid = payload.get("sequence_diagram_mermaid")
    if mermaid:
        lines.extend(["## Sequence Diagram", "", "```mermaid", mermaid.strip(), "```", ""])
    return "\n".join(lines)


def render_proof(payload: dict) -> str:
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


def render_generic(payload: dict) -> str:
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
        lines.append(render_value(value))
        lines.append("")
    return "\n".join(lines)


TASK_HANDLERS: dict[str, Callable[[dict], str]] = {
    "B1": render_b1,
    "B2": render_b2,
    "B3": render_b3,
    "I1": render_i1,
    "I2": render_i2,
    "A5": lambda payload: render_issues(payload, key="issues"),
    "I6": render_generic,
}
