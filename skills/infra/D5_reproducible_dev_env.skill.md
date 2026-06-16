## Skill: Reproducible Dev Environment Agent

### Task ID
`D5`

### Level
`INFRA`

### Objective
Bootstrap repo from fresh clone with single command; tests pass on clean machine.

### Depends On
- B3

### Input Contract
```json
{
  "repository_path": "required",
  "bootstrap_type": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/infra_devops/D5_reproducible_dev_env_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/D5/output.json`
- Validate output against Output Contract
- Run `make skill-done RUN_ID={run_id} SKILL=D5` to open the report UI

### Output Contract (STRICT JSON)
```json
{
  "task_id": "D5",
  "config_files": [],
  "bootstrap_command": "",
  "bootstrap_proof": {
    "command": "",
    "exit_code": 0,
    "output_hash": ""
  },
  "test_proof": {
    "command": "",
    "exit_code": 0
  },
  "previously_implicit": []
}
```

### Validation Rules
- bootstrap_proof.exit_code == 0
- test_proof.exit_code == 0
- DC-D5-01 through DC-D5-02 pass

### Failure Conditions
- BOOTSTRAP_FAILED
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/infra_devops/D5_reproducible_dev_env_agent.md`
- Blueprint: `eval_blueprints/D/D5_blueprint.md`
- Skill: `skills/infra/D5_reproducible_dev_env.skill.md`
