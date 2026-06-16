## Agent: Polyglot FastAPI Node Agent (I4)

### Task ID
`I4`

### Capability Level
`I`

### Time Budget
90 minutes

### Objective
Build FastAPI /convert service and Node.js CLI client with hardcoded rates, tests, and two-terminal README.

### Depends On
B4, B5

### Inputs
- output_dir (absolute path)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/I4/polyglot_manifest.json`

```json
{
  "task_id": "I4",
  "fastapi_service": {
    "path": "",
    "endpoint": "POST /convert",
    "tests": {
      "count": 0,
      "exit_code": 0
    }
  },
  "node_client": {
    "path": "",
    "tests_or_script": {
      "command": "",
      "exit_code": 0
    }
  },
  "data_contract": {
    "request": {},
    "response": {}
  },
  "readme": {
    "terminal_1": [],
    "terminal_2": []
  }
}
```

See also: `verification/output_contracts.md`

### Eval Deliverables
- FastAPI /convert
- Node CLI client
- Validation
- Tests
- Two-terminal README

### Rules
- FastAPI POST /convert with input validation
- Node CLI calls service via HTTP
- Hardcoded conversion rates in config
- Service tests >= 2; client verification scripted
- README with two-terminal run order

### Validation
- Both components run
- Integration script passes
- DC-I4-01 through DC-I4-02 pass

### Failure Conditions
- BUILD_FAILED
- INTEGRATION_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/I/I4_blueprint.md`

### Agent Spec Path
`agents/intermediate/I4_polyglot_fastapi_node_agent.md`
