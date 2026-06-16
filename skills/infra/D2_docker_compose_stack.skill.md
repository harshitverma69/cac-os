## Skill: Docker Compose Stack Agent

### Task ID
`D2`

### Level
`INFRA`

### Objective
Stand up multi-service stack (API + DB + worker) with docker-compose, seed data, and E2E test script.

### Depends On
- I5

### Input Contract
```json
{
  "output_dir": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/infra_devops/D2_docker_compose_stack_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/D2/output.json`
- Validate output against Output Contract

### Output Contract (STRICT JSON)
```json
{
  "task_id": "D2",
  "compose_file": "",
  "dockerfiles": [],
  "seed_script": "",
  "test_run": {
    "command": "",
    "exit_code": 0
  },
  "inter_service_logs_proof": [],
  "teardown": {
    "command": "",
    "reup_proof": {
      "exit_code": 0
    }
  }
}
```

### Validation Rules
- test_run.exit_code == 0
- reup_proof.exit_code == 0
- DC-D2-01 through DC-D2-02 pass

### Failure Conditions
- COMPOSE_UP_FAILED
- E2E_TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/infra_devops/D2_docker_compose_stack_agent.md`
- Blueprint: `eval_blueprints/D/D2_blueprint.md`
- Skill: `skills/infra/D2_docker_compose_stack.skill.md`
