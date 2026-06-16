## Skill: Bug Diagnosis Agent

### Task ID
`I6`

### Level
`INTERMEDIATE`

### Objective
Reproduce seeded bug, identify root cause with file paths, apply minimal fix, verify with command proof.

### Depends On
- I2

### Input Contract
```json
{
  "repository_path": "required",
  "bug_context": "required",
  "flow_trace_report.json": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/intermediate/I6_bug_diagnosis_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/I6/output.json`
- Validate output against Output Contract

### Output Contract (STRICT JSON)
```json
{
  "task_id": "I6",
  "reproduction_steps": [],
  "root_cause": {
    "file_path": "",
    "line": 0,
    "description": ""
  },
  "fix": {
    "files_changed": [],
    "diff_summary": ""
  },
  "verification": {
    "command": "",
    "exit_code": 0
  },
  "verification_log": {
    "agent_suggested": [],
    "manually_verified": []
  }
}
```

### Validation Rules
- root_cause.file_path exists
- verification.exit_code == 0
- DC-I6-01 through DC-I6-03 pass

### Failure Conditions
- REPRODUCTION_FAILED
- FIX_FAILED
- VERIFICATION_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/intermediate/I6_bug_diagnosis_agent.md`
- Blueprint: `eval_blueprints/I/I6_blueprint.md`
- Skill: `skills/intermediate/I6_bug_diagnosis.skill.md`
