"""Rich terminal UI for Repo-Analyser skill reports (no markdown files)."""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from runtime.report_renderer import SKILL_TITLES, render_report
from runtime.skill_constants import cursor_slash_command

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "core" / "skill_registry.json"

LEVEL_LABELS = {
    "B": "BASIC",
    "I": "INTERMEDIATE",
    "A": "ADVANCED",
    "D": "INFRA",
}

WIDTH = 72


class Theme:
    """ANSI colors; disabled when not a TTY or NO_COLOR is set."""

    def __init__(self) -> None:
        enabled = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
        self._e = enabled

    def wrap(self, code: str, text: str) -> str:
        if not self._e:
            return text
        return f"\033[{code}m{text}\033[0m"

    def bold(self, t: str) -> str:
        return self.wrap("1", t)

    def dim(self, t: str) -> str:
        return self.wrap("2", t)

    def cyan(self, t: str) -> str:
        return self.wrap("36", t)

    def green(self, t: str) -> str:
        return self.wrap("32", t)

    def yellow(self, t: str) -> str:
        return self.wrap("33", t)

    def red(self, t: str) -> str:
        return self.wrap("31", t)

    def magenta(self, t: str) -> str:
        return self.wrap("35", t)

    def blue(self, t: str) -> str:
        return self.wrap("34", t)


def load_skill_meta(skill_id: str) -> dict[str, Any]:
    if not REGISTRY_PATH.is_file():
        return {}
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return registry.get("skills", {}).get(skill_id.upper(), {})


