## Agent: Dockerize Agent (I5)

### Task ID
`I5`

### Capability Level
`I`

### Time Budget
60 minutes

### Objective
Containerize a service so it builds and runs cleanly in Docker with health check proof.

### Depends On
None

### Inputs
- service_path (absolute path)
- service_port (integer)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/I5/docker_manifest.json`

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

See also: `verification/output_contracts.md`

### Eval Deliverables
- Dockerfile
- Build proof
- Container run proof
- Health/curl proof
- README

### Rules
- Multi-stage Dockerfile preferred
- build_proof: docker build succeeds
- run_proof: container starts and responds
- health_check: curl or wget against /health or root
- README with docker build and run commands

### Validation
- build_proof.exit_code == 0
- health_check.response_status == 200
- DC-I5-01 through DC-I5-02 pass

### Failure Conditions
- BUILD_FAILED
- RUN_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/I/I5_blueprint.md`

### Agent Spec Path
`agents/intermediate/I5_dockerize_agent.md`
