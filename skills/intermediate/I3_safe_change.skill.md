## Skill: Safe Change Agent

### Task ID
`I3`

### Level
`INTERMEDIATE`

### Objective
Make a small focused change in an unfamiliar module with minimal diff, test update, and verification log.

### Depends On
- B3

### Input Contract
```json
{
  "repository_path": "required",
  "change_spec": "required",
  "test_discovery_report.json": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/intermediate/I3_safe_change_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/I3/output.json`
- Validate output against Output Contract
- Run `make skill-done RUN_ID={run_id} SKILL=I3` to open the report UI

### Output Contract (STRICT JSON)
```json
{
  "task_id": "I3",
  "branch_or_diff_ref": "",
  "files_changed": [],
  "rationale": [],
  "test_command": "",
  "test_result": {
    "exit_code": 0
  },
  "risk_assessment": {
    "level": "low|medium|high",
    "factors": []
  },
  "verification_log": {
    "agent_suggested": [],
    "manually_verified": [],
    "uncertain": []
  }
}
```

### Validation Rules
- files_changed non-empty
- test_result.exit_code == 0
- verification_log populated
- DC-I3-01 through DC-I3-03 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/intermediate/I3_safe_change_agent.md`
- Blueprint: `eval_blueprints/I/I3_blueprint.md`
- Skill: `skills/intermediate/I3_safe_change.skill.md`
