"""Extra parser and orchestrator edge-case tests."""

from __future__ import annotations

import pytest

from runtime.skill_orchestrator import SkillOrchestrator
from runtime.skill_parser import (
    extract_json_block,
    parse_depends_on,
    split_sections,
    task_sort_key,
)


def test_task_sort_key_level_priority():
    assert task_sort_key("B1") < task_sort_key("A1")
    assert task_sort_key("I1") < task_sort_key("A1")


def test_parse_depends_on_variants():
    sections = {
        "Depends On": "B1, B2\n- I1",
    }
    assert parse_depends_on(sections) == ["B1", "B2", "I1"]


def test_parse_depends_on_none():
    assert parse_depends_on({"Depends On": "None"}) == []


def test_extract_json_block_invalid_json():
    sections = {"Input Contract": "```json\n{not-json}\n```"}
    assert extract_json_block(sections, "Input Contract") is None


def test_orchestrator_detect_cycle():
    orch = SkillOrchestrator()
    graph = {"B1": ["B2"], "B2": ["B1"]}
    cycle = orch.detect_cycle(graph)
    assert cycle is not None
