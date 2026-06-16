## Agent: CI Pipeline Agent (D3)

### Task ID
`D3`

### Capability Level
`D`

### Time Budget
45 minutes

### Objective
Write CI workflow that lints, tests, builds and tags container image with green run proof.

### Depends On
B3, I5

### Inputs
- repository_path
- ci_platform (github_actions|gitlab_ci)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/D3/ci_manifest.json`

```json
{
  "task_id": "D3",
  "workflow_file": "",
  "cache_config": {},
  "pass_proof": {
    "command_or_link": "",
    "exit_code": 0
  },
  "failure_demo": {
    "broken_commit": "",
    "expected_fail_stage": ""
  }
}
```

See also: `verification/output_contracts.md`

### Eval Deliverables
- Workflow YAML
- Cache/matrix
- Green run proof
- Failure mode demo

### Rules
- Stages: lint → test → build image → tag
- Cache config if matrix/dependencies heavy
- pass_proof: local act run or CI link
- failure_demo: deliberately broken commit fails at expected stage

### Validation
- pass_proof.exit_code == 0
- failure_demo documents expected fail
- DC-D3-01 through DC-D3-02 pass

### Failure Conditions
- WORKFLOW_INVALID
- PIPELINE_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/D/D3_blueprint.md`

### Agent Spec Path
`agents/infra_devops/D3_ci_pipeline_agent.md`
