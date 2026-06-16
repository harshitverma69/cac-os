## Agent: Kubernetes Manifests Agent (D4)

### Task ID
`D4`

### Capability Level
`D`

### Time Budget
60 minutes

### Objective
Write K8s manifests, validate with dry-run/kubeval, deploy on kind/minikube with curl proof.

### Depends On
I5

### Inputs
- service_path (absolute path)
- cluster (kind|minikube)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/D4/k8s_manifest.json`

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

See also: `verification/output_contracts.md`

### Eval Deliverables
- Manifest YAML
- Dry-run output
- kubectl apply
- curl proof
- README

### Rules
- Deployment, Service, ConfigMap required; Ingress optional
- dry-run or kubeval before apply
- Local cluster only (kind/minikube)
- curl or port-forward proof
- README with up/down commands

### Validation
- dry_run_proof.exit_code == 0
- curl_proof.response_status == 200
- DC-D4-01 through DC-D4-02 pass

### Failure Conditions
- VALIDATION_FAILED
- APPLY_FAILED
- CURL_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/D/D4_blueprint.md`

### Agent Spec Path
`agents/infra_devops/D4_kubernetes_manifests_agent.md`
