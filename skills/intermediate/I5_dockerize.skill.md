## Skill: Dockerize Agent

### Task ID
`I5`

### Level
`INTERMEDIATE`

### Objective
Containerize a service so it builds and runs cleanly in Docker with health check proof.

### Depends On
None

### Input Contract
```json
{
  "service_path": "required",
  "service_port": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/intermediate/I5_dockerize_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/I5/output.json`
- Validate output against Output Contract

### Output Contract (STRICT JSON)
```json
{
  "task_id": "I5",
  "dockerfile_path": "",
  "build_proof": {
    "command": "",
    "exit_code": 0
  },
  "run_proof": {
    "command": "",
    "exit_code": 0
  },
  "health_check": {
    "command": "",
    "response_status": 200,
    "response_body_sample": {}
  },
  "readme_commands": {
    "build": [],
    "run": [],
    "curl_proof": []
  }
}
```

### Validation Rules
- build_proof.exit_code == 0
- health_check.response_status == 200
- DC-I5-01 through DC-I5-02 pass

### Failure Conditions
- BUILD_FAILED
- RUN_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/intermediate/I5_dockerize_agent.md`
- Blueprint: `eval_blueprints/I/I5_blueprint.md`
- Skill: `skills/intermediate/I5_dockerize.skill.md`
