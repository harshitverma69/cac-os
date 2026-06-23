"""Deterministic Markdown parsers for agent specs and skill definitions."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

from runtime.deterministic import VOLATILE_OUTPUT_KEYS

SECTION_HEADING = re.compile(r"^### (.+)$")
SKILL_TITLE = re.compile(r"^## Skill:\s*(.+)$")
AGENT_TITLE = re.compile(r"^#{1,2} Agent:\s*(.+?)\s*\(([A-Z]\d+)\)\s*$")
BACKTICK_VALUE = re.compile(r"`([^`]+)`")
JSON_FENCE = re.compile(r"```json\s*\n(.*?)\n```", re.DOTALL)
OUTPUT_FILE = re.compile(
    r"Output file:\s*`[^`]*/\{run_id\}/[^/]+/([^`]+)`",
    re.IGNORECASE,
)

LEVEL_LABELS = {
    "B": "BASIC",
    "I": "INTERMEDIATE",
    "A": "ADVANCED",
    "D": "INFRA",
}

LEVEL_SKILL_DIRS = {
    "B": "basics",
    "I": "intermediate",
    "A": "advanced",
    "D": "infra",
}

LEVEL_ORDER = {"B": 0, "I": 1, "A": 2, "D": 3}


def task_sort_key(task_id: str) -> tuple[int, int]:
    return (LEVEL_ORDER.get(task_id[0], 9), int(task_id[1:]))


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


def parse_bullet_list(body: str) -> list[str]:
    items: list[str] = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("-"):
            continue
        item = line[1:].strip()
        if item.lower() in {"none", "—", "-"}:
            continue
        items.append(item)
    return items


def parse_task_id(sections: dict[str, str], fallback: str) -> str:
    body = sections.get("Task ID", "")
    match = BACKTICK_VALUE.search(body)
    if match:
        return match.group(1).strip().upper()
    stripped = body.strip().upper()
    if re.fullmatch(r"[BIAD]\d+", stripped):
        return stripped
    return fallback.upper()


def parse_depends_on(sections: dict[str, str]) -> list[str]:
    body = sections.get("Depends On", "")
    deps: list[str] = []
    for line in body.splitlines():
        line = line.strip()
        if not line or line.lower() == "none":
            continue
        if line.startswith("-"):
            token = line[1:].strip()
        else:
            token = line
        for part in re.split(r"[,\s]+", token):
            part = part.strip().upper()
            if re.fullmatch(r"[BIAD]\d+", part):
                deps.append(part)
    return sorted(set(deps))


def extract_json_block(sections: dict[str, str], *keys: str) -> dict | None:
    for key in keys:
        body = sections.get(key, "")
        match = JSON_FENCE.search(body)
        if match:
            try:
                return cast(dict[str, Any], json.loads(match.group(1)))
            except json.JSONDecodeError:
                return None
    return None


def parse_numbered_steps(body: str) -> list[str]:
    steps: list[str] = []
    for line in body.splitlines():
        line = line.strip()
        match = re.match(r"^\d+\.\s+(.*)$", line)
        if match:
            steps.append(match.group(1).strip())
    return steps


@dataclass
class SkillDefinition:
    skill_id: str
    name: str
    level: str
    level_code: str
    depends_on: list[str] = field(default_factory=list)
    input_contract: dict = field(default_factory=dict)
    output_contract: dict = field(default_factory=dict)
    execution_steps: list[str] = field(default_factory=list)
    validation_rules: list[str] = field(default_factory=list)
    failure_conditions: list[str] = field(default_factory=list)
    source_path: str = ""
    agent_source: str = ""
    blueprint_source: str = ""
    canonical_output_file: str = "output.json"
    description: str = ""

    @property
    def output_keys(self) -> set[str]:
        if isinstance(self.output_contract, dict):
            return set(self.output_contract.keys())
        return set()


def parse_skill_markdown(path: Path, root: Path | None = None) -> SkillDefinition:
    text = path.read_text(encoding="utf-8")
    sections = split_sections(text)
    lines = text.splitlines()
    title_match = SKILL_TITLE.match(lines[0].strip()) if lines else None

    fallback_id = path.stem.split("_", 1)[0].upper()
    skill_id = parse_task_id(sections, fallback_id)
    level_code = skill_id[0]
    name = title_match.group(1).strip() if title_match else path.stem

    input_contract = extract_json_block(sections, "Input Contract") or {}
    output_contract = extract_json_block(sections, "Output Contract (STRICT JSON)", "Output Contract") or {}

    return SkillDefinition(
        skill_id=skill_id,
        name=name,
        level=LEVEL_LABELS.get(level_code, level_code),
        level_code=level_code,
        depends_on=parse_depends_on(sections),
        input_contract=input_contract,
        output_contract=output_contract,
        execution_steps=parse_bullet_list(sections.get("Execution Steps (DETERMINISTIC ONLY)", "")),
        validation_rules=parse_bullet_list(sections.get("Validation Rules", "")),
        failure_conditions=parse_bullet_list(sections.get("Failure Conditions", "")),
        source_path=path.relative_to(root).as_posix() if root else str(path),
        description=sections.get("Objective", "").replace("\n", " ").strip(),
    )


def parse_agent_markdown(path: Path) -> dict:
    text = strip_frontmatter(path.read_text(encoding="utf-8"))
    sections = split_sections(text)
    title_match = parse_agent_title(text)

    fallback_id = path.name.split("_", 1)[0].upper()
    skill_id = parse_task_id(sections, fallback_id)
    level_code = parse_capability_level(sections, skill_id)
    full_name = title_match.group(1).strip() if title_match else path.stem

    output_body = sections.get("Outputs (STRICT JSON)", sections.get("Outputs", ""))
    output_match = OUTPUT_FILE.search(output_body)
    canonical_output = output_match.group(1) if output_match else "output.json"
    output_contract = extract_json_block(sections, "Outputs (STRICT JSON)", "Outputs") or {}
    if not output_contract:
        json_match = JSON_FENCE.search(text)
        if json_match:
            try:
                output_contract = json.loads(json_match.group(1))
            except json.JSONDecodeError:
                output_contract = {}

    inputs = []
    for item in parse_bullet_list(sections.get("Inputs", "")):
        key = item.split("(", 1)[0].split("{", 1)[0].strip()
        if key:
            inputs.append(key)

    input_contract = {key: "required" for key in inputs}

    return {
        "skill_id": skill_id,
        "name": full_name,
        "level_code": level_code,
        "level": LEVEL_LABELS.get(level_code, level_code),
        "depends_on": parse_depends_on(sections),
        "description": sections.get("Objective", "").replace("\n", " ").strip(),
        "input_contract": input_contract,
        "output_contract": output_contract,
        "validation_rules": parse_bullet_list(sections.get("Validation", "")),
        "failure_conditions": parse_bullet_list(sections.get("Failure Conditions", "")),
        "canonical_output_file": canonical_output,
        "agent_source": path.as_posix(),
    }


def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :].lstrip("\n")
    return text


def parse_agent_title(text: str) -> re.Match[str] | None:
    for line in text.splitlines():
        match = AGENT_TITLE.match(line.strip())
        if match:
            return match
    return None


def parse_capability_level(sections: dict[str, str], task_id: str) -> str:
    body = sections.get("Capability Level", "")
    match = BACKTICK_VALUE.search(body)
    if match:
        return match.group(1).strip().upper()
    return task_id[0].upper()


def validate_output_schema(output: dict, contract: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(contract, dict):
        return errors

    for key in contract:
        if key in VOLATILE_OUTPUT_KEYS:
            continue
        if key not in output:
            errors.append(f"MISSING_OUTPUT_KEY: {key}")

    expected_task_id = contract.get("task_id")
    if expected_task_id and output.get("task_id") != expected_task_id:
        errors.append(f"TASK_ID_MISMATCH: expected {expected_task_id}, got {output.get('task_id')}")

    return errors
