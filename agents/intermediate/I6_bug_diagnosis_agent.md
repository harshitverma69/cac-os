## Agent: Bug Diagnosis Agent (I6)

### Task ID
`I6`

### Capability Level
`I`

### Time Budget
60 minutes

### Objective
Reproduce seeded bug, identify root cause with file paths, apply minimal fix, verify with command proof.

### Depends On
I2

### Inputs
- repository_path
- bug_context {symptoms, reproduction_hint}
- flow_trace_report.json (I2, optional)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/I6/bug_fix_report.json`

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

See also: `verification/output_contracts.md`

### Eval Deliverables
- Reproduction
- Root cause paths
- Minimal fix
- Verification result
- Agent vs verified

### Rules
- Reproduction steps must be executable commands
- Root cause requires file_path + line evidence
- Fix must be minimal (smallest diff)
- Verification command proves bug no longer reproduces
- Separate agent_suggested vs manually_verified

### Validation
- root_cause.file_path exists
- verification.exit_code == 0
- DC-I6-01 through DC-I6-03 pass

### Failure Conditions
- REPRODUCTION_FAILED
- FIX_FAILED
- VERIFICATION_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/I/I6_blueprint.md`

### Agent Spec Path
`agents/intermediate/I6_bug_diagnosis_agent.md`
