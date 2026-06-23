#!/usr/bin/env python3
"""Install Repo-Analyser skills into Cursor's / slash menu."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from runtime.skill_constants import CURSOR_PREFIX, cursor_skill_name, cursor_slash_command

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "core" / "skill_registry.json"
MANIFEST_PATH = ROOT / "skills" / "cursor_skills_manifest.json"


def load_registries() -> tuple[dict, dict]:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    tasks = json.loads((ROOT / "scripts" / "task_registry.json").read_text(encoding="utf-8"))["tasks"]
    return registry, tasks


def render_cursor_skill(task_id: str, meta: dict, task_meta: dict) -> str:
    name = cursor_skill_name(task_id)
    deps = meta.get("depends_on") or []
    deps_text = ", ".join(deps) if deps else "none"
    level = meta.get("level", task_meta.get("level", ""))
    blueprint = f"eval_blueprints/{task_meta['level']}/{task_id}_blueprint.md"
    agent = meta.get("agent_source", "")
    skill_path = meta.get("path", "")

    description = (
        f"Repo-Analyser {task_id} ({level}) — {meta['description']} "
        f"Use when running eval task {task_id} or `{cursor_slash_command(task_id)}`."
    )

    return f"""---
name: {name}
description: {description}
---

# Repo-Analyser — {meta['name']} ({task_id})

Execute **Repo-Analyser skill {task_id}** deterministically. Follow the Markdown specs — no free-form guessing.

## What this skill does

{meta['description']}

## Depends on

{deps_text}

## Read these files (in order)

1. Agent spec: `{agent}`
2. Skill spec: `{skill_path}`
3. Eval blueprint: `{blueprint}`
4. Full guide: `docs/HOW_TO_RUN.md`

## Output (strict JSON)

**Preferred — write JSON + output.md and auto-open CLI UI in one step:**

```bash
python3 -m runtime.skill_finish write --run-id <run_id> --skill {task_id} --payload-file /path/to/payload.json
```

If the terminal UI does not appear, open `generated_projects/{{run_id}}/{task_id}/output.md`.

**Or** if you already wrote `generated_projects/{{run_id}}/{task_id}/output.json`, display the UI (mandatory final step — do not end turn without this):

```bash
python3 -m runtime.skill_finish --run-id <run_id> --skill {task_id}
```

Golden reference: `generated_projects/_golden/{task_id}/{meta.get('output_file', 'output.json')}`

## FINAL STEP (mandatory — last action, no steps after this)

Run one of the commands above. **Do not skip.** The terminal CLI report must appear before you finish.
"""


def install_skills(target_root: Path, clean: bool = False) -> dict:
    registry, tasks = load_registries()
    skills = registry.get("skills", {})

    if clean and target_root.is_dir():
        for child in target_root.iterdir():
            if child.is_dir() and (
                child.name.startswith(f"{CURSOR_PREFIX}-") or child.name.startswith("cac-os-")  # legacy prefix
            ):
                shutil.rmtree(child)

    installed: list[dict] = []

    for task_id in sorted(skills.keys(), key=lambda tid: (tid[0], int(tid[1:]))):
        meta = skills[task_id]
        task_meta = tasks[task_id]
        name = cursor_skill_name(task_id)
        skill_dir = target_root / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            render_cursor_skill(task_id, meta, task_meta),
            encoding="utf-8",
        )

        installed.append(
            {
                "task_id": task_id,
                "cursor_skill": name,
                "slash_command": cursor_slash_command(task_id),
                "title": meta["name"],
                "description": meta["description"],
                "agent_spec": meta["agent_source"],
                "skill_spec": meta["path"],
                "cursor_path": f"~/.cursor/skills/{name}/SKILL.md",
            }
        )

    manifest = {
        "generator": "tools/install_cursor_skills.py",
        "skill_count": len(installed),
        "install_target": str(target_root),
        "prefix": CURSOR_PREFIX,
        "skills": installed,
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Install Repo-Analyser skills into Cursor / menu")
    parser.add_argument(
        "--project",
        action="store_true",
        help="Install to repo-analyser/.cursor/skills/ instead of ~/.cursor/skills/",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove existing repo-analyser-* (and legacy cac-os-*) skills first",
    )
    args = parser.parse_args()

    target = (ROOT / ".cursor" / "skills") if args.project else (Path.home() / ".cursor" / "skills")
    target.mkdir(parents=True, exist_ok=True)
    manifest = install_skills(target, clean=args.clean)

    print(f"OK: installed {manifest['skill_count']} Cursor skills → {target}")
    print(f"  manifest: {MANIFEST_PATH.relative_to(ROOT)}")
    print("  guide: docs/HOW_TO_RUN.md")
    print("")
    print("Type / in Cursor. Examples:")
    for entry in manifest["skills"][:4]:
        print(f"  {entry['slash_command']}  →  {entry['title']}")
    print(f"  ... +{manifest['skill_count'] - 4} more")
    return 0


if __name__ == "__main__":
    sys.exit(main())
