## Agent: Terraform Plan Agent (D1)

### Task ID
`D1`

### Capability Level
`D`

### Time Budget
60 minutes

### Objective
Write Terraform for small service that passes validate and produces clean plan against test backend.

### Depends On
None

### Inputs
- output_dir (absolute path)
- provider (aws|gcp)
- resources (string[])

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/D1/terraform_manifest.json`

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

See also: `verification/output_contracts.md`

### Eval Deliverables
- .tf files
- Provider/backend
- validate output
- plan output
- README

### Rules
- Include provider, variables, backend config
- terraform validate must pass
- terraform plan against local/test backend (no real cloud spend)
- README with apply and destroy commands

### Validation
- validate_proof.exit_code == 0
- plan_proof.exit_code == 0
- DC-D1-01 through DC-D1-02 pass

### Failure Conditions
- VALIDATE_FAILED
- PLAN_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/D/D1_blueprint.md`

### Agent Spec Path
`agents/infra_devops/D1_terraform_plan_agent.md`
