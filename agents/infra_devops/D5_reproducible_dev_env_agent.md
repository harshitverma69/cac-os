## Agent: Reproducible Dev Environment Agent (D5)

### Task ID
`D5`

### Capability Level
`D`

### Time Budget
45 minutes

### Objective
Bootstrap repo from fresh clone with single command; tests pass on clean machine.

### Depends On
B3

### Inputs
- repository_path
- bootstrap_type (devcontainer|nix|makefile_mise)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/D5/bootstrap_manifest.json`

```json
{
  "task_id": "D5",
  "config_files": [],
  "bootstrap_command": "",
  "bootstrap_proof": {
    "command": "",
    "exit_code": 0,
    "output_hash": ""
  },
  "test_proof": {
    "command": "",
    "exit_code": 0
  },
  "previously_implicit": []
}
```

See also: `verification/output_contracts.md`

### Eval Deliverables
- Bootstrap config
- Single command output
- Passing tests
- Implicit deps notes

### Rules
- Single command bootstrap from fresh clone
- Document previously implicit deps: system packages, env vars, versions
- test_proof uses B3 discovered test command
- Proof requires actual command output hash

### Validation
- bootstrap_proof.exit_code == 0
- test_proof.exit_code == 0
- DC-D5-01 through DC-D5-02 pass

### Failure Conditions
- BOOTSTRAP_FAILED
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/D/D5_blueprint.md`

### Agent Spec Path
`agents/infra_devops/D5_reproducible_dev_env_agent.md`
