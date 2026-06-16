## Agent: Rust Greenfield CLI Agent (B6)

### Task ID
`B6`

### Capability Level
`B`

### Time Budget
60 minutes

### Objective
Build Rust CLI that accepts file path, counts INFO/WARN/ERROR lines, handles missing file gracefully, with tests and README.

### Depends On
None

### Inputs
- project_name (string)
- output_dir (absolute path)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/B6/greenfield_manifest.json`

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

See also: `verification/output_contracts.md`

### Eval Deliverables
- Cargo project
- CLI file path arg
- INFO/WARN/ERROR counts
- Missing file handling
- 3+ tests

### Rules
- Cargo project with clap or std::env::args for file path
- Count log level prefixes case-insensitively
- Missing file: graceful error message, non-panic exit
- Minimum 3 cargo tests including missing file case
- README with cargo build/run/test

### Validation
- tests.count >= 3
- missing_file_proof exit graceful
- DC-B6-01 through DC-B6-03 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION
- BUILD_FAILED
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/B/B6_blueprint.md`

### Agent Spec Path
`agents/basics/B6_rust_greenfield_agent.md`
