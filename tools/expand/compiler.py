"""Compile expanded agent markdown from registry and phase data."""

from __future__ import annotations

from tools.expand.parser import (
    _blueprint_text,
    _checklist_lines,
    _cursor_name,
    _extract_section_text,
    _golden_schema,
)
from tools.expand.phases_data import INPUT_BULLETS, INPUTS, PHASES
from tools.expand.template_engine import COMMON_RULES, FINAL_STEP, REGISTRY, TASKS


def _display_name(task_id: str, slug: str) -> str:
    parts = slug.split("_")
    if parts and parts[-1] == "agent":
        parts = parts[:-1]
    if parts and parts[0].upper() == task_id:
        parts = parts[1:]
    return " ".join(part.replace("-", " ").title() for part in parts) if parts else slug


def render_agent(task_id: str) -> str:
    meta = REGISTRY["skills"][task_id]
    task_meta = TASKS[task_id]
    blueprint = _blueprint_text(task_id)
    json_schema = _golden_schema(task_id)
    time_budget = _extract_section_text(blueprint, "Time Budget") or "see blueprint"
    validation = _checklist_lines(_extract_section_text(blueprint, "Success Criteria"))
    failure = _checklist_lines(_extract_section_text(blueprint, "Failure Conditions"))
    eval_deliverables = _checklist_lines(_extract_section_text(blueprint, "Deliverables Checklist"))
    depends = meta.get("depends_on") or []
    depends_text = ", ".join(f"`{d}`" for d in depends) if depends else "None"
    level = meta.get("level", task_meta["level"])
    display_name = _display_name(task_id, task_meta["slug"])
    description = meta["description"]
    output_file = task_meta["output_file"]
    slug = task_meta["slug"]

    phases_md = ""
    for title, body in PHASES.get(task_id, []):
        phases_md += f"\n## {title}\n{body.strip()}\n"

    checklist_items = [
        f"`task_id` is `{task_id}` in output JSON",
        f"Output written to `generated_projects/{{run_id}}/{task_id}/output.json`",
        "`generated_at` set (ISO 8601 UTC)",
        "All required proof fields populated with real command results",
        f"python3 -m runtime.skill_finish write --run-id <run_id> --skill {task_id} executed as final step",
    ]
    if task_id == "B1":
        checklist_items.extend(
            [
                "Every artifact has `file_path` evidence",
                "All ten artifact categories present (empty arrays allowed)",
                "Category counts consistent with `artifacts` contents",
                "`dependency_graph_summary` built from imports only",
            ]
        )

    checklist = "\n".join(f"- [ ] {item}" for item in checklist_items)

    input_bullets = "\n".join(f"- {item}" for item in INPUT_BULLETS.get(task_id, []))
    depends_on_section = "\n".join(f"- {d}" for d in depends) if depends else "- None"
    default_inputs_table = (
        "| Field | Required | Description |\n" "|-------|----------|-------------|\n" "| See agent spec | — | — |"
    )
    inputs_section = INPUTS.get(task_id, default_inputs_table)

    return f"""---
name: {_cursor_name(task_id)}
description: |
  Repo-Analyser {task_id} ({level}) — {description}
  Read-only analysis where applicable; strict JSON output to generated_projects.
---

## Agent: {display_name} ({task_id})

You are the **{display_name}** in the Repo-Analyser deterministic eval framework.

**Objective:** {description}

**Capability level:** `{task_meta['level']}` · **Time budget:** {time_budget} · **Depends on:** {depends_text}

Your primary deliverable is **strict JSON** at `generated_projects/{{run_id}}/{task_id}/output.json`. Use `python3 -m runtime.skill_finish write` to write JSON and **auto-open the terminal CLI** — do not write a separate markdown report.

---

## Input

The user or orchestrator provides:

{inputs_section}

If required fields are missing, ask once. Do not proceed without them.

The orchestrator supplies `run_id` for the output folder under `generated_projects/`.

Record analysis start time immediately; set `generated_at` in the output envelope when complete.

---

{phases_md.strip()}

---

## Eval deliverables

{eval_deliverables or "_See phases above._"}

---

## Rules

{COMMON_RULES}

Task-specific rules from the original spec are preserved in **Validation** and **Failure conditions** below.

See output schema in **Registry compatibility** below and `generated_projects/_golden/{task_id}/{output_file}`.

---

## Validation

{validation or "_See eval blueprint._"}

---

## Failure conditions

{failure or "_See eval blueprint._"}

---

## Completion checklist

{checklist}

---

{FINAL_STEP.format(task_id=task_id)}

---

## Registry compatibility (skill_parser / registry builder)

### Task ID
`{task_id}`

### Capability Level
`{task_meta['level']}`

### Time Budget
{time_budget}

### Depends On
{depends_on_section}

### Objective
{description}

### Inputs
{input_bullets}

### Outputs (STRICT JSON)
Output file: `generated_projects/{{run_id}}/{task_id}/{output_file}`

```json
{json_schema}
```

### Eval Deliverables
{eval_deliverables or "- See phases above."}

### Validation
{validation or "- See eval blueprint."}

### Failure Conditions
{failure or "- See eval blueprint."}

---

## References

- Skill spec: `{meta['path']}`
- Eval blueprint: `eval_blueprints/{task_meta['level']}/{task_id}_blueprint.md`
- Execution rules: `core/execution_rules.md`
- Agent spec path: `agents/{task_meta['folder']}/{task_id}_{slug}_agent.md`
"""
