## Skill: Repo Artifact Inventory Agent

### Task ID
`B1`

### Level
`BASIC`

### Objective
Inspect an unfamiliar repository and produce a deterministic inventory of classes, interfaces, services, controllers, models, repositories, jobs, consumers, configs, and utilities.

### Depends On
None

### Input Contract
```json
{
  "repository_path": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/basics/B1_repo_artifact_inventory_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/B1/output.json`
- Validate output against Output Contract
- Run `make skill-done RUN_ID={run_id} SKILL=B1` to open the report UI

### Output Contract (STRICT JSON)
```json
{
  "task_id": "B1",
  "files_scanned": 0,
  "modules": [],
  "artifacts": {
    "classes": [],
    "interfaces": [],
    "services": [],
    "controllers": [],
    "models": [],
    "repositories": [],
    "jobs": [],
    "consumers": [],
    "configurations": [],
    "utilities": []
  },
  "dependency_graph_summary": {
    "nodes": [],
    "edges": []
  },
  "limitations": []
}
```

### Validation Rules
- files_scanned >= 1 for non-empty repositories
- Every artifact has non-empty file_path
- Major modules discovered with evidence paths
- DC-B1-01 through DC-B1-04 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION: repository_path missing or not a directory
- ZERO_ARTIFACTS: source files exist but zero artifacts extracted
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/basics/B1_repo_artifact_inventory_agent.md`
- Blueprint: `eval_blueprints/B/B1_blueprint.md`
- Skill: `skills/basics/B1_repo_artifact_inventory.skill.md`
