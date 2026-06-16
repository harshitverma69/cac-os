"""Post-skill hook: export Markdown and open the report UI."""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path

from runtime.report_renderer import (
    SKILL_TITLES,
    export_run_markdown,
    export_skill_markdown,
    find_skill_json,
    load_skill_payload,
    render_report,
)

ROOT = Path(__file__).resolve().parent.parent
GENERATED_ROOT = ROOT / "generated_projects"


def _banner(run_id: str, skill_id: str, title: str) -> str:
    line = "═" * 62
    return (
        f"\n╔{line}╗\n"
        f"║  CAC-OS Report — {skill_id} {title:<38}║\n"
        f"║  Run: {run_id:<53}║\n"
        f"╚{line}╝\n"
    )


def _open_in_editor(path: Path) -> None:
    if not path.is_file():
        return
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Windows":
            subprocess.Popen(["start", "", str(path)], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.Popen(["xdg-open", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        pass


def show_skill_report(
    run_dir: Path,
    skill_id: str,
    *,
    open_editor: bool = True,
    interactive: bool = True,
) -> int:
    """Display the skill report and optionally enter a mini UI loop."""
    skill_id = skill_id.upper()
    skill_dir = run_dir / skill_id
    json_path = find_skill_json(skill_dir)

    if json_path is None:
        print(f"No output found for {skill_id} in {run_dir.name}", file=sys.stderr)
        print(f"Expected JSON under: {skill_dir}/", file=sys.stderr)
        return 1

    try:
        export_skill_markdown(skill_dir)
        export_run_markdown(run_dir)
    except Exception as exc:
        print(f"Warning: markdown export failed: {exc}", file=sys.stderr)

    task_id, payload = load_skill_payload(skill_dir)
    title = SKILL_TITLES.get(skill_id, skill_id)
    md_path = skill_dir / "output.md"
    index_path = run_dir / "REPORT.md"

    print(_banner(run_dir.name, skill_id, title[:38]))
    print(render_report(payload, task_id=task_id or skill_id))

    if open_editor and md_path.is_file():
        _open_in_editor(md_path)
        print(f"\n[opened] {md_path}")

    if not interactive:
        return 0

    print("\n" + "─" * 62)
    print("  [Enter] menu   [o] open report   [i] open index   [q] quit")
    while True:
        try:
            raw = input("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            return 0

        if raw in {"", "m", "menu"}:
            return _mini_menu(run_dir, skill_id, md_path, index_path)
        if raw in {"q", "quit", "exit"}:
            print("Bye.")
            return 0
        if raw in {"o", "open"}:
            _open_in_editor(md_path)
            print(f"[opened] {md_path}")
            continue
        if raw in {"i", "index"}:
            _open_in_editor(index_path)
            print(f"[opened] {index_path}")
            continue
        if raw in {"r", "refresh"}:
            return show_skill_report(run_dir, skill_id, open_editor=False, interactive=True)
        print("  Unknown command. Try Enter, o, i, q.")


def _mini_menu(run_dir: Path, skill_id: str, md_path: Path, index_path: Path) -> int:
    from runtime.report_cli import interactive_loop, list_skills, view_skill

    while True:
        print("\n── Skill done — what next? ──")
        print("  1. View this report again")
        print("  2. Browse all skills in this run")
        print("  3. Open output.md in editor")
        print("  4. Open full run browser")
        print("  5. Quit")
        try:
            raw = input("Choice [1-5]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            return 0

        if raw in {"1", "r"}:
            view_skill(run_dir, skill_id, write_md=False)
        elif raw == "2":
            skills = list_skills(run_dir)
            for index, (sid, jp) in enumerate(skills, start=1):
                marker = "✓" if jp else "·"
                print(f"  {index}. [{marker}] {sid}")
            pick = input("Skill number (blank=back): ").strip()
            if pick.isdigit() and 1 <= int(pick) <= len(skills):
                view_skill(run_dir, skills[int(pick) - 1][0], write_md=False)
        elif raw == "3":
            _open_in_editor(md_path)
            print(f"[opened] {md_path}")
        elif raw == "4":
            return interactive_loop(GENERATED_ROOT)
        elif raw in {"5", "q", ""}:
            print("Bye.")
            return 0


def finish_skill(run_id: str, skill_id: str, *, generated_root: Path | None = None) -> int:
    """Export reports and open the UI for a completed skill run."""
    root = generated_root or GENERATED_ROOT
    run_dir = root / run_id
    if not run_dir.is_dir():
        print(f"Run directory not found: {run_dir}", file=sys.stderr)
        return 1
    return show_skill_report(run_dir, skill_id.upper(), open_editor=True, interactive=True)


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Open CAC-OS report UI after a skill completes")
    parser.add_argument("--run-id", required=True, help="Run directory name, e.g. master-mapping")
    parser.add_argument("--skill", required=True, help="Skill ID, e.g. B1")
    parser.add_argument("--no-open", action="store_true", help="Do not open output.md in the editor")
    parser.add_argument("--no-interactive", action="store_true", help="Print report and exit")
    args = parser.parse_args(argv)

    run_dir = GENERATED_ROOT / args.run_id
    return show_skill_report(
        run_dir,
        args.skill.upper(),
        open_editor=not args.no_open,
        interactive=not args.no_interactive,
    )


if __name__ == "__main__":
    raise SystemExit(main())
