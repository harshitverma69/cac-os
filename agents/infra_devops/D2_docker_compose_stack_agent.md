## Agent: Docker Compose Stack Agent (D2)

### Task ID
`D2`

### Capability Level
`D`

### Time Budget
90 minutes

### Objective
Stand up multi-service stack (API + DB + worker) with docker-compose, seed data, and E2E test script.

### Depends On
I5

### Inputs
- output_dir (absolute path)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/D2/compose_manifest.json`

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

See also: `verification/output_contracts.md`

### Eval Deliverables
- compose.yml
- Dockerfiles
- Seed script
- E2E test output
- Logs
- Teardown/re-up

### Rules
- docker-compose.yml with api, database, worker services
- Seed/fixture script for DB
- One-command E2E test all green
- Logs prove inter-service communication
- Teardown + clean re-up from zero

### Validation
- test_run.exit_code == 0
- reup_proof.exit_code == 0
- DC-D2-01 through DC-D2-02 pass

### Failure Conditions
- COMPOSE_UP_FAILED
- E2E_TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/D/D2_blueprint.md`

### Agent Spec Path
`agents/infra_devops/D2_docker_compose_stack_agent.md`
