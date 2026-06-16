## Agent: Safe Change Agent (I3)

### Task ID
`I3`

### Capability Level
`I`

### Time Budget
60 minutes

### Objective
Make a small focused change in an unfamiliar module with minimal diff, test update, and verification log.

### Depends On
B3

### Inputs
- repository_path
- change_spec {description, target_module}
- test_discovery_report.json (B3, optional)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/I3/change_report.json`

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

See also: `verification/output_contracts.md`

### Eval Deliverables
- Diff/branch
- Files changed
- Why these files
- Test result
- Risk
- Agent vs verified

### Rules
- Diff must be minimal and focused on change_spec
- Every changed file listed with rationale
- Test command from B3 or discovered at runtime
- Separate agent_suggested vs manually_verified
- Risk: high if >3 files or public API change

### Validation
- files_changed non-empty
- test_result.exit_code == 0
- verification_log populated
- DC-I3-01 through DC-I3-03 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/I/I3_blueprint.md`

### Agent Spec Path
`agents/intermediate/I3_safe_change_agent.md`
