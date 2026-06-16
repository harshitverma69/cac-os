## Skill: FastAPI Greenfield Service Agent

### Task ID
`B4`

### Level
`BASIC`

### Objective
Build a small Python FastAPI service from scratch with POST/GET endpoints, input validation, tests, and README.

### Depends On
None

### Input Contract
```json
{
  "project_name": "required",
  "output_dir": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/basics/B4_fastapi_greenfield_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/B4/output.json`
- Validate output against Output Contract
- Run `make skill-done RUN_ID={run_id} SKILL=B4` to open the report UI

### Output Contract (STRICT JSON)
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

### Validation Rules
- files_created includes main.py, requirements.txt, README.md, tests/
- tests.count >= 3
- run_proof.exit_code == 0
- DC-B4-01 through DC-B4-03 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION
- BUILD_FAILED
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/basics/B4_fastapi_greenfield_agent.md`
- Blueprint: `eval_blueprints/B/B4_blueprint.md`
- Skill: `skills/basics/B4_fastapi_greenfield.skill.md`
