"""Markdown formatting helpers for report rendering."""

from __future__ import annotations

import json
from typing import Any


def stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list | dict):
        return json.dumps(value, ensure_ascii=True)
    return str(value)


def collect_headers(items: list[dict]) -> list[str]:
    headers: list[str] = []
    for item in items:
        for key in item:
            if key not in headers:
                headers.append(key)
    return headers[:6]


def table(headers: list[str], rows: list[tuple]) -> list[str]:
    header_line = "| " + " | ".join(headers) + " |"
    sep_line = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(str(cell).replace("|", "\\|") for cell in row) + " |" for row in rows]
    return [header_line, sep_line, *body]


def render_value(value: Any, *, depth: int = 0) -> str:
    if value is None:
        return "_null_"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, int | float):
        return str(value)
    if isinstance(value, str):
        if "\n" in value and depth == 0:
            return f"```\n{value.strip()}\n```"
        return value
    if isinstance(value, list):
        if not value:
            return "_Empty list_"
        if all(isinstance(item, dict) for item in value):
            headers = collect_headers(value)
            if headers:
                rows = [tuple(stringify(item.get(header, "")) for header in headers) for item in value]
                return "\n".join(table(headers, rows))
        return "\n".join(f"- {render_value(item, depth=depth + 1)}" for item in value[:100])
    if isinstance(value, dict):
        if not value:
            return "_Empty object_"
        rows = [(key, render_value(item, depth=depth + 1)) for key, item in sorted(value.items())]
        return "\n".join(table(["Key", "Value"], rows))
    return str(value)
