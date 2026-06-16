"""Parser coverage for remaining branches."""

from __future__ import annotations

from pathlib import Path

from runtime.skill_parser import parse_agent_markdown, parse_task_id, split_sections

ROOT = Path(__file__).resolve().parent.parent


def test_parse_task_id_plain_text():
    sections = split_sections("### Task ID\nB2\n")
    assert parse_task_id(sections, "B1") == "B2"


def test_parse_agent_inputs_strip_braces():
    agent = parse_agent_markdown(ROOT / "agents" / "intermediate" / "I6_bug_diagnosis_agent.md")
    assert "bug_context" in agent["input_contract"]
