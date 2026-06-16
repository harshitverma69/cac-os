## Agent: Repo Artifact Inventory Agent (B1)

### Task ID
`B1`

### Capability Level
`B`

### Time Budget
30 minutes

### Objective
Inspect an unfamiliar repository and produce a deterministic inventory of classes, interfaces, services, controllers, models, repositories, jobs, consumers, configs, and utilities.

### Depends On
None

### Inputs
- repository_path (absolute string)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/B1/inventory_report.json`

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

See also: `verification/output_contracts.md`

### Eval Deliverables
- Total files scanned
- Major modules discovered
- Evidence file paths
- Known limitations

### Rules
- Scan parseable source files only (.java, .py, .ts, .js, .go, .rs, .kt)
- Classify artifacts by naming convention, annotations, and directory patterns
- Build dependency edges from import/require statements only
- Every artifact entry must include file_path evidence
- Sort all arrays by name ascending (DT-10)
- No prose or explanation in output JSON

### Validation
- files_scanned >= 1 for non-empty repositories
- Every artifact has non-empty file_path
- Major modules discovered with evidence paths
- DC-B1-01 through DC-B1-04 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION: repository_path missing or not a directory
- ZERO_ARTIFACTS: source files exist but zero artifacts extracted
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/B/B1_blueprint.md`

### Agent Spec Path
`agents/basics/B1_repo_artifact_inventory_agent.md`
