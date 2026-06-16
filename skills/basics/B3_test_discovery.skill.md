## Skill: Test Discovery Agent

### Task ID
`B3`

### Level
`BASIC`

### Objective
Find test framework, config file, relevant test files, and exact commands to run tests for a module.

### Depends On
None

### Input Contract
```json
{
  "repository_path": "required",
  "module_path": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/basics/B3_test_discovery_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/B3/output.json`
- Validate output against Output Contract
- Run `make skill-done RUN_ID={run_id} SKILL=B3` to open the report UI

### Output Contract (STRICT JSON)
```json
{
  "task_id": "B3",
  "framework": "",
  "config_files": [],
  "test_files": [],
  "commands": {
    "unit": "",
    "integration": "",
    "coverage": ""
  },
  "command_result": {
    "exit_code": 0,
    "stdout_hash": "",
    "stderr_hash": ""
  },
  "failures": [],
  "interpretation": []
}
```

### Validation Rules
- framework is non-empty for repos with tests
- At least one test command defined
- test_files paths exist on disk
- DC-B3-01 through DC-B3-03 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION
- ZERO_ARTIFACTS: no test framework detected
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/basics/B3_test_discovery_agent.md`
- Blueprint: `eval_blueprints/B/B3_blueprint.md`
- Skill: `skills/basics/B3_test_discovery.skill.md`
