"""Interactive CLI for browsing Repo-Analyser skill run outputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from runtime.report_renderer import (
    SKILL_TITLES,
    export_run_markdown,
    export_skill_markdown,
    find_skill_json,
    load_skill_payload,
)
from runtime.report_ui import Theme, render_terminal_ui

ROOT = Path(__file__).resolve().parent.parent
GENERATED_ROOT = ROOT / "generated_projects"


def list_runs(generated_root: Path | None = None) -> list[Path]:
    root = generated_root or GENERATED_ROOT
    if not root.is_dir():
        return []
    runs = [p for p in root.iterdir() if p.is_dir() and not p.name.startswith("_")]
    return sorted(runs, key=lambda p: p.stat().st_mtime, reverse=True)


def list_skills(run_dir: Path) -> list[tuple[str, Path | None]]:
    skills: list[tuple[str, Path | None]] = []
    manifest_path = run_dir / "manifest.json"
    status_map: dict[str, str] = {}
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest.get("tasks", []):
            status_map[entry.get("task_id", "")] = entry.get("status", "unknown")

    seen: set[str] = set()
    for skill_dir in sorted(run_dir.iterdir(), key=lambda p: p.name):
        if not skill_dir.is_dir():
            continue
        skill_id = skill_dir.name
        if skill_id in seen:
            continue
        seen.add(skill_id)
        json_path = find_skill_json(skill_dir)
        skills.append((skill_id, json_path))

    if not skills and status_map:
        for skill_id in sorted(status_map):
            skill_dir = run_dir / skill_id
            skills.append((skill_id, find_skill_json(skill_dir) if skill_dir.is_dir() else None))
    return skills


def print_run_summary(run_dir: Path) -> None:
    print(f"\n{'=' * 60}")
    print(f"  Run: {run_dir.name}")
    print(f"  Path: {run_dir}")
    print(f"{'=' * 60}")

    manifest_path = run_dir / "manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        repo = manifest.get("repository_path")
        if repo:
            print(f"  Repository: {repo}")

    skills = list_skills(run_dir)
    print(f"\n  Skills ({len(skills)}):")
    for skill_id, json_path in skills:
        title = SKILL_TITLES.get(skill_id, skill_id)
        status = "has output" if json_path else "no output"
        print(f"    {skill_id:<4} {title:<32} [{status}]")
    print()


def view_skill(run_dir: Path, skill_id: str, *, write_md: bool = False) -> int:
    skill_dir = run_dir / skill_id
    if not skill_dir.is_dir():
        print(f"Skill directory not found: {skill_dir}", file=sys.stderr)
        return 1

    task_id, payload = load_skill_payload(skill_dir)
    if not payload:
        print(f"No JSON output for {skill_id} in {run_dir.name}", file=sys.stderr)
        return 1

    print(render_terminal_ui(run_dir.name, task_id or skill_id, payload, run_dir=run_dir))

    if write_md:
        md_path = export_skill_markdown(skill_dir)
        print(f"\n[written] {md_path}", file=sys.stderr)
    return 0


def _prompt_choice(label: str, count: int) -> int | None:
    while True:
        raw = input(f"{label} [1-{count}, q=quit]: ").strip().lower()
        if raw in {"q", "quit", "exit"}:
            return None
        if raw.isdigit():
            choice = int(raw)
            if 1 <= choice <= count:
                return choice - 1
        print("  Invalid choice — try again.")


def interactive_loop(generated_root: Path | None = None) -> int:
    root = generated_root or GENERATED_ROOT
    theme = Theme()
    print("")
    print(theme.cyan("╭──────────────────────────────────────────────────────────────────────╮"))
    print(
        theme.cyan("│")
        + f"  {theme.bold('Repo-Analyser Run Browser')}  {theme.dim('browse past skill outputs')}"
        + " " * 8
        + theme.cyan("│")
    )
    print(theme.cyan("╰──────────────────────────────────────────────────────────────────────╯"))
    print("")

    while True:
        runs = list_runs(root)
        if not runs:
            print(f"No runs found under {root}")
            return 1

        print("Available runs:")
        for index, run_dir in enumerate(runs, start=1):
            skill_count = sum(1 for _, jp in list_skills(run_dir) if jp)
            print(f"  {index:>2}. {run_dir.name:<24} ({skill_count} skills with output)")

        run_choice = _prompt_choice("Select run", len(runs))
        if run_choice is None:
            print("Bye.")
            return 0

        run_dir = runs[run_choice]
        print_run_summary(run_dir)

        while True:
            skills = list_skills(run_dir)
            if not skills:
                print("No skills in this run.")
                break

            print("Skills:")
            for index, (skill_id, json_path) in enumerate(skills, start=1):
                title = SKILL_TITLES.get(skill_id, skill_id)
                marker = "✓" if json_path else "·"
                print(f"  {index:>2}. [{marker}] {skill_id} — {title}")

            print("\nActions:")
            print("  Enter number — view skill report in terminal")
            print("  e          — export all skills to output.md + REPORT.md")
            print("  b          — back to run list")
            print("  q          — quit")

            raw = input("\nChoice: ").strip().lower()
            if raw in {"q", "quit", "exit"}:
                print("Bye.")
                return 0
            if raw in {"b", "back"}:
                break
            if raw in {"e", "export"}:
                paths = export_run_markdown(run_dir)
                print(f"\nExported {len(paths)} markdown file(s).")
                print(f"  Index: {run_dir / 'REPORT.md'}")
                continue
            if raw.isdigit():
                choice = int(raw)
                if 1 <= choice <= len(skills):
                    skill_id = skills[choice - 1][0]
                    print("\n" + "-" * 60 + "\n")
                    from runtime.skill_finish import show_skill_report

                    show_skill_report(run_dir, skill_id, interactive=True)
                    continue
            print("  Invalid choice.")


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Browse and export Repo-Analyser run reports")
    parser.add_argument("--generated-root", type=Path, default=GENERATED_ROOT)
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list-runs", help="List available run directories")

    p_view = sub.add_parser("view", help="Render a skill report to the terminal")
    p_view.add_argument("--run-id", required=True, help="Run directory name under generated_projects/")
    p_view.add_argument("--skill", required=True, help="Skill ID, e.g. B1")
    p_view.add_argument("--write-md", action="store_true", help="Also write output.md")

    p_export = sub.add_parser("export-md", help="Export Markdown reports for a run")
    p_export.add_argument("--run-id", required=True, help="Run directory name")
    p_export.add_argument("--skill", help="Export only one skill (optional)")

    sub.add_parser("interactive", help="Interactive report browser")

    p_show = sub.add_parser("show", help="Show a completed skill report (post-skill UI)")
    p_show.add_argument("--run-id", required=True, help="Run directory name")
    p_show.add_argument("--skill", required=True, help="Skill ID, e.g. B1")
    p_show.add_argument("--no-open", action="store_true", help="Do not open output.md in editor")
    p_show.add_argument("--no-interactive", action="store_true", help="Print report and exit")

    args = parser.parse_args(argv)
    root = args.generated_root

    if args.command == "list-runs":
        for run_dir in list_runs(root):
            print(run_dir.name)
        return 0

    if args.command == "view":
        run_dir = root / args.run_id
        return view_skill(run_dir, args.skill.upper(), write_md=args.write_md)

    if args.command == "export-md":
        run_dir = root / args.run_id
        if not run_dir.is_dir():
            print(f"Run not found: {run_dir}", file=sys.stderr)
            return 1
        if args.skill:
            skill_dir = run_dir / args.skill.upper()
            path = export_skill_markdown(skill_dir)
            print(path)
        else:
            paths = export_run_markdown(run_dir)
            for path in paths:
                print(path)
        return 0

    if args.command == "interactive":
        return interactive_loop(root)

    if args.command == "show":
        from runtime.skill_finish import show_skill_report

        run_dir = root / args.run_id
        return show_skill_report(
            run_dir,
            args.skill.upper(),
            save_md=False,
            interactive=not args.no_interactive,
        )

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
