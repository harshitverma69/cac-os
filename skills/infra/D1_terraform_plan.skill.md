## Skill: Terraform Plan Agent

### Task ID
`D1`

### Level
`INFRA`

### Objective
Write Terraform for small service that passes validate and produces clean plan against test backend.

### Depends On
None

### Input Contract
```json
{
  "output_dir": "required",
  "provider": "required",
  "resources": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/infra_devops/D1_terraform_plan_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/D1/output.json`
- Validate output against Output Contract

### Output Contract (STRICT JSON)
```json
{
  "task_id": "D1",
  "tf_files": [],
  "variables": {},
  "validate_proof": {
    "command": "terraform validate",
    "exit_code": 0
  },
  "plan_proof": {
    "command": "terraform plan",
    "exit_code": 0,
    "changes_summary": {}
  },
  "readme": {
    "apply": [],
    "destroy": []
  }
}
```

### Validation Rules
- validate_proof.exit_code == 0
- plan_proof.exit_code == 0
- DC-D1-01 through DC-D1-02 pass

### Failure Conditions
- VALIDATE_FAILED
- PLAN_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/infra_devops/D1_terraform_plan_agent.md`
- Blueprint: `eval_blueprints/D/D1_blueprint.md`
- Skill: `skills/infra/D1_terraform_plan.skill.md`
