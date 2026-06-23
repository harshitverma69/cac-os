"""Aggregate skill run results into execution and final reports."""

from __future__ import annotations

from pathlib import Path

from runtime.deterministic import DETERMINISTIC_STAMP, canonical_json_dumps
from runtime.models import ExecutionReport, SkillResult
from runtime.orchestrator.planner import ExecutionPlan
from runtime.skill_parser import task_sort_key

ROOT = Path(__file__).resolve().parent.parent.parent


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def aggregate_results(
    plan: ExecutionPlan,
    results: list[SkillResult],
    run_dir: Path,
    last_wave: int,
    aborted: bool,
) -> ExecutionReport:
    log_path = run_dir / "execution_log.json"
    final_path = run_dir / "final_report.json"
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
        "run_id": plan.run_id,
        "started_at": stamp,
    }
    log_path.write_text(canonical_json_dumps(log_doc), encoding="utf-8")

    status = "failed" if aborted else "complete"
    final_doc = {
        "completed_count": len(completed),
        "execution_log": display_path(log_path),
        "failed_count": len(failed),
        "outputs": {skill_id: display_path(run_dir / skill_id / "output.json") for skill_id in completed},
        "run_id": plan.run_id,
        "skills_completed": completed,
        "skills_failed": failed,
        "skills_requested": plan.requested,
        "status": status,
        "total_skills": len(plan.execution_order),
    }
    final_path.write_text(canonical_json_dumps(final_doc), encoding="utf-8")

    return ExecutionReport(
        run_id=plan.run_id,
        status=status,
        completed=completed,
        failed=failed,
        execution_log=display_path(log_path),
        final_report=display_path(final_path),
        skills_requested=plan.requested,
        total_skills=len(plan.execution_order),
    )


def report_to_runner_summary(report: ExecutionReport) -> dict:
    return {
        "completed": report.completed,
        "execution_log": report.execution_log,
        "failed": report.failed,
        "final_report": report.final_report,
        "status": report.status,
    }
