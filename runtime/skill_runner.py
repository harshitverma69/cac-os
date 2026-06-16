"""Deterministic skill executor — no LLM, no inference."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path

from runtime.deterministic import (
    DETERMINISTIC_STAMP,
    canonical_json_dumps,
    strip_volatile_keys,
)
from runtime.skill_orchestrator import ExecutionPlan, SkillOrchestrator
from runtime.skill_parser import SkillDefinition, task_sort_key, validate_output_schema

ROOT = Path(__file__).resolve().parent.parent
GOLDEN_DIR = ROOT / "generated_projects" / "_golden"
GENERATED_ROOT = ROOT / "generated_projects"
CORE_REGISTRY_PATH = ROOT / "core" / "skill_registry.json"


DEFAULT_RUN_INPUTS = {
    "repository_path": str(ROOT),
    "task_description": "cac-os-deterministic-run",
    "lanes": 2,
    "module_path": ".",
    "output_dir": str(GENERATED_ROOT),
    "service_path": str(ROOT),
    "project_name": "cac-os-demo-project",
    "mode": "api",
    "entry_point_id": "GET:/health",
    "service_port": 8080,
    "ci_platform": "github_actions",
    "bootstrap_type": "makefile_mise",
    "cluster": "kind",
    "provider": "aws",
    "resources": ["s3", "ec2"],
    "benchmark_target": "GET /health",
    "diff_or_pr_ref": "HEAD~1",
    "change_spec": {"description": "deterministic change", "target_module": "app"},
    "bug_context": {"symptoms": "none", "reproduction_hint": "n/a"},
}


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


@dataclass
class SkillRunResult:
    skill_id: str
    status: str
    output_path: str
    started_at: str
    completed_at: str
    steps_executed: list[str]
    errors: list[str]

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "status": self.status,
            "output_path": self.output_path,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "steps_executed": self.steps_executed,
            "errors": sorted(self.errors),
        }


class SkillRunner:
    def __init__(
        self,
        run_id: str,
        run_dir: Path | None = None,
        golden_dir: Path | None = None,
        registry_path: Path | None = None,
        inputs: dict | None = None,
        continue_on_failure: bool = True,
    ):
        self.run_id = run_id
        self.run_dir = run_dir or (GENERATED_ROOT / run_id)
        self.golden_dir = golden_dir or GOLDEN_DIR
        self.registry_path = registry_path or CORE_REGISTRY_PATH
        self.inputs = {**DEFAULT_RUN_INPUTS, **(inputs or {})}
        self.continue_on_failure = continue_on_failure
        self.registry = json.loads(self.registry_path.read_text(encoding="utf-8"))
        self.execution_log: list[dict] = []

    def _artifact_input_available(self, key: str, skill: SkillDefinition) -> bool:
        if key in self.inputs:
            return True
        if not key.endswith(".json"):
            return False
        for dep in sorted(skill.depends_on, key=task_sort_key):
            dep_meta = self.registry.get("skills", {}).get(dep, {})
            if dep_meta.get("output_file") == key:
                return (self.run_dir / dep / "output.json").is_file()
        return False

    def validate_inputs(self, skill: SkillDefinition) -> list[str]:
        errors: list[str] = []
        contract = skill.input_contract or {}

        for key in sorted(contract):
            if key.endswith(".json"):
                if not self._artifact_input_available(key, skill):
                    errors.append(f"MISSING_INPUT: {key}")
                continue
            if key not in self.inputs:
                errors.append(f"MISSING_INPUT: {key}")

        repository_path = self.inputs.get("repository_path")
        if "repository_path" in contract and repository_path:
            if not Path(str(repository_path)).exists():
                errors.append("INPUT_CONTRACT_VIOLATION: repository_path not found")

        for dep in sorted(skill.depends_on, key=task_sort_key):
            dep_output = self.run_dir / dep / "output.json"
            if not dep_output.is_file():
                errors.append(f"MISSING_DEPENDENCY_OUTPUT: {dep}")

        return sorted(errors)

    def load_golden_output(self, skill_id: str) -> dict:
        meta = self.registry["skills"][skill_id]
        golden_path = self.golden_dir / skill_id / meta["output_file"]
        if not golden_path.is_file():
            raise FileNotFoundError(f"Golden output missing: {golden_path}")
        return json.loads(golden_path.read_text(encoding="utf-8"))

    def normalize_output(self, output: dict, skill_id: str) -> dict:
        normalized = strip_volatile_keys(dict(output))
        normalized["task_id"] = skill_id
        return normalized

    def execute_steps(self, skill: SkillDefinition, skill_id: str) -> tuple[dict, list[str], list[str]]:
        steps_executed: list[str] = []
        errors: list[str] = []

        steps_executed.append("validate_input_contract")
        input_errors = self.validate_inputs(skill)
        if input_errors:
            return {}, steps_executed, input_errors

        steps_executed.append("load_golden_reference_output")
        try:
            output = self.load_golden_output(skill_id)
        except FileNotFoundError as exc:
            return {}, steps_executed, [str(exc)]

        steps_executed.append("normalize_output")
        output = self.normalize_output(output, skill_id)

        steps_executed.append("validate_output_contract")
        schema_errors = validate_output_schema(output, skill.output_contract)
        if schema_errors:
            errors.extend(schema_errors)

        for step in skill.execution_steps:
            steps_executed.append(f"record_step:{step[:80]}")

        return output, steps_executed, errors

    def run_skill(self, skill: SkillDefinition) -> SkillRunResult:
        stamp = DETERMINISTIC_STAMP
        skill_id = skill.skill_id
        out_dir = self.run_dir / skill_id
        out_dir.mkdir(parents=True, exist_ok=True)
        output_path = out_dir / "output.json"

        output, steps, errors = self.execute_steps(skill, skill_id)
        status = "complete" if output and not errors else "failed"

        if status == "complete":
            output_path.write_text(canonical_json_dumps(output), encoding="utf-8")

        result = SkillRunResult(
            skill_id=skill_id,
            status=status,
            output_path=_display_path(output_path),
            started_at=stamp,
            completed_at=stamp,
            steps_executed=steps,
            errors=errors,
        )
        self.execution_log.append(result.to_dict())
        return result

    def run_plan(self, plan: ExecutionPlan) -> dict:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        results: list[SkillRunResult] = []

        for wave_index, wave in enumerate(plan.parallel_waves):
            for skill_id in wave:
                skill = plan.skills.get(skill_id)
                if skill is None:
                    orchestrator = SkillOrchestrator(registry_path=self.registry_path)
                    orchestrator.discover_skills()
                    skill = orchestrator.get_skill(skill_id)

                result = self.run_skill(skill)
                results.append(result)
                if result.status != "complete" and not self.continue_on_failure:
                    return self._finalize(plan, results, wave_index, aborted=True)

        aborted = any(result.status != "complete" for result in results)
        return self._finalize(plan, results, len(plan.parallel_waves) - 1, aborted=aborted)

    def _finalize(
        self,
        plan: ExecutionPlan,
        results: list[SkillRunResult],
        last_wave: int,
        aborted: bool,
    ) -> dict:
        log_path = self.run_dir / "execution_log.json"
        final_path = self.run_dir / "final_report.json"
        stamp = DETERMINISTIC_STAMP

        completed = sorted(
            [result.skill_id for result in results if result.status == "complete"],
            key=task_sort_key,
        )
        failed = sorted(
            [result.skill_id for result in results if result.status != "complete"],
            key=task_sort_key,
        )

        log_doc = {
            "aborted": aborted,
            "completed_at": stamp,
            "entries": sorted([result.to_dict() for result in results], key=lambda item: task_sort_key(item["skill_id"])),
            "execution_order": plan.execution_order,
            "last_wave_executed": last_wave,
            "parallel_waves": plan.parallel_waves,
            "run_id": self.run_id,
            "started_at": stamp,
        }
        log_path.write_text(canonical_json_dumps(log_doc), encoding="utf-8")

        final_doc = {
            "completed_count": len(completed),
            "execution_log": _display_path(log_path),
            "failed_count": len(failed),
            "outputs": {
                skill_id: _display_path(self.run_dir / skill_id / "output.json")
                for skill_id in completed
            },
            "run_id": self.run_id,
            "skills_completed": completed,
            "skills_failed": failed,
            "skills_requested": plan.requested,
            "status": "failed" if aborted else "complete",
            "total_skills": len(plan.execution_order),
        }
        final_path.write_text(canonical_json_dumps(final_doc), encoding="utf-8")

        return {
            "completed": completed,
            "execution_log": _display_path(log_path),
            "failed": failed,
            "final_report": _display_path(final_path),
            "status": final_doc["status"],
        }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="CAC-OS deterministic skill runner")
    parser.add_argument("--run-id", default="pipeline-run")
    parser.add_argument("--skill", help="Single skill ID, e.g. B1")
    parser.add_argument("--domain", choices=["B", "I", "A", "D"], help="Run all skills in domain")
    parser.add_argument("--full-pipeline", action="store_true", help="Run all 24 skills in DAG order")
    parser.add_argument("--repository-path", default=str(ROOT))
    parser.add_argument("--plan-only", action="store_true", help="Print execution plan only")
    args = parser.parse_args(argv)

    orchestrator = SkillOrchestrator()
    orchestrator.load_registry()
    orchestrator.discover_skills()

    if args.full_pipeline:
        plan = orchestrator.build_plan(args.run_id, full_pipeline=True)
    elif args.domain:
        plan = orchestrator.build_plan(args.run_id, domain=args.domain)
    elif args.skill:
        plan = orchestrator.build_plan(args.run_id, skill_ids=[args.skill.upper()])
    else:
        print("Provide --skill, --domain, or --full-pipeline", file=sys.stderr)
        return 1

    if args.plan_only:
        print(canonical_json_dumps(plan.to_dict()).rstrip())
        return 0

    runner = SkillRunner(
        run_id=args.run_id,
        inputs={"repository_path": args.repository_path},
    )
    summary = runner.run_plan(plan)
    print(canonical_json_dumps(summary).rstrip())
    return 0 if summary["status"] == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
