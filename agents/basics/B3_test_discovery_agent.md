## Agent: Test Discovery Agent (B3)

### Task ID
`B3`

### Capability Level
`B`

### Time Budget
15 minutes

### Objective
Find test framework, config file, relevant test files, and exact commands to run tests for a module.

### Depends On
None

### Inputs
- repository_path
- module_path (optional string)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/B3/test_discovery_report.json`

```json
{
  "task_id": "B3",
  "framework": "",
  "config_files": [],
  "test_files": [],
  "commands": {
    "unit": "",
    "integration": "",
    "coverage": ""
  },
  "command_result": {
    "exit_code": 0,
    "stdout_hash": "",
    "stderr_hash": ""
  },
  "failures": [],
  "interpretation": []
}
```

See also: `verification/output_contracts.md`

### Eval Deliverables
- Test framework and config
- Relevant test files
- Exact commands
- Command result
- Failure interpretation

### Rules
- Detect framework from config files: pytest.ini, jest.config, Cargo.toml [dev-dependencies], pom.xml
- Test files by naming convention: test_*, *_test.*, *.spec.*, *_test.rs
- Commands must be copy-paste executable shell strings
- command_result populated only after actual command execution proof
- Interpretation references specific failing test names if failures exist

### Validation
- framework is non-empty for repos with tests
- At least one test command defined
- test_files paths exist on disk
- DC-B3-01 through DC-B3-03 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION
- ZERO_ARTIFACTS: no test framework detected
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/B/B3_blueprint.md`

### Agent Spec Path
`agents/basics/B3_test_discovery_agent.md`