def _strip_ansi(text: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", text)


def _truncate(text: str, max_len: int) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def _box_top(title: str = "", theme: Theme | None = None) -> str:
    if title:
        label = f"─ {title} "
        fill = "─" * max(1, WIDTH - len(label) - 1)
        inner = (theme or Theme()).dim(label + fill)
        return f"╭{inner}╮"
    return f"╭{'─' * (WIDTH - 2)}╮"


def _box_bottom() -> str:
    return f"╰{'─' * (WIDTH - 2)}╯"


def _box_line(content: str) -> str:
    plain = _strip_ansi(content)
    pad = max(0, WIDTH - 4 - len(plain))
    return f"│ {content}{' ' * pad} │"


def compute_outcome(skill_id: str, payload: dict[str, Any]) -> tuple[str, str, str, list[tuple[str, str]]]:
    """Return (status_label, status_tone, headline, metric_rows)."""
    skill_id = skill_id.upper()
    metrics: list[tuple[str, str]] = []

    repo = payload.get("repository_path") or payload.get("review_target", {}).get("repository_path", "")
    if repo:
        metrics.append(("Repository", _truncate(str(repo), 52)))

    if payload.get("generated_at"):
        metrics.append(("Generated", str(payload["generated_at"])))

    scan_complete = payload.get("scan_complete")
    warnings = payload.get("warnings") or []

    if skill_id == "A5":
        issues = payload.get("issues") or []
        blocking = sum(1 for i in issues if i.get("severity") == "blocking")
        non_blocking = len(issues) - blocking
        metrics.append(("Issues", str(len(issues))))
        metrics.append(("Blocking", str(blocking)))
        metrics.append(("Non-blocking", str(non_blocking)))
        target = payload.get("review_target", {})
        if target.get("diff_or_pr_ref"):
            metrics.append(("Reviewed", str(target["diff_or_pr_ref"])))
        if blocking:
            return (
                "NEEDS FIX",
                "warn",
                f"{blocking} blocking issue(s) must be addressed before merge",
                metrics,
            )
        if issues:
            return ("REVIEWED", "ok", f"{len(issues)} issue(s) documented — none blocking", metrics)
        return ("CLEAN", "ok", "No issues found — ready to merge", metrics)

    if skill_id == "B1":
        files = payload.get("files_scanned", 0)
        artifacts = payload.get("artifacts") or {}
        total = sum(len(v) for v in artifacts.values() if isinstance(v, list))
        modules = len(payload.get("modules") or [])
        metrics.extend([("Files scanned", str(files)), ("Artifacts", str(total)), ("Modules", str(modules))])
        if files > 0 and total > 0:
            return ("INVENTORY OK", "ok", f"Catalogued {total} artifacts across {modules} module(s)", metrics)
        return ("EMPTY", "warn", "Scan completed but no artifacts extracted", metrics)

    if skill_id == "B2":
        endpoints = payload.get("endpoints") or []
        frontend = payload.get("frontend_routes") or []
        metrics.append(("API endpoints", str(len(endpoints))))
        metrics.append(("Frontend routes", str(len(frontend))))
        if endpoints:
            return ("MAPPED", "ok", f"Found {len(endpoints)} API endpoint(s)", metrics)
        return ("NO ROUTES", "warn", "No API endpoints discovered", metrics)

    if skill_id == "B3":
        framework = payload.get("framework", "unknown")
        tests = len(payload.get("test_files") or [])
        metrics.append(("Framework", str(framework)))
        metrics.append(("Test files", str(tests)))
        result = payload.get("command_result") or {}
        exit_code = result.get("exit_code")
        if exit_code == 0:
            return ("TESTS PASS", "ok", f"{framework} tests runnable — last run exit 0", metrics)
        if exit_code is not None and exit_code >= 0:
            return ("TESTS FAIL", "fail", f"Test command exited with code {exit_code}", metrics)
        return ("DISCOVERED", "ok", f"Found {tests} test file(s) for {framework}", metrics)

    if skill_id == "I1":
        tables = payload.get("tables") or payload.get("entities") or []
        metrics.append(("Tables / entities", str(len(tables))))
        if tables:
            return ("SCHEMA OK", "ok", f"Documented {len(tables)} table(s) / entity(ies)", metrics)
        return ("NO SCHEMA", "warn", "No tables or entities found in source", metrics)

    if skill_id == "I2":
        steps = payload.get("steps") or []
        metrics.append(("Trace steps", str(len(steps))))
        if steps:
            return ("TRACED", "ok", f"End-to-end flow has {len(steps)} step(s)", metrics)
        return ("INCOMPLETE", "warn", "Flow trace has no steps", metrics)

    if skill_id == "I6":
        root_cause = payload.get("root_cause") or {}
        if root_cause.get("file_path"):
            metrics.append(("Root cause", _truncate(str(root_cause.get("file_path")), 52)))
        verified = payload.get("verification") or payload.get("fix_verified")
        if verified:
            return ("FIXED", "ok", "Bug diagnosed and fix verified", metrics)
        return ("DIAGNOSED", "ok", "Root cause identified", metrics)

    if scan_complete is False:
        return ("INCOMPLETE", "warn", "Scan did not complete — check warnings", metrics)
    if warnings:
        metrics.append(("Warnings", str(len(warnings))))
        return ("COMPLETE", "warn", f"Finished with {len(warnings)} warning(s)", metrics)
    return ("COMPLETE", "ok", "Skill finished successfully", metrics)


def _status_badge(label: str, tone: str, theme: Theme) -> str:
    icons = {"ok": "✔", "warn": "◆", "fail": "✖"}
    colors = {"ok": theme.green, "warn": theme.yellow, "fail": theme.red}
    icon = icons.get(tone, "●")
    paint = colors.get(tone, theme.cyan)
    return paint(f"{icon} {label}")


def render_header(run_id: str, skill_id: str, meta: dict[str, Any], theme: Theme) -> list[str]:
    skill_id = skill_id.upper()
    name = meta.get("name") or SKILL_TITLES.get(skill_id, skill_id)
    level_code = meta.get("level_code") or skill_id[0]
    level = meta.get("level") or LEVEL_LABELS.get(level_code, level_code)
    command = cursor_slash_command(skill_id)
    objective = _truncate(meta.get("description", ""), WIDTH - 8)

    lines = [
        "",
        _box_top(theme=theme),
        _box_line(f"{theme.bold(theme.cyan('Repo-Analyser'))}  {theme.dim('repository analysis framework')}"),
        _box_line(""),
        _box_line(f"{theme.dim('Agent')}    {theme.bold(skill_id)}  {theme.magenta('·')}  {name}"),
        _box_line(f"{theme.dim('Level')}    {theme.blue(level)}"),
        _box_line(f"{theme.dim('Command')}  {theme.cyan(command)}"),
        _box_line(f"{theme.dim('Run')}      {run_id}"),
    ]
    if objective:
        lines.append(_box_line(f"{theme.dim('Goal')}     {_truncate(objective, WIDTH - 12)}"))
    lines.append(_box_bottom())
    return lines


def render_outcome_panel(
    status_label: str,
    tone: str,
    headline: str,
    metrics: list[tuple[str, str]],
    theme: Theme,
) -> list[str]:
    lines = [
        "",
        _box_top("Outcome"),
        _box_line(_status_badge(status_label, tone, theme)),
        _box_line(theme.bold(_truncate(headline, WIDTH - 6))),
    ]
    if metrics:
        lines.append(_box_line(""))
        for key, value in metrics:
            lines.append(_box_line(f"{theme.dim(key + ':')}  {_truncate(value, WIDTH - 14 - len(key))}"))
    lines.append(_box_bottom())
    return lines


def render_a5_issues(issues: list[dict], theme: Theme) -> list[str]:
    if not issues:
        return [_box_line(theme.dim("No issues."))]

    lines: list[str] = []
    for index, issue in enumerate(issues, start=1):
        sev = issue.get("severity", "").replace("_", " ").upper()
        sev_paint = theme.red if "BLOCKING" in sev and "NON" not in sev else theme.yellow
        cat = issue.get("category", "")
        iid = issue.get("id", f"#{index}")
        lines.append(_box_line(""))
        lines.append(_box_line(f"{theme.bold(iid)}  {sev_paint(sev)}  {theme.dim(cat)}"))
        if issue.get("file_path"):
            loc = issue["file_path"]
            if issue.get("line"):
                loc += f":{issue['line']}"
            lines.append(_box_line(f"  {theme.dim('at')}  {theme.cyan(_truncate(loc, WIDTH - 10))}"))
        if issue.get("description"):
            desc = issue["description"]
            for chunk_start in range(0, len(desc), WIDTH - 6):
                lines.append(_box_line(f"  {_truncate(desc[chunk_start : chunk_start + WIDTH - 6], WIDTH - 4)}"))
        if issue.get("suggested_fix"):
            lines.append(_box_line(f"  {theme.green('fix')}  {_truncate(issue['suggested_fix'], WIDTH - 10)}"))
        steps = issue.get("verification_steps") or []
        if steps:
            lines.append(_box_line(f"  {theme.dim('verify')}"))
            for step in steps[:3]:
                lines.append(_box_line(f"    {theme.dim('·')} {_truncate(str(step), WIDTH - 8)}"))
    return lines


def render_b1_highlights(payload: dict, theme: Theme) -> list[str]:
    lines: list[str] = []
    artifacts = payload.get("artifacts") or {}
    for category in sorted(artifacts):
        items = artifacts[category] or []
        if not items:
            continue
        lines.append(_box_line(f"{theme.bold(category.replace('_', ' ').title())}  {theme.dim(f'({len(items)})')}"))
        for item in items[:8]:
            name = item.get("name", "")
            path = _truncate(item.get("file_path", ""), 40)
            lines.append(_box_line(f"  {theme.cyan('•')} {name}  {theme.dim(path)}"))
        if len(items) > 8:
            lines.append(_box_line(f"  {theme.dim(f'… and {len(items) - 8} more')}"))
    return lines or [_box_line(theme.dim("No artifacts."))]


def render_details(skill_id: str, payload: dict, theme: Theme) -> list[str]:
    skill_id = skill_id.upper()
    lines = ["", _box_top("Details")]

    if skill_id == "A5":
        lines.extend(render_a5_issues(payload.get("issues") or [], theme))
    elif skill_id == "B1":
        lines.extend(render_b1_highlights(payload, theme))
    elif skill_id == "B2":
        endpoints = payload.get("endpoints") or []
        for ep in endpoints[:15]:
            method = ep.get("method", "")
            route = ep.get("route", ep.get("path", ""))
            handler = ep.get("handler_method", ep.get("handler", ""))
            method_col = theme.yellow(f"{method:<7}")
            lines.append(_box_line(f"  {method_col} {route}  {theme.dim('→')} {handler}"))
        if len(endpoints) > 15:
            lines.append(_box_line(theme.dim(f"  … and {len(endpoints) - 15} more")))
    elif skill_id == "B3":
        for key in ("framework", "config_file"):
            if payload.get(key):
                lines.append(_box_line(f"  {theme.dim(key)}  {payload[key]}"))
        cmds = payload.get("commands") or payload.get("test_commands") or []
        if isinstance(cmds, dict):
            cmds = list(cmds.values())
        for cmd in cmds[:5]:
            c = cmd.get("command", cmd) if isinstance(cmd, dict) else cmd
            lines.append(_box_line(f"  {theme.green('$')} {c}"))
    else:
        body = render_report(payload, task_id=skill_id)
        for raw_line in body.splitlines()[4:40]:
            if raw_line.strip():
                lines.append(_box_line(f"  {_truncate(raw_line, WIDTH - 4)}"))

    limitations = payload.get("limitations") or []
    if limitations:
        lines.append(_box_line(""))
        lines.append(_box_line(theme.dim("Limitations")))
        for lim in limitations[:4]:
            lines.append(_box_line(f"  {theme.dim('·')} {_truncate(lim, WIDTH - 8)}"))

    lines.append(_box_bottom())
    return lines


def render_footer(theme: Theme) -> list[str]:
    return [
        "",
        theme.dim("─" * WIDTH),
        theme.dim("  JSON → generated_projects/<run>/<skill>/output.json"),
        theme.dim("  UI   → http://127.0.0.1:8765 (auto-opens Live runs tab)"),
        "",
    ]


def render_terminal_ui(
    run_id: str,
    skill_id: str,
    payload: dict[str, Any],
    *,
    run_dir: Path | None = None,
) -> str:
    """Build the full terminal report string."""
    theme = Theme()
    skill_id = skill_id.upper()
    meta = load_skill_meta(skill_id)
    status_label, tone, headline, metrics = compute_outcome(skill_id, payload)

    parts: list[str] = []
    parts.extend(render_header(run_id, skill_id, meta, theme))
    parts.extend(render_outcome_panel(status_label, tone, headline, metrics, theme))
    parts.extend(render_details(skill_id, payload, theme))
    parts.extend(render_footer(theme))
    return "\n".join(parts)
