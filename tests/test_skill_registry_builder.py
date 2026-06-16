"""Tests for skill registry builder."""

from __future__ import annotations

import json
from pathlib import Path

from runtime.skill_registry_builder import build_skill_registry, write_registry

ROOT = Path(__file__).resolve().parent.parent


def test_build_skill_registry_structure(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(
        "runtime.skill_registry_builder.SKILLS_ROOT",
        tmp_path / "skills",
    )
    monkeypatch.setattr(
        "runtime.skill_registry_builder.CORE_REGISTRY_PATH",
        tmp_path / "core" / "skill_registry.json",
    )

    registry = build_skill_registry(write_skills=True)
    assert registry["skill_count"] == 24
    assert "B1" in registry["skills"]
    assert registry["skills"]["B1"]["level"] == "BASIC"
    assert registry["skills"]["B2"]["depends_on"] == ["B1"]

    skill_file = tmp_path / "skills" / "basics" / "B1_repo_artifact_inventory.skill.md"
    assert skill_file.is_file()
    text = skill_file.read_text(encoding="utf-8")
    assert "## Skill:" in text
    assert "### Input Contract" in text
    assert "### Output Contract (STRICT JSON)" in text

    path = write_registry(registry)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded["skill_count"] == 24
