## Agent: Modernization Executable Agent (A4)

### Task ID
`A4`

### Capability Level
`A`

### Time Budget
90 minutes

### Objective
Analyze repo for modernization opportunities, prioritize, implement highest-value lowest-risk first step.

### Depends On
B1, B3

### Inputs
- repository_path
- inventory_report.json (B1)
- test_discovery_report.json (B3)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/A4/modernization_report.json`

```json
{
  "task_id": "A4",
  "findings": [],
  "prioritized_plan": [],
  "first_step": {
    "action": "",
    "files_changed": [],
    "evidence": []
  },
  "verification": {
    "command": "",
    "exit_code": 0
  },
  "rollback_notes": []
}
```

See also: `verification/output_contracts.md`

### Eval Deliverables
- Findings with evidence
- Prioritized plan
- First step implemented
- Verification
- Rollback

### Rules
- Findings require file/config evidence paths
- Prioritize: value=impact score, risk=change scope
- First step must be implemented (not plan-only)
- Verification: build, test, or lint command with exit_code 0
- Rollback notes: git revert or manual steps

### Validation
- first_step.files_changed non-empty
- verification.exit_code == 0
- DC-A4-01 through DC-A4-02 pass

### Failure Conditions
- NO_FINDINGS
- IMPLEMENTATION_FAILED
- VERIFICATION_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/A/A4_blueprint.md`

### Agent Spec Path
`agents/advanced/A4_modernization_executable_agent.md`
