# CAC-OS — How to Run

## 1. Install dependencies

This repo is metadata-driven (no runtime agents required).

Ensure:

- Python 3.10+
- No external AI services required

---

## 2. Generate Skill Registry

Run:

```bash
make build-skills
```

This compiles all agent specs into:

- `skills/basics|intermediate|advanced|infra/*.skill.md`
- `core/skill_registry.json`
- `docs/SKILL_CATALOG.md` (what each skill does)

For the Cursor capability menu only:

```bash
make skills
```

Generates `skills/skill_registry.json` and `skills/skill_registry.md`.

---

## 2b. Execute Skills (Deterministic Runtime)

Single skill:

```bash
make run-skill SKILL=B1 RUN_ID=my-run
# or
python -m runtime --skill B1 --run-id my-run
```

Domain (includes transitive dependencies):

```bash
python -m runtime --domain B --run-id basics-run
```

Full pipeline (all 24 skills, DAG order):

```bash
make run-pipeline RUN_ID=full-run
# or
python -m runtime --full-pipeline --run-id full-run
```

Outputs per run:

- `generated_projects/{run_id}/{skill_id}/output.json`
- `generated_projects/{run_id}/execution_log.json`
- `generated_projects/{run_id}/final_report.json`

Run tests:

```bash
make test
```

---

## 3. Validate Agent Specs

Run deterministic validation:

```bash
make validate
```

Or directly:

```bash
python scripts/cac_os.py validate-registry
```

Checks:

- Agent specs, blueprints, and golden examples exist
- Required golden JSON fields present
- DAG dependency correctness (acyclic)

---

## 4. Understand System Execution Model

Read in order:

1. `core/capability_registry.md`
2. `execution_models/task_router.md`
3. `execution_models/dependency_graph.md`

---

## 5. How execution works (IMPORTANT)

This system does **not** run agents.

Instead:

1. Cursor reads agent MD specs (or the compiled skill registry)
2. Converts them into structured outputs
3. Writes JSON artifacts to `generated_projects/{run_id}/`

---

## 6. Run a Task (manual simulation)

Example: **B2 API Endpoint Map**

Steps:

1. Open `agents/basics/B2_api_endpoint_map_agent.md` (or find it via `skills/skill_registry.json`)
2. Follow the INPUT contract
3. Produce OUTPUT JSON exactly as specified
4. Save to: `generated_projects/{run_id}/B2/api_map_report.json`
5. Add a `manifest.json` for the run folder

Plan dependencies first:

```bash
make route INTENT=map_apis
```

---

## 7. Verify output

Run:

```bash
make validate-run RUN_DIR=generated_projects/{run_id}
```

See also: `verification/deterministic_checks.md` and `verification/output_contracts.md`

---

## 8. System Philosophy

- No runtime AI agents
- No inference layer
- No dynamic reasoning
- Only deterministic spec execution

---

## Architecture: Spec → Skill Compiler

```
Markdown Agent Specs (agents/)
        ↓
Skill Registry Generator (tools/build_skill_registry.py)
        ↓
Cursor-readable capability layer (skills/skill_registry.md)
        ↓
Manual / deterministic execution → generated_projects/{run_id}/
```
