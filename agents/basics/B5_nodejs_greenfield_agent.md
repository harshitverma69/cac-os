## Agent: Node.js Greenfield API Agent (B5)

### Task ID
`B5`

### Capability Level
`B`

### Time Budget
60 minutes

### Objective
Build equivalent transaction/balance service as Node.js API or CLI with tests and README.

### Depends On
B4

### Inputs
- project_name (string)
- output_dir (absolute path)
- mode (api|cli)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/B5/greenfield_manifest.json`

```json
{
  "task_id": "B5",
  "project_path": "",
  "mode": "api|cli",
  "files_created": [],
  "endpoints_or_commands": [],
  "tests": {
    "count": 0,
    "command": "",
    "exit_code": 0
  },
  "readme_commands": {
    "install": [],
    "run": [],
    "test": []
  },
  "run_proof": {
    "command": "",
    "exit_code": 0
  }
}
```

See also: `verification/output_contracts.md`

### Eval Deliverables
- Node API or CLI
- Equivalent endpoints/commands
- Tests
- README

### Rules
- Mirror B4 data contract: transactions + balance
- Use Express/Fastify for api mode or commander for cli mode
- Minimum 3 tests (jest or vitest)
- package.json with scripts
- Proof of run required

### Validation
- tests.count >= 3
- run_proof.exit_code == 0
- DC-B5-01 through DC-B5-02 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION
- BUILD_FAILED
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/B/B5_blueprint.md`

### Agent Spec Path
`agents/basics/B5_nodejs_greenfield_agent.md`
