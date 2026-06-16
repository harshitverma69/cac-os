## Skill: Full Pipeline (All Skills)

### Task ID
`ALL`

### Level
`PIPELINE`

### Objective
Execute all 24 CAC-OS skills in DAG order with deterministic outputs. No skill may be skipped; dependencies are enforced before each wave.

### Depends On
None

### Input Contract
```json
{
  "repository_path": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Load `core/skill_registry.json` and build dependency DAG
- Validate DAG is acyclic
- Compute topological execution order for all 24 skills
- Schedule parallel waves for independent skills only
- For each skill: validate inputs, load golden reference, validate output schema, write `output.json`
- Write `execution_log.json` and `final_report.json`

### Output Contract (STRICT JSON)
```json
{
  "run_id": "string",
  "status": "complete",
  "skills_completed": [],
  "skills_failed": [],
  "total_skills": 24,
  "execution_log": "generated_projects/{run_id}/execution_log.json"
}
```

### Validation Rules
- All 24 skills must complete without schema errors
- Execution order must respect DAG dependencies
- Parallel lanes may only include mutually independent skills

### Failure Conditions
- missing input
- schema mismatch
- cycle detected in DAG
- missing dependency output
- skill execution aborted mid-pipeline

### Pipeline Order (24 tasks — DAG enforced)

```
B1 → B2 → B3 → B4 → B5 → B6 → I1 → I2 → I3 → I4 → I5 → I6 → A1 → A2 → A3 → A4 → A5 → A6 → D1 → D2 → D3 → D4 → D5 → D6
```

### Domain Groups

| Domain | Skills |
|--------|--------|
| BASIC (B) | B1, B2, B3, B4, B5, B6 |
| INTERMEDIATE (I) | I1, I2, I3, I4, I5, I6 |
| ADVANCED (A) | A1, A2, A3, A4, A5, A6 |
| INFRA (D) | D1, D2, D3, D4, D5, D6 |

### Sources
- Registry: `core/skill_registry.json`
- Orchestrator: `runtime/skill_orchestrator.py`
- Runner: `runtime/skill_runner.py`
