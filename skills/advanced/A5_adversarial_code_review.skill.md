## Skill: Adversarial Code Review Agent

### Task ID
`A5`

### Level
`ADVANCED`

### Objective
Review agent-generated PR for correctness, security, test, performance, maintainability issues; propose fixes.

### Depends On
None

### Input Contract
```json
{
  "diff_or_pr_ref": "required",
  "repository_path": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/advanced/A5_adversarial_code_review_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/A5/output.json`
- Validate output against Output Contract

### Output Contract (STRICT JSON)
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

### Validation Rules
- Every issue has category and severity
- blocking issues have suggested_fix
- DC-A5-01 through DC-A5-02 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION: no diff
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/advanced/A5_adversarial_code_review_agent.md`
- Blueprint: `eval_blueprints/A/A5_blueprint.md`
- Skill: `skills/advanced/A5_adversarial_code_review.skill.md`
