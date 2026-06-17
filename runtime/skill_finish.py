"""Post-skill hook: write output JSON and display report in the terminal."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from runtime.deterministic import canonical_json_dumps
from runtime.report_renderer import export_run_markdown, export_skill_markdown, find_skill_json, load_skill_payload
from runtime.report_ui import render_terminal_ui

ROOT = Path(__file__).resolve().parent.parent
GENERATED_ROOT = ROOT / "generated_projects"


def export_markdown_reports(run_dir: Path, skill_dir: Path) -> None:
    """Write output.md and refresh run REPORT.md (fallback when CLI UI is unavailable)."""
    try:
        export_skill_markdown(skill_dir)
        export_run_markdown(run_dir)
    except Exception as exc:
        print(f"Warning: markdown export failed: {exc}", file=sys.stderr)


def write_skill_output(
    run_id: str,
    skill_id: str,
    payload: dict[str, Any],
    *,
    generated_root: Path | None = None,
    save_md: bool = True,
    show_ui: bool = True,
) -> Path:
    """Write output.json for a skill, export markdown, and optionally display the terminal UI."""
    root = generated_root or GENERATED_ROOT
    skill_id = skill_id.upper()
    run_dir = root / run_id
    skill_dir = run_dir / skill_id
    skill_dir.mkdir(parents=True, exist_ok=True)
    output_path = skill_dir / "output.json"
    output_path.write_text(canonical_json_dumps(payload), encoding="utf-8")
    if save_md:
        export_markdown_reports(run_dir, skill_dir)
    try:
        from runtime.frontend_sync import publish_skill_run

        publish_skill_run(run_id, skill_id, payload)
    except Exception as exc:
        print(f"Warning: frontend sync failed: {exc}", file=sys.stderr)
    if show_ui:
        show_skill_report(run_dir, skill_id, save_md=False, interactive=False, sync_frontend=False)
    return output_path


def show_skill_report(
    run_dir: Path,
    skill_id: str,
    *,
    save_md: bool = True,
    interactive: bool = False,
    sync_frontend: bool = True,
) -> int:
    """Render a skill report to the terminal; refreshes markdown reports by default."""
    skill_id = skill_id.upper()
    skill_dir = run_dir / skill_id
    json_path = find_skill_json(skill_dir)

    if json_path is None:
        print(f"No output found for {skill_id} in {run_dir.name}", file=sys.stderr)
        print(f"Expected JSON under: {skill_dir}/", file=sys.stderr)
        return 1

    if save_md:
        export_markdown_reports(run_dir, skill_dir)

    task_id, payload = load_skill_payload(skill_dir)
    if sync_frontend:
        try:
            from runtime.frontend_sync import publish_skill_run

            publish_skill_run(run_dir.name, task_id or skill_id, payload)
        except Exception as exc:
            print(f"Warning: frontend sync failed: {exc}", file=sys.stderr)
    print(render_terminal_ui(run_dir.name, task_id or skill_id, payload, run_dir=run_dir))

    if not interactive:
        return 0

    return _interactive_menu(run_dir, skill_id)


def _interactive_menu(run_dir: Path, skill_id: str) -> int:
    from runtime.report_cli import interactive_loop, list_skills

    print("\n" + "─" * 62)
    print("  [Enter] menu   [r] refresh   [b] browse runs   [q] quit")
    while True:
        try:
            raw = input("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            return 0

        if raw in {"q", "quit", "exit"}:
            print("Bye.")
            return 0
        if raw in {"r", "refresh"}:
            return show_skill_report(run_dir, skill_id, interactive=True)
        if raw in {"b", "browse"}:
            return interactive_loop(GENERATED_ROOT)
        if raw in {"", "m", "menu"}:
            while True:
                print("\n── What next? ──")
                print("  1. View this report again")
                print("  2. Browse all skills in this run")
                print("  3. Open full run browser")
                print("  4. Quit")
                try:
                    choice = input("Choice [1-4]: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nBye.")
                    return 0
                if choice in {"1", "r"}:
                    show_skill_report(run_dir, skill_id, interactive=False)
                elif choice == "2":
                    skills = list_skills(run_dir)
                    for index, (sid, jp) in enumerate(skills, start=1):
                        marker = "✓" if jp else "·"
                        print(f"  {index}. [{marker}] {sid}")
                    pick = input("Skill number (blank=back): ").strip()
                    if pick.isdigit() and 1 <= int(pick) <= len(skills):
                        show_skill_report(run_dir, skills[int(pick) - 1][0], interactive=False)
                elif choice == "3":
                    return interactive_loop(GENERATED_ROOT)
                elif choice in {"4", "q", ""}:
                    break
            continue
        print("  Unknown command. Try Enter, r, b, q.")


def finish_skill(run_id: str, skill_id: str, *, generated_root: Path | None = None) -> int:
    """Display the report for a completed skill run (terminal only)."""
    root = generated_root or GENERATED_ROOT
    run_dir = root / run_id
    if not run_dir.is_dir():
        print(f"Run directory not found: {run_dir}", file=sys.stderr)
        return 1
    return show_skill_report(run_dir, skill_id.upper())


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Write and/or display Repo-Analyser skill reports")
    sub = parser.add_subparsers(dest="command")

    show_p = sub.add_parser("show", help="Display an existing skill output (default command)")
    show_p.add_argument("--run-id", required=True, help="Run directory name, e.g. repo-analyser")
    show_p.add_argument("--skill", required=True, help="Skill ID, e.g. B1")
    show_p.add_argument("--no-md", action="store_true", help="Skip writing output.md files")
    show_p.add_argument("--interactive", action="store_true", help="Enter interactive menu after display")

    write_p = sub.add_parser("write", help="Write output.json, output.md, and auto-open the terminal UI")
    write_p.add_argument("--run-id", required=True)
    write_p.add_argument("--skill", required=True)
    write_p.add_argument("--payload-file", required=True, help="Path to JSON payload file")
    write_p.add_argument("--no-md", action="store_true", help="Skip writing output.md files")
    write_p.add_argument("--no-ui", action="store_true", help="Skip terminal UI")

    # Back-compat: `python -m runtime.skill_finish --run-id X --skill Y`
    parser.add_argument("--run-id", help=argparse.SUPPRESS)
    parser.add_argument("--skill", help=argparse.SUPPRESS)
    parser.add_argument("--no-md", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--interactive", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--payload-file", help=argparse.SUPPRESS)

    args = parser.parse_args(argv)
    no_md = getattr(args, "no_md", False)

    if args.command == "write" or args.payload_file:
        payload_path = Path(args.payload_file)
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        write_skill_output(
            args.run_id,
            args.skill,
            payload,
            save_md=not no_md,
            show_ui=not getattr(args, "no_ui", False),
        )
        return 0

    run_id = args.run_id
    skill = args.skill
    if not run_id or not skill:
        parser.error("Provide --run-id and --skill (or use the write subcommand)")

    run_dir = GENERATED_ROOT / run_id
    return show_skill_report(
        run_dir,
        skill.upper(),
        save_md=not no_md,
        interactive=args.interactive,
    )


if __name__ == "__main__":
    raise SystemExit(main())
