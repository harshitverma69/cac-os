## Skill: Node.js Greenfield API Agent

### Task ID
`B5`

### Level
`BASIC`

### Objective
Build equivalent transaction/balance service as Node.js API or CLI with tests and README.

### Depends On
- B4

### Input Contract
```json
{
  "project_name": "required",
  "output_dir": "required",
  "mode": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/basics/B5_nodejs_greenfield_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/B5/output.json`
- Validate output against Output Contract

### Output Contract (STRICT JSON)
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

### Validation Rules
- tests.count >= 3
- run_proof.exit_code == 0
- DC-B5-01 through DC-B5-02 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION
- BUILD_FAILED
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/basics/B5_nodejs_greenfield_agent.md`
- Blueprint: `eval_blueprints/B/B5_blueprint.md`
- Skill: `skills/basics/B5_nodejs_greenfield.skill.md`
