## Skill: CI Pipeline Agent

### Task ID
`D3`

### Level
`INFRA`

### Objective
Write CI workflow that lints, tests, builds and tags container image with green run proof.

### Depends On
- B3
- I5

### Input Contract
```json
{
  "repository_path": "required",
  "ci_platform": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/infra_devops/D3_ci_pipeline_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/D3/output.json`
- Validate output against Output Contract
- Run `make skill-done RUN_ID={run_id} SKILL=D3` to open the report UI

### Output Contract (STRICT JSON)
```json
{
  "task_id": "D3",
  "workflow_file": "",
  "cache_config": {},
  "pass_proof": {
    "command_or_link": "",
    "exit_code": 0
  },
  "failure_demo": {
    "broken_commit": "",
    "expected_fail_stage": ""
  }
}
```

### Validation Rules
- pass_proof.exit_code == 0
- failure_demo documents expected fail
- DC-D3-01 through DC-D3-02 pass

### Failure Conditions
- WORKFLOW_INVALID
- PIPELINE_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/infra_devops/D3_ci_pipeline_agent.md`
- Blueprint: `eval_blueprints/D/D3_blueprint.md`
- Skill: `skills/infra/D3_ci_pipeline.skill.md`
