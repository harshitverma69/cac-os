"""Build skill definitions and core/skill_registry.json from agent specs."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from runtime.skill_parser import (
    LEVEL_SKILL_DIRS,
    parse_agent_markdown,
    parse_numbered_steps,
    split_sections,
    task_sort_key,
)

ROOT = Path(__file__).resolve().parent.parent
TASK_REGISTRY_PATH = ROOT / "scripts" / "task_registry.json"
SKILLS_ROOT = ROOT / "skills"
CORE_REGISTRY_PATH = ROOT / "core" / "skill_registry.json"
AGENT_DIRS = ("agents", "agents_md")


def load_task_registry() -> dict:
    with TASK_REGISTRY_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def agent_spec_path(task_id: str, meta: dict) -> Path:
    for scan_dir in AGENT_DIRS:
        candidate = ROOT / scan_dir / meta["folder"] / f"{task_id}_{meta['slug']}_agent.md"
        if candidate.is_file():
            return candidate
    return ROOT / "agents" / meta["folder"] / f"{task_id}_{meta['slug']}_agent.md"


def blueprint_path(task_id: str, meta: dict) -> Path:
    return ROOT / "eval_blueprints" / meta["level"] / f"{task_id}_blueprint.md"


def render_skill_markdown(
    agent: dict,
    meta: dict,
    blueprint_steps: list[str],
    skill_rel_path: str,
) -> str:
    depends = agent["depends_on"]
    depends_block = "\n".join(f"- {dep}" for dep in depends) if depends else "None"

    input_json = json.dumps(agent["input_contract"], indent=2)
    output_json = json.dumps(agent["output_contract"], indent=2)
    validation = agent["validation_rules"] or ["Output matches golden reference schema"]
    failure = agent["failure_conditions"] or ["missing input", "schema mismatch"]

    steps = blueprint_steps or [
        f"Read agent spec: `{agent['agent_source']}`",
        "Apply deterministic rules from `core/execution_rules.md`",
        f"Write structured JSON to `generated_projects/{{run_id}}/{agent['skill_id']}/output.json`",
        "Validate output against Output Contract",
    ]
    steps_block = "\n".join(f"- {step}" for step in steps)
    validation_block = "\n".join(f"- {rule}" for rule in validation)
    failure_block = "\n".join(f"- {item}" for item in failure)

    return f"""## Skill: {agent['name']}

### Task ID
`{agent['skill_id']}`

### Level
`{agent['level']}`

### Objective
{agent['description']}

### Depends On
{depends_block}

### Input Contract
```json
{input_json}
```

### Execution Steps (DETERMINISTIC ONLY)
{steps_block}

### Output Contract (STRICT JSON)
```json
{output_json}
```

### Validation Rules
{validation_block}

### Failure Conditions
{failure_block}

