## Skill: Rust Greenfield CLI Agent

### Task ID
`B6`

### Level
`BASIC`

### Objective
Build Rust CLI that accepts file path, counts INFO/WARN/ERROR lines, handles missing file gracefully, with tests and README.

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
- Read agent spec: `agents/basics/B6_rust_greenfield_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/B6/output.json`
- Validate output against Output Contract
- Run `make skill-done RUN_ID={run_id} SKILL=B6` to open the report UI

### Output Contract (STRICT JSON)
```json
{
  "task_id": "B6",
  "project_path": "",
  "files_created": [],
  "cli": {
    "accepts": "file_path",
    "counts": [
      "INFO",
      "WARN",
      "ERROR"
    ],
    "missing_file_exit_code": 0
  },
  "tests": {
    "count": 0,
    "command": "cargo test",
    "exit_code": 0
  },
  "readme_commands": {
    "build": [],
    "run": [],
    "test": []
  },
  "run_proof": {
    "command": "",
    "exit_code": 0,
    "missing_file_proof": {
      "exit_code": 0
    }
  }
}
```

### Validation Rules
- tests.count >= 3
- missing_file_proof exit graceful
- DC-B6-01 through DC-B6-03 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION
- BUILD_FAILED
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/basics/B6_rust_greenfield_agent.md`
- Blueprint: `eval_blueprints/B/B6_blueprint.md`
- Skill: `skills/basics/B6_rust_greenfield.skill.md`
