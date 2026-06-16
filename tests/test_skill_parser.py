"""Tests for CAC-OS skill parser."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime.skill_parser import (
    parse_agent_markdown,
    parse_skill_markdown,
    split_sections,
    validate_output_schema,
)

ROOT = Path(__file__).resolve().parent.parent


def test_split_sections_extracts_headings():
    text = "### Task ID\n`B1`\n\n### Objective\nScan repo\n"
    sections = split_sections(text)
    assert sections["Task ID"] == "`B1`"
    assert sections["Objective"] == "Scan repo"


def test_parse_agent_markdown_b1():
    path = ROOT / "agents" / "basics" / "B1_repo_artifact_inventory_agent.md"
    agent = parse_agent_markdown(path)
    assert agent["skill_id"] == "B1"
    assert agent["level"] == "BASIC"
    assert "repository_path" in agent["input_contract"]
    assert agent["output_contract"]["task_id"] == "B1"
    assert "inventory_report.json" == agent["canonical_output_file"]


def test_parse_generated_skill_markdown():
    skill_path = ROOT / "skills" / "basics" / "B1_repo_artifact_inventory.skill.md"
    if not skill_path.is_file():
        pytest.skip("Run skill_registry_builder first")

    skill = parse_skill_markdown(skill_path, ROOT)
    assert skill.skill_id == "B1"
    assert skill.level == "BASIC"
    assert skill.output_contract["task_id"] == "B1"
    assert len(skill.execution_steps) >= 1


def test_validate_output_schema_detects_missing_keys():
    contract = {"task_id": "B1", "files_scanned": 0}
    errors = validate_output_schema({"task_id": "B1"}, contract)
    assert any("files_scanned" in err for err in errors)


def test_validate_output_schema_detects_task_id_mismatch():
    contract = {"task_id": "B2"}
    errors = validate_output_schema({"task_id": "B1"}, contract)
    assert any("TASK_ID_MISMATCH" in err for err in errors)


def test_validate_output_schema_passes_valid_output():
    contract = {"task_id": "B1", "modules": []}
    output = {"task_id": "B1", "modules": [], "extra": True}
    assert validate_output_schema(output, contract) == []