### Sources
- Agent: `{agent['agent_source']}`
- Blueprint: `eval_blueprints/{meta['level']}/{agent['skill_id']}_blueprint.md`
- Skill: `{skill_rel_path}`
"""


def discover_blueprint_steps(path: Path) -> list[str]:
    if not path.is_file():
        return []
    sections = split_sections(path.read_text(encoding="utf-8"))
    return parse_numbered_steps(sections.get("Execution Steps", ""))


def build_skill_registry(write_skills: bool = True) -> dict:
    registry_data = load_task_registry()
    tasks = registry_data["tasks"]
    skills: dict[str, dict] = {}

    for task_id in sorted(tasks.keys(), key=task_sort_key):
        meta = tasks[task_id]
        agent_path = agent_spec_path(task_id, meta)
        if not agent_path.is_file():
            raise FileNotFoundError(f"Missing agent spec: {agent_path}")

        agent = parse_agent_markdown(agent_path)
        agent["agent_source"] = agent_path.relative_to(ROOT).as_posix()
        agent["depends_on"] = meta["depends_on"]
        agent["canonical_output_file"] = meta["output_file"]

        level_dir = LEVEL_SKILL_DIRS[meta["level"]]
        skill_filename = f"{task_id}_{meta['slug']}.skill.md"
        skill_path = SKILLS_ROOT / level_dir / skill_filename
        skill_rel = f"skills/{level_dir}/{skill_filename}"

        bp_path = blueprint_path(task_id, meta)
        steps = discover_blueprint_steps(bp_path)

        if write_skills:
            skill_path.parent.mkdir(parents=True, exist_ok=True)
            skill_path.write_text(
                render_skill_markdown(agent, meta, steps, skill_rel),
                encoding="utf-8",
            )

        skills[task_id] = {
            "path": skill_rel,
            "depends_on": meta["depends_on"],
            "level": agent["level"],
            "level_code": meta["level"],
            "name": agent["name"],
            "description": agent["description"],
            "agent_source": agent["agent_source"],
            "blueprint": bp_path.relative_to(ROOT).as_posix(),
            "output_file": meta["output_file"],
            "canonical_output_file": meta["output_file"],
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "runtime/skill_registry_builder.py",
        "eval_source": registry_data.get("eval_source"),
        "skill_count": len(skills),
        "skills": skills,
    }


def write_registry(registry: dict) -> Path:
    CORE_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    CORE_REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return CORE_REGISTRY_PATH


def render_skill_catalog(registry: dict) -> str:
    lines = [
        "# CAC-OS Skill Catalog",
        "",
        "> What each skill does and where it lives. Regenerate with "
        "`python runtime/skill_registry_builder.py`.",
        "",
        f"Total skills: **{registry['skill_count']}**",
        "",
    ]

    by_level = {
        "BASIC": [],
        "INTERMEDIATE": [],
        "ADVANCED": [],
        "INFRA": [],
    }

    for skill_id, meta in registry["skills"].items():
        by_level[meta["level"]].append((skill_id, meta))

    titles = {
        "BASIC": "Basic Skills (B1–B6)",
        "INTERMEDIATE": "Intermediate Skills (I1–I6)",
        "ADVANCED": "Advanced Skills (A1–A6)",
        "INFRA": "Infra Skills (D1–D6)",
    }

    for level in ("BASIC", "INTERMEDIATE", "ADVANCED", "INFRA"):
        entries = sorted(by_level[level], key=lambda item: task_sort_key(item[0]))
        if not entries:
            continue
        lines.append(f"## {titles[level]}")
        lines.append("")
        lines.append("| ID | Name | Works On | Depends On | Skill File |")
        lines.append("|----|------|----------|------------|------------|")
        for skill_id, meta in entries:
            deps = ", ".join(meta["depends_on"]) if meta["depends_on"] else "—"
            lines.append(
                f"| {skill_id} | {meta['name']} | {meta['description']} | {deps} | `{meta['path']}` |"
            )
        lines.append("")

    lines.extend(
        [
            "## Master Pipeline Skill",
            "",
            "| ID | Name | Works On | Skill File |",
            "|----|------|----------|------------|",
            "| ALL | Full Pipeline | Runs all 24 skills in DAG order with deterministic golden outputs | `skills/run_all_skills.skill.md` |",
            "",
            "## How Skills Execute",
            "",
            "1. `runtime/skill_registry_builder.py` compiles agent specs → `.skill.md` + `core/skill_registry.json`",
            "2. `runtime/skill_orchestrator.py` builds the DAG and execution plan",
            "3. `runtime/skill_runner.py` executes each skill deterministically (golden reference, no LLM)",
            "4. Outputs land in `generated_projects/{run_id}/{skill_id}/output.json`",
            "",
        ]
    )

    return "\n".join(lines)


def write_skill_catalog(registry: dict) -> Path:
    catalog_path = ROOT / "docs" / "SKILL_CATALOG.md"
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_path.write_text(render_skill_catalog(registry) + "\n", encoding="utf-8")
    return catalog_path


def main() -> int:
    registry = build_skill_registry(write_skills=True)
    path = write_registry(registry)
    catalog_path = write_skill_catalog(registry)
    print(f"OK: built {registry['skill_count']} skills")
    print(f"  - {path.relative_to(ROOT)}")
    print(f"  - {catalog_path.relative_to(ROOT)}")
    for level_dir in sorted(LEVEL_SKILL_DIRS.values()):
        count = len(list((SKILLS_ROOT / level_dir).glob("*.skill.md")))
        if count:
            print(f"  - skills/{level_dir}/ ({count} skills)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
