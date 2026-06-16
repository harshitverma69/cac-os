## Agent: FastAPI Greenfield Service Agent (B4)

### Task ID
`B4`

### Capability Level
`B`

### Time Budget
60 minutes

### Objective
Build a small Python FastAPI service from scratch with POST/GET endpoints, input validation, tests, and README.

### Depends On
None

### Inputs
- project_name (string)
- output_dir (absolute path)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/B4/greenfield_manifest.json`

```json
{
  "task_id": "B4",
  "project_path": "",
  "files_created": [],
  "endpoints": [
    "POST /transactions",
    "GET /transactions",
    "GET /balance"
  ],
  "tests": {
    "count": 0,
    "files": [],
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
    "exit_code": 0,
    "response_sample": {}
  }
}
```

See also: `verification/output_contracts.md`

### Eval Deliverables
- FastAPI app
- POST/GET endpoints
- Input validation
- 3+ tests
- README commands

### Rules
- Create FastAPI app with POST /transactions, GET /transactions, GET /balance
- Input validation via Pydantic models
- Minimum 3 pytest tests
- README with install/run/test commands
- run_proof requires actual server start or TestClient invocation
- Output is file manifest + proof, not prose

### Validation
- files_created includes main.py, requirements.txt, README.md, tests/
- tests.count >= 3
- run_proof.exit_code == 0
- DC-B4-01 through DC-B4-03 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION
- BUILD_FAILED
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/B/B4_blueprint.md`

### Agent Spec Path
`agents/basics/B4_fastapi_greenfield_agent.md`
