"""Deterministic serialization helpers — no wall-clock or environment leakage."""

from __future__ import annotations

import json
from typing import Any

# Fixed stamp used in execution metadata (never wall-clock).
DETERMINISTIC_STAMP = "1970-01-01T00:00:00Z"

# Keys stripped from skill outputs before write (volatile / run-specific).
VOLATILE_OUTPUT_KEYS = frozenset({"generated_at", "run_id"})


def stable_sort(items: list[Any]) -> list[Any]:
    return sorted(items, key=lambda item: json.dumps(item, sort_keys=True))


def canonicalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: canonicalize(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return [canonicalize(item) for item in value]
    return value


def strip_volatile_keys(data: dict) -> dict:
    return {key: value for key, value in data.items() if key not in VOLATILE_OUTPUT_KEYS}


def canonical_json_dumps(data: Any) -> str:
    normalized = canonicalize(data)
    return json.dumps(normalized, indent=2, sort_keys=True) + "\n"
