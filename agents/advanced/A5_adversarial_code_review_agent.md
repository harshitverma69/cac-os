## Agent: Adversarial Code Review Agent (A5)

### Task ID
`A5`

### Capability Level
`A`

### Time Budget
60 minutes

### Objective
Review agent-generated PR for correctness, security, test, performance, maintainability issues; propose fixes.

### Depends On
None

### Inputs
- diff_or_pr_ref (string)
- repository_path

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/A5/code_review_report.json`

```json
{
  "task_id": "A5",
  "issues": [
    {
      "id": "",
      "category": "correctness|security|test|performance|maintainability",
      "severity": "blocking|non_blocking",
      "file_path": "",
      "line": 0,
      "description": "",
      "suggested_fix": "",
      "verification_steps": []
    }
  ]
}
```

See also: `verification/output_contracts.md`

### Eval Deliverables
- Issue list
- Severity classification
- Suggested fixes
- Verification steps

### Rules
- Issue categories: correctness, security, test, performance, maintainability
- Severity: blocking | non_blocking
- Every issue has suggested_fix and verification_steps
- Evidence: file_path + line from diff
- No approval without addressing blocking issues

### Validation
- Every issue has category and severity
- blocking issues have suggested_fix
- DC-A5-01 through DC-A5-02 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION: no diff
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/A/A5_blueprint.md`

### Agent Spec Path
`agents/advanced/A5_adversarial_code_review_agent.md`
