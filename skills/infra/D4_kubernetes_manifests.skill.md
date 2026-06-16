## Skill: Kubernetes Manifests Agent

### Task ID
`D4`

### Level
`INFRA`

### Objective
Write K8s manifests, validate with dry-run/kubeval, deploy on kind/minikube with curl proof.

### Depends On
- I5

### Input Contract
```json
{
  "service_path": "required",
  "cluster": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/infra_devops/D4_kubernetes_manifests_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/D4/output.json`
- Validate output against Output Contract
- Run `make skill-done RUN_ID={run_id} SKILL=D4` to open the report UI

### Output Contract (STRICT JSON)
```json
{
  "task_id": "D4",
  "manifests": [],
  "dry_run_proof": {
    "command": "",
    "exit_code": 0
  },
  "apply_proof": {
    "command": "kubectl apply",
    "exit_code": 0
  },
  "curl_proof": {
    "command": "",
    "response_status": 200
  },
  "readme": {
    "up": [],
    "down": []
  }
}
```

### Validation Rules
- dry_run_proof.exit_code == 0
- curl_proof.response_status == 200
- DC-D4-01 through DC-D4-02 pass

### Failure Conditions
- VALIDATION_FAILED
- APPLY_FAILED
- CURL_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/infra_devops/D4_kubernetes_manifests_agent.md`
- Blueprint: `eval_blueprints/D/D4_blueprint.md`
- Skill: `skills/infra/D4_kubernetes_manifests.skill.md`
