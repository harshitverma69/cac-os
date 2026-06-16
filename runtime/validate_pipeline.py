"""Full pipeline validation — DAG, schema, coverage, determinism."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from runtime.deterministic import canonical_json_dumps
from runtime.skill_orchestrator import SkillOrchestrator
from runtime.skill_parser import parse_skill_markdown, task_sort_key, validate_output_schema
from runtime.skill_registry_builder import validate_skill_coverage

ROOT = Path(__file__).resolve().parent.parent
GENERATED_ROOT = ROOT / "generated_projects"
SKILLS_ROOT = ROOT / "skills"
CORE_REGISTRY_PATH = ROOT / "core" / "skill_registry.json"


def expected_skill_ids() -> list[str]:
    return [f"{level}{index}" for level in "BIAD" for index in range(1, 7)]


def load_skill_contracts(orchestrator: SkillOrchestrator) -> dict[str, dict]:
    orchestrator.discover_skills()
    contracts: dict[str, dict] = {}
    for skill_id in expected_skill_ids():
        if skill_id in orchestrator._skills:
            contracts[skill_id] = orchestrator._skills[skill_id].output_contract
    return contracts


def validate_run_outputs(run_dir: Path, contracts: dict[str, dict]) -> tuple[list[str], list[dict]]:
    failed_skills: list[str] = []
    invalid_outputs: list[dict] = []

    for skill_id in expected_skill_ids():
        output_path = run_dir / skill_id / "output.json"
        if not output_path.is_file():
            failed_skills.append(skill_id)
            invalid_outputs.append(
                {"skill_id": skill_id, "errors": ["MISSING_OUTPUT_FILE"]}
            )
            continue

        try:
            payload = json.loads(output_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failed_skills.append(skill_id)
            invalid_outputs.append(
                {"skill_id": skill_id, "errors": [f"INVALID_JSON: {exc}"]}
            )
            continue

        contract = contracts.get(skill_id, {})
        errors = validate_output_schema(payload, contract)
        if errors:
            if skill_id not in failed_skills:
                failed_skills.append(skill_id)
            invalid_outputs.append({"skill_id": skill_id, "errors": errors})

    return sorted(failed_skills, key=task_sort_key), invalid_outputs


def compare_skill_outputs(run_a: Path, run_b: Path) -> tuple[bool, list[str]]:
    mismatches: list[str] = []

    for skill_id in expected_skill_ids():
        path_a = run_a / skill_id / "output.json"
        path_b = run_b / skill_id / "output.json"
        if not path_a.is_file() or not path_b.is_file():
            mismatches.append(f"{skill_id}: missing output in one run")
            continue
        bytes_a = path_a.read_bytes()
        bytes_b = path_b.read_bytes()
        if bytes_a != bytes_b:
            mismatches.append(f"{skill_id}: output.json differs")

    return not mismatches, mismatches


def validate_pipeline(
    run_id: str,
    compare_run_id: str | None = None,
) -> dict:
    orchestrator = SkillOrchestrator(
        skills_root=SKILLS_ROOT,
        registry_path=CORE_REGISTRY_PATH,
    )
    orchestrator.load_registry()

    dag_report = orchestrator.validate_dag()
    coverage_report = validate_skill_coverage(
        json.loads(CORE_REGISTRY_PATH.read_text(encoding="utf-8")),
        SKILLS_ROOT,
    )

    run_dir = GENERATED_ROOT / run_id
    contracts = load_skill_contracts(orchestrator)
    failed_skills, invalid_outputs = validate_run_outputs(run_dir, contracts)

    deterministic = True
    determinism_mismatches: list[str] = []
    if compare_run_id:
        compare_dir = GENERATED_ROOT / compare_run_id
        deterministic, determinism_mismatches = compare_skill_outputs(run_dir, compare_dir)

    dag_valid = dag_report["dag_status"] == "VALID"
    coverage_ok = coverage_report["coverage_status"] == "100%"
    outputs_ok = not failed_skills and not invalid_outputs

    pipeline_status = "PASS" if dag_valid and coverage_ok and outputs_ok and deterministic else "FAIL"

    return {
        "pipeline_status": pipeline_status,
        "failed_skills": failed_skills,
        "invalid_outputs": invalid_outputs,
        "dag_valid": dag_valid,
        "dag_report": dag_report,
        "coverage_report": coverage_report,
        "deterministic": deterministic,
        "determinism_mismatches": determinism_mismatches,
        "run_id": run_id,
        "compare_run_id": compare_run_id,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="CAC-OS pipeline validator")
    parser.add_argument("--run-id", required=True, help="Pipeline run directory name")
    parser.add_argument(
        "--compare-run-id",
        help="Second run id for determinism comparison of skill outputs",
    )
    args = parser.parse_args(argv)

    report = validate_pipeline(args.run_id, args.compare_run_id)
    print(canonical_json_dumps(report).rstrip())
    return 0 if report["pipeline_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
