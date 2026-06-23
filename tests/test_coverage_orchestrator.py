"""Full coverage for orchestrator, dependency resolver, executor, plugins."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from runtime.models import RunContext, SkillResult
from runtime.orchestrator import SkillOrchestrator
from runtime.orchestrator.cli import main as orchestrator_cli_main
from runtime.orchestrator.dependency_resolver import (
    collect_transitive,
    detect_cycle,
    detect_cycles,
    find_missing_dependencies,
    find_orphan_skills,
    parallel_waves,
    topological_sort,
)
from runtime.orchestrator.executor import DEFAULT_RUN_INPUTS, SkillExecutor
from runtime.orchestrator.planner import (
    discover_skills,
    load_registry,
    skills_for_domain,
)
from runtime.plugins.base import BaseSkillPlugin
from runtime.plugins.loader import GoldenReplayPlugin
from runtime.plugins.registry import PluginRegistry
from runtime.skill_orchestrator import main as skill_orchestrator_main
from runtime.skill_runner import SkillRunResult
from runtime.skill_runner import main as skill_runner_main

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def orchestrator() -> SkillOrchestrator:
    orch = SkillOrchestrator(
        skills_root=ROOT / "skills",
        registry_path=ROOT / "core" / "skill_registry.json",
    )
    return orch


def test_skill_orchestrator_lazy_loads(orchestrator: SkillOrchestrator):
    assert orchestrator.get_skill("B1").skill_id == "B1"
    assert orchestrator.dependency_graph()
    assert orchestrator.collect_transitive(["B2"], orchestrator.dependency_graph())
    assert orchestrator.detect_cycle(orchestrator.dependency_graph()) is None
    assert orchestrator.detect_cycles(orchestrator.dependency_graph()) == []
    assert orchestrator.find_missing_dependencies(orchestrator.dependency_graph()) == []
    assert orchestrator.find_orphan_skills(orchestrator.dependency_graph()) == []
    assert orchestrator.validate_dag()["dag_status"] == "VALID"
    assert orchestrator.topological_sort(["B2"])
    assert orchestrator.parallel_waves(["B1", "B2"])
    assert orchestrator.skills_for_domain("B")
    assert orchestrator.full_pipeline_skills()
    orchestrator.build_plan("x", skill_ids=["B1"])


def test_skill_orchestrator_unknown_skill(orchestrator: SkillOrchestrator):
    orchestrator.discover_skills()
    with pytest.raises(KeyError):
        orchestrator.get_skill("ZZ99")


def test_dependency_resolver_edge_cases():
    graph = {"A": ["B"], "B": ["A"]}
    assert detect_cycle(graph)
    assert detect_cycles(graph)

    assert detect_cycles({"X": ["Y"], "Y": ["Z"], "Z": ["X"]})
    detect_cycles({"A": ["GHOST"]})  # dep not in graph keys (line 18 continue)

    graph_missing_dep = {"B2": ["MISSING"]}
    assert find_missing_dependencies(graph_missing_dep)

    assert find_orphan_skills({}) == []
    orphans = find_orphan_skills({"B1": ["B2"], "B2": ["B1"]})
    assert sorted(orphans) == ["B1", "B2"]

    with pytest.raises(KeyError):
        collect_transitive(["UNKNOWN"], {"A": []})

    with pytest.raises(ValueError):
        topological_sort(["A"], {"A": ["B"], "B": ["A"]})

    with pytest.raises(ValueError):
        parallel_waves(["A", "B"], {"A": ["B"], "B": ["A"]})


def test_planner_load_registry_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_registry(tmp_path / "missing.json")


def test_planner_skills_for_domain_invalid():
    registry = load_registry()
    with pytest.raises(ValueError):
        skills_for_domain(registry, "Z")


def test_planner_discover_skills_empty_dir(tmp_path):
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    assert discover_skills(skills_root) == {}


def test_planner_discover_master_skill(tmp_path, monkeypatch):
    import runtime.orchestrator.planner as planner_mod

    monkeypatch.setattr(planner_mod, "ROOT", tmp_path)
    skills_root = tmp_path / "skills"
    skills_root.mkdir()
    master = skills_root / "run_all_skills.skill.md"
    master.write_text(
        (ROOT / "skills" / "run_all_skills.skill.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    skills = discover_skills(skills_root)
    assert "ALL" in skills


def test_executor_edge_cases(tmp_path, orchestrator: SkillOrchestrator, monkeypatch):
    orchestrator.load_registry()
    orchestrator.discover_skills()
    context = RunContext(
        run_id="ex",
        run_dir=tmp_path / "ex",
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={"repository_path": str(ROOT)},
        continue_on_failure=False,
    )
    executor = SkillExecutor(context)
    skill_b2 = orchestrator.get_skill("B2")

    assert executor._artifact_input_available("not_json_key", skill_b2) is False

    bad_repo_ctx = RunContext(
        run_id="bad",
        run_dir=tmp_path / "bad",
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={"repository_path": str(tmp_path / "missing-repo")},
    )
    bad_executor = SkillExecutor(bad_repo_ctx)
    errors = bad_executor.validate_inputs(orchestrator.get_skill("B1"))
    assert any("repository_path not found" in e for e in errors)

    with patch.object(executor, "load_golden_output", return_value={"bad": True}):
        _, _, step_errors = executor.execute_steps(orchestrator.get_skill("B1"), "B1")
        assert step_errors

    monkeypatch.setenv("REPO_ANALYSER_AUTO_SKILL_DONE", "1")
    result = executor.run_skill(orchestrator.get_skill("B1"))
    assert result.status == "complete"

    plan = orchestrator.build_plan("abort", skill_ids=["B1"])
    plan.skills = {}
    fail_ctx = RunContext(
        run_id="abort",
        run_dir=tmp_path / "abort",
        golden_dir=tmp_path / "empty-golden",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={"repository_path": str(ROOT)},
        continue_on_failure=False,
    )
    summary = SkillExecutor(fail_ctx).run_plan(plan)
    assert summary["status"] == "failed"


def test_skill_runner_continue_on_failure_and_cli(tmp_path, orchestrator: SkillOrchestrator, capsys):
    from runtime.skill_runner import SkillRunner

    run_id = "abort-early"
    plan = orchestrator.build_plan(run_id, skill_ids=["B1"])
    plan.skills = {}
    runner = SkillRunner(
        run_id=run_id,
        run_dir=tmp_path / run_id,
        golden_dir=tmp_path / "empty",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={"repository_path": str(ROOT)},
        continue_on_failure=False,
    )
    summary = runner.run_plan(plan)
    assert summary["status"] == "failed"

    rc = skill_runner_main(["--skill", "B1", "--run-id", "cli-run", "--plan-only"])
    assert rc == 0
    assert "B1" in capsys.readouterr().out

    rc = skill_runner_main([])
    assert rc == 1

    rc = skill_runner_main(["--skill", "B1", "--run-id", "cli-run2"])
    assert rc in {0, 1}


def test_orchestrator_cli_no_args():
    assert orchestrator_cli_main([]) == 1


def test_skill_orchestrator_module_main(capsys):
    rc = skill_orchestrator_main(["--validate-dag"])
    assert rc == 0


def test_plugins_registry_and_base():
    registry = PluginRegistry()
    plugin = GoldenReplayPlugin(
        "B1",
        __import__("runtime.models", fromlist=["SkillSpec"]).SkillSpec.from_registry_entry(
            "B1", {"name": "x", "level": "B", "level_code": "B"}
        ),
    )
    registry.register(plugin)
    assert registry.get("b1") is plugin
    assert registry.all_plugins()
    assert registry.skill_ids() == ["B1"]

    class Bad(BaseSkillPlugin):
        id = "BAD"
        version = "0"

    with pytest.raises(NotImplementedError):
        Bad().execute(
            RunContext(
                run_id="r",
                run_dir=Path("/tmp/r"),
                golden_dir=Path("/tmp/g"),
                registry_path=Path("/tmp/reg.json"),
            )
        )


def test_golden_replay_plugin_execute(tmp_path, monkeypatch):
    from runtime.models import SkillSpec

    spec = SkillSpec.from_registry_entry("B1", {"name": "Inv", "level": "B", "level_code": "B"})
    plugin = GoldenReplayPlugin("B1", spec)
    context = RunContext(
        run_id="plug",
        run_dir=tmp_path / "plug",
        golden_dir=ROOT / "generated_projects" / "_golden",
        registry_path=ROOT / "core" / "skill_registry.json",
        inputs={**DEFAULT_RUN_INPUTS, "repository_path": str(ROOT)},
    )
    monkeypatch.setenv("REPO_ANALYSER_AUTO_SKILL_DONE", "0")
    result = plugin.execute(context)
    assert isinstance(result, SkillResult)
    assert result.status == "complete"


def test_skill_run_result_to_dict():
    legacy = SkillRunResult("B1", "complete", "p", "t0", "t1", [], [])
    assert legacy.to_dict()["skill_id"] == "B1"
