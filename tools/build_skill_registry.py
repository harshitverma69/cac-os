#!/usr/bin/env python3
"""Compile agent Markdown specs into Cursor-readable skill registry files."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
AGENT_SCAN_DIRS = ("agents", "agents_md")
LEVEL_LABELS = {
    "B": "BASIC",
    "I": "INTERMEDIATE",
    "A": "ADVANCED",
    "D": "INFRA",
}
SECTION_HEADING = re.compile(r"^### (.+)$")
AGENT_TITLE = re.compile(r"^## Agent:\s*(.+?)\s*\(([A-Z]\d+)\)\s*$")
BACKTICK_VALUE = re.compile(r"`([^`]+)`")
OUTPUT_FILE = re.compile(
    r"Output file:\s*`[^`]*/\{run_id\}/[^/]+/([^`]+)`",
    re.IGNORECASE,
)


def discover_agent_specs() -> list[Path]:
    specs: list[Path] = []
    seen: set[str] = set()

    for scan_dir in AGENT_SCAN_DIRS:
        base = ROOT / scan_dir
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*_agent.md")):
            rel = path.relative_to(ROOT).as_posix()
            if rel in seen:
                continue
            seen.add(rel)
            specs.append(path)

    return specs


def split_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current: str | None = None
    lines: list[str] = []

    for line in text.splitlines():
        match = SECTION_HEADING.match(line)
        if match:
            if current is not None:
                sections[current] = "\n".join(lines).strip()
            current = match.group(1).strip()
            lines = []
            continue
        if current is not None:
            lines.append(line)

    if current is not None:
        sections[current] = "\n".join(lines).strip()

    return sections


def parse_task_id(sections: dict[str, str], fallback: str) -> str:
    body = sections.get("Task ID", "")
    match = BACKTICK_VALUE.search(body)
    if match:
        return match.group(1).strip()
    return fallback


def parse_capability_level(sections: dict[str, str], task_id: str) -> str:
    body = sections.get("Capability Level", "")
    match = BACKTICK_VALUE.search(body)
    if match:
        return match.group(1).strip().upper()
    return task_id[0].upper()


def parse_objective(sections: dict[str, str]) -> str:
    return sections.get("Objective", "").replace("\n", " ").strip()


def parse_inputs(sections: dict[str, str]) -> list[str]:
    body = sections.get("Inputs", "")
    inputs: list[str] = []

    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        item = line[1:].strip()
        item = item.split("(", 1)[0].strip()
        if item:
            inputs.append(item)

    return inputs


def parse_outputs(sections: dict[str, str]) -> list[str]:
    body = sections.get("Outputs (STRICT JSON)", sections.get("Outputs", ""))
    match = OUTPUT_FILE.search(body)
    if match:
        return [match.group(1).strip()]

    for line in body.splitlines():
        if line.strip().startswith("Output file:"):
            tick = BACKTICK_VALUE.search(line)
            if tick:
                filename = tick.group(1).split("/")[-1].strip()
                if filename:
                    return [filename]

    return []


def display_name(full_name: str) -> str:
    name = full_name.strip()
    if name.endswith(" Agent"):
        name = name[: -len(" Agent")]
    return name


def parse_agent_spec(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    sections = split_sections(text)

    title_match = AGENT_TITLE.match(text.splitlines()[0].strip()) if text else None
    fallback_id = path.name.split("_", 1)[0].upper()
    task_id = parse_task_id(sections, fallback_id)
    level_code = parse_capability_level(sections, task_id)
    full_name = title_match.group(1).strip() if title_match else path.stem

    return {
        "skill_id": task_id,
        "name": full_name,
        "display_name": display_name(full_name),
        "level": LEVEL_LABELS.get(level_code, level_code),
        "level_code": level_code,
        "input": parse_inputs(sections),
        "output": parse_outputs(sections),
        "description": parse_objective(sections),
        "source": path.relative_to(ROOT).as_posix(),
    }


def sort_key(skill: dict) -> tuple[str, int]:
    skill_id = skill["skill_id"]
    return (skill_id[0], int(skill_id[1:]))


def build_registry(skills: list[dict]) -> dict:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "tools/build_skill_registry.py",
        "scan_roots": [d for d in AGENT_SCAN_DIRS if (ROOT / d).is_dir()],
        "skill_count": len(skills),
        "skills": skills,
    }


def render_markdown(skills: list[dict]) -> str:
    grouped: dict[str, list[dict]] = {}
    for skill in skills:
        grouped.setdefault(skill["level"], []).append(skill)

    lines = [
        "# CAC-OS Skill Registry",
        "",
        "> Cursor capability menu compiled from agent specs. Regenerate with "
        "`python tools/build_skill_registry.py`.",
        "",
    ]

    section_titles = {
        "BASIC": "BASIC SKILLS",
        "INTERMEDIATE": "INTERMEDIATE SKILLS",
        "ADVANCED": "ADVANCED SKILLS",
        "INFRA": "INFRA SKILLS",
    }

    for level in ("BASIC", "INTERMEDIATE", "ADVANCED", "INFRA"):
        entries = grouped.get(level, [])
        if not entries:
            continue
        lines.append(f"## {section_titles[level]}")
        lines.append("")
        for skill in entries:
            lines.append(f"- {skill['skill_id']} → {skill['display_name']}")
        lines.append("")

    lines.extend(
        [
            "## Source",
            "",
            "Each skill maps to one agent spec under `agents/` (legacy alias: `agents_md/`).",
            "Open the `source` path from `skill_registry.json` for inputs, rules, and output contracts.",
            "",
        ]
    )

    return "\n".join(lines)


def write_outputs(registry: dict, markdown: str) -> tuple[Path, Path]:
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    json_path = SKILLS_DIR / "skill_registry.json"
    md_path = SKILLS_DIR / "skill_registry.md"

    json_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(markdown, encoding="utf-8")

    return json_path, md_path


def main() -> int:
    specs = discover_agent_specs()
    if not specs:
        print("No agent specs found under agents/ or agents_md/", file=sys.stderr)
        return 1

    skills = sorted((parse_agent_spec(path) for path in specs), key=sort_key)
    registry = build_registry(skills)
    markdown = render_markdown(skills)
    json_path, md_path = write_outputs(registry, markdown)

    print(f"OK: compiled {len(skills)} skills")
    print(f"  - {json_path.relative_to(ROOT)}")
    print(f"  - {md_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
