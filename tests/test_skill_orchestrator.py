"""Tests for CAC-OS skill orchestrator."""

from __future__ import annotations

from pathlib import Path

import pytest

from runtime.skill_orchestrator import SkillOrchestrator

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def orchestrator() -> SkillOrchestrator:
    orch = SkillOrchestrator(
        skills_root=ROOT / "skills",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    orch.load_registry()
    orch.discover_skills()
    return orch


def test_full_pipeline_has_24_skills(orchestrator: SkillOrchestrator):
    skills = orchestrator.full_pipeline_skills()
    assert len(skills) == 24


def test_topological_sort_respects_dependencies(orchestrator: SkillOrchestrator):
    order = orchestrator.topological_sort(["B2"])
    assert order.index("B1") < order.index("B2")


def test_topological_sort_full_pipeline_order(orchestrator: SkillOrchestrator):
    order = orchestrator.topological_sort(orchestrator.full_pipeline_skills())
    assert order[0] == "B1"
    assert order.index("B1") < order.index("B2")
    assert order.index("B2") < order.index("I2")
    assert order.index("I5") < order.index("D2")


def test_parallel_waves_group_independent_skills(orchestrator: SkillOrchestrator):
    order = orchestrator.topological_sort(["B1", "B3", "B4"])
    waves = orchestrator.parallel_waves(order)
    assert waves[0] == ["B1", "B3", "B4"]


def test_detect_cycle_raises(orchestrator: SkillOrchestrator):
    graph = orchestrator.dependency_graph(["B1", "B2"])
    graph["B1"] = ["B2"]
    cycle = orchestrator.detect_cycle(graph)
    assert cycle is not None
    assert "B1" in cycle and "B2" in cycle


def test_domain_filter_basics(orchestrator: SkillOrchestrator):
    basics = orchestrator.skills_for_domain("B")
    assert basics == ["B1", "B2", "B3", "B4", "B5", "B6"]


def test_build_plan_full_pipeline(orchestrator: SkillOrchestrator):
    plan = orchestrator.build_plan("test-run", full_pipeline=True)
    assert len(plan.execution_order) == 24
    assert len(plan.parallel_waves) >= 1
    assert plan.skills["B1"].skill_id == "B1"


def test_missing_skill_raises(orchestrator: SkillOrchestrator):
    with pytest.raises(KeyError):
        orchestrator.topological_sort(["Z9"])
