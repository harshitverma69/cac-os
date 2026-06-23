"""Build skill definitions and core/skill_registry.json from agent specs."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, cast

from runtime.deterministic import DETERMINISTIC_STAMP, canonical_json_dumps
from runtime.skill_constants import cursor_slash_command
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
EXPECTED_SKILL_COUNT = 24
EXPECTED_SKILL_IDS = [f"{level}{index}" for level in "BIAD" for index in range(1, 7)]


def validate_skill_coverage(registry: dict, skills_root: Path = SKILLS_ROOT) -> dict:
    skills = registry.get("skills", {})
    missing: list[str] = []
    duplicates: list[str] = []
    missing_files: list[str] = []
    missing_contracts: list[str] = []

    seen: set[str] = set()
    for skill_id in sorted(skills.keys(), key=task_sort_key):
        if skill_id in seen:  # pragma: no cover - dict keys are unique
            duplicates.append(skill_id)
        seen.add(skill_id)

    for skill_id in EXPECTED_SKILL_IDS:
        if skill_id not in skills:
            missing.append(skill_id)
            continue

        meta = skills[skill_id]
        skill_path = ROOT / meta["path"]
        if not skill_path.is_file():
            missing_files.append(meta["path"])

        if not meta.get("output_file"):
            missing_contracts.append(skill_id)

    for skill_id in sorted(set(skills.keys()) - set(EXPECTED_SKILL_IDS), key=task_sort_key):
        if skill_id not in duplicates:
            duplicates.append(skill_id)

    total = len([skill_id for skill_id in EXPECTED_SKILL_IDS if skill_id in skills])
    coverage_ok = (
        total == EXPECTED_SKILL_COUNT and not missing and not duplicates and not missing_files and not missing_contracts
    )

    return {
        "total_skills": total,
        "missing": missing,
        "duplicates": sorted(set(duplicates), key=task_sort_key),
        "missing_files": missing_files,
        "missing_output_contracts": missing_contracts,
        "coverage_status": "100%" if coverage_ok else "INCOMPLETE",
    }


def load_task_registry() -> dict[str, Any]:
    with TASK_REGISTRY_PATH.open(encoding="utf-8") as handle:
        return cast(dict[str, Any], json.load(handle))


def agent_spec_path(task_id: str, meta: dict[str, Any]) -> Path:
    folder = str(meta["folder"])
    slug = str(meta["slug"])
    for scan_dir in AGENT_DIRS:
        candidate = ROOT / scan_dir / folder / f"{task_id}_{slug}_agent.md"
        if candidate.is_file():
            return candidate
    return ROOT / "agents" / folder / f"{task_id}_{slug}_agent.md"


def blueprint_path(task_id: str, meta: dict[str, Any]) -> Path:
    level = str(meta["level"])
    return ROOT / "eval_blueprints" / level / f"{task_id}_blueprint.md"


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
        f"Write JSON + output.md via `python3 -m runtime.skill_finish write --run-id {{run_id}} --skill {agent['skill_id']} --payload-file <payload.json>` (auto-opens CLI UI)",
        "Validate output against Output Contract",
    ]
    steps_block = "\n".join(f"- {step}" for step in steps)
    validation_block = "\n".join(f"- {rule}" for rule in validation)
    failure_block = "\n".join(f"- {item}" for item in failure)

    return f"""## Skill: {agent["name"]}

### Task ID
`{agent["skill_id"]}`

### Level
`{agent["level"]}`

### Objective
{agent["description"]}

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
- Agent: `{agent["agent_source"]}`
- Blueprint: `eval_blueprints/{meta["level"]}/{agent["skill_id"]}_blueprint.md`
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
        "generated_at": DETERMINISTIC_STAMP,
        "generator": "runtime/skill_registry_builder.py",
        "eval_source": registry_data.get("eval_source"),
        "skill_count": len(skills),
        "skills": skills,
        "coverage": validate_skill_coverage({"skills": skills}, SKILLS_ROOT),
    }


def write_registry(registry: dict) -> Path:
    CORE_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    CORE_REGISTRY_PATH.write_text(canonical_json_dumps(registry), encoding="utf-8")
    return CORE_REGISTRY_PATH


