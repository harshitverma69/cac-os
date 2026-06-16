## Skill: Polyglot FastAPI Node Agent

### Task ID
`I4`

### Level
`INTERMEDIATE`

### Objective
Build FastAPI /convert service and Node.js CLI client with hardcoded rates, tests, and two-terminal README.

### Depends On
- B4
- B5

### Input Contract
```json
{
  "output_dir": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/intermediate/I4_polyglot_fastapi_node_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/I4/output.json`
- Validate output against Output Contract
- Run `make skill-done RUN_ID={run_id} SKILL=I4` to open the report UI

### Output Contract (STRICT JSON)
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

### Validation Rules
- Both components run
- Integration script passes
- DC-I4-01 through DC-I4-02 pass

### Failure Conditions
- BUILD_FAILED
- INTEGRATION_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/intermediate/I4_polyglot_fastapi_node_agent.md`
- Blueprint: `eval_blueprints/I/I4_blueprint.md`
- Skill: `skills/intermediate/I4_polyglot_fastapi_node.skill.md`