def render_how_to_run(registry: dict) -> str:
    lines = [
        "# Repo-Analyser — How to Run",
        "",
        "> Single guide for setup, commands, and all 24 skills. Regenerate with `make build-skills`.",
        "",
        "## What is Repo-Analyser?",
        "",
        "Repo-Analyser is a **deterministic Markdown execution framework** — not a runtime AI system.",
        "Agent specs define inputs, outputs, and rules. Cursor (or you) execute them and write JSON.",
        "",
        "**Total skills:** 24 (B1–B6, I1–I6, A1–A6, D1–D6)",
        "",
        "---",
        "",
        "## 1. Prerequisites",
        "",
        "- Python 3.10+",
        "- No external AI services required for validation/runtime",
        "",
        "Optional for tests:",
        "",
        "```bash",
        "python3 -m venv .venv && source .venv/bin/activate",
        "pip install pytest pytest-cov",
        "```",
        "",
        "---",
        "",
        "## 2. First-time setup",
        "",
        "See **[docs/SETUP.md](SETUP.md)** for the full guide (frontend auto-open, troubleshooting).",
        "",
        "```bash",
        "git clone https://github.com/harshitverma69/Repo-Analyser.git",
        "cd Repo-Analyser",
        "make build-skills",
        "make install-cursor-skills   # 24 /repo-analyser-* skills → ~/.cursor/skills/",
        "make build-frontend",
        "```",
        "",
        "Or: `make setup` (runs all three plus `make validate`).",
        "",
        "**Restart Cursor completely** after `install-cursor-skills` so slash commands appear.",
        "",
        "When any skill finishes, the **browser opens automatically** to the Live runs tab",
        "(port 8765). `make serve-frontend` is optional — use it to keep the UI open beforehand.",
        "",
        "---",
        "",
        "## 3. Common commands",
        "",
        "| Command | Purpose |",
        "|---------|---------|",
        "| `make build-skills` | Regenerate skill files and registry |",
        "| `make expand-agent-specs` | Expand all 24 agent specs to procedural detail |",
        "| `make install-cursor-skills` | Install skills into Cursor `/` menu |",
        "| `make build-frontend` | Generate local browser guide (`frontend/data/skills.json`) |",
        "| `make serve-frontend` | Open local UI at http://127.0.0.1:8765 |",
        "| `make validate` | Validate all agent specs and DAG |",
        "| `make validate-dag` | Validate skill dependency graph |",
        "| `make run-skill SKILL=B1 RUN_ID=my-run` | Run one skill |",
        "| `make run-pipeline RUN_ID=my-run` | Run all 24 skills in DAG order |",
        "| `make validate-pipeline RUN_ID=my-run` | Validate a pipeline run |",
        "| `make harden` | Full production check (tests + determinism) |",
        "| `make test` | Run test suite |",
        "",
        "### Run one skill in Cursor",
        "",
        "1. Type `/repo-analyser-repo-inventory` (or any skill below) in chat",
        "2. Follow the agent spec and skill spec",
        "3. Write output, **output.md**, and auto-open CLI UI:",
        "",
        "```bash",
        "python3 -m runtime.skill_finish write --run-id <run_id> --skill B1 --payload-file payload.json",
        "```",
        "",
        "This also **auto-opens the browser** (Live runs tab) and prints the terminal CLI report.",
        "",
        "Or if `output.json` already exists: `python3 -m runtime.skill_finish --run-id <run_id> --skill B1`",
        "",
        "### Run via deterministic runtime",
        "",
        "```bash",
        "make run-skill SKILL=B2 RUN_ID=demo",
        "make run-pipeline RUN_ID=full-run",
        "python -m runtime.validate_pipeline --run-id full-run",
        "```",
        "",
        "---",
        "",
        "## 4. Repository layout",
        "",
        "| Path | Role |",
        "|------|------|",
        "| `agents/` | Source agent specs (inputs, outputs, rules) |",
        "| `skills/` | Compiled skill specs (`.skill.md`) for execution |",
        "| `core/skill_registry.json` | Machine-readable index of all 24 skills |",
        "| `eval_blueprints/` | Step-by-step eval runbooks |",
        "| `runtime/` | Deterministic orchestrator, runner, validator |",
        "| `generated_projects/_golden/` | Reference JSON outputs |",
        "| `generated_projects/{run_id}/` | Your run outputs |",
        "| `frontend/` | Local browser guide for all 24 agents |",
        "| `tools/install_cursor_skills.py` | Installs Cursor `/repo-analyser-*` skills |",
        "",
        "---",
        "",
        "## 5. All 24 skills",
        "",
    ]

    by_level = {
        "BASIC": "Basic (B1–B6) — Repo reading and greenfield builds",
        "INTERMEDIATE": "Intermediate (I1–I6) — Repo operations and polyglot work",
        "ADVANCED": "Advanced (A1–A6) — Parallel work and system building",
        "INFRA": "Infra (D1–D6) — DevOps and infrastructure",
    }

    grouped: dict[str, list[tuple[str, dict]]] = {
        "BASIC": [],
        "INTERMEDIATE": [],
        "ADVANCED": [],
        "INFRA": [],
    }
    for skill_id, meta in registry["skills"].items():
        grouped[meta["level"]].append((skill_id, meta))

    for level in ("BASIC", "INTERMEDIATE", "ADVANCED", "INFRA"):
        entries = sorted(grouped[level], key=lambda item: task_sort_key(item[0]))
        if not entries:
            continue
        lines.append(f"### {by_level[level]}")
        lines.append("")
        for skill_id, meta in entries:
            deps = ", ".join(meta["depends_on"]) if meta["depends_on"] else "none"
            lines.extend(
                [
                    f"#### {skill_id} — {meta['name']}",
                    "",
                    f"**Role:** {meta['description']}",
                    "",
                    f"**Depends on:** {deps}",
                    "",
                    "| Item | Location |",
                    "|------|----------|",
                    f"| Cursor command | `{cursor_slash_command(skill_id)}` |",
                    f"| Agent spec | `{meta['agent_source']}` |",
                    f"| Skill spec | `{meta['path']}` |",
                    f"| Eval blueprint | `{meta['blueprint']}` |",
                    f"| Output JSON | `generated_projects/{{run_id}}/{skill_id}/output.json` |",
                    f"| Golden reference | `generated_projects/_golden/{skill_id}/{meta['output_file']}` |",
                    "",
                ]
            )

    lines.extend(
        [
            "### Master pipeline",
            "",
            "**Role:** Run all 24 skills in DAG order with deterministic outputs.",
            "",
            "| Item | Location |",
            "|------|----------|",
            "| Skill spec | `skills/run_all_skills.skill.md` |",
            "| Run command | `make run-pipeline RUN_ID=my-run` |",
            "",
            "---",
            "",
            "## 6. System rules",
            "",
            "- No runtime AI agents inside Repo-Analyser itself",
            "- No inference or probabilistic logic in the runtime",
            "- Markdown specs are the program; JSON is the output",
            "- Execution order follows the DAG in `execution_models/dependency_graph.md`",
            "",
        ]
    )

    return "\n".join(lines)


def write_how_to_run(registry: dict) -> Path:
    doc_path = ROOT / "docs" / "HOW_TO_RUN.md"
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(render_how_to_run(registry) + "\n", encoding="utf-8")
    return doc_path


def main() -> int:
    registry = build_skill_registry(write_skills=True)
    path = write_registry(registry)
    doc_path = write_how_to_run(registry)
    coverage = registry["coverage"]
    print(f"OK: built {registry['skill_count']} skills")
    print(f"  - {path.relative_to(ROOT)}")
    print(f"  - {doc_path.relative_to(ROOT)}")
    print(f"  - coverage: {coverage['coverage_status']} ({coverage['total_skills']}/{EXPECTED_SKILL_COUNT})")
    for level_dir in sorted(LEVEL_SKILL_DIRS.values()):
        count = len(list((SKILLS_ROOT / level_dir).glob("*.skill.md")))
        if count:
            print(f"  - skills/{level_dir}/ ({count} skills)")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
