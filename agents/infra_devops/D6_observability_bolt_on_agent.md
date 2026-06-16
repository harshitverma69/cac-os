## Agent: Observability Bolt-On Agent (D6)

### Task ID
`D6`

### Capability Level
`D`

### Time Budget
60 minutes

### Objective
Add structured logging and /metrics endpoint; stand up Prometheus + Grafana with working dashboard panel.

### Depends On
I5

### Inputs
- service_path (absolute path)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/D6/observability_manifest.json`

```json
{
  "task_id": "D6",
  "code_diff_files": [],
  "metrics_endpoint": "/metrics",
  "compose_stack": {
    "prometheus": "",
    "grafana": ""
  },
  "dashboard_panel": {
    "title": "",
    "query": "",
    "data_proof": {}
  },
  "load_script": "",
  "readme_run_order": []
}
```

See also: `verification/output_contracts.md`

### Eval Deliverables
- Logging/metrics diff
- Prometheus/Grafana compose
- Load script
- Dashboard panel proof
- README

### Rules
- Structured JSON logging added to service
- Prometheus-compatible /metrics endpoint
- docker-compose for Prometheus + Grafana with provisioned datasource
- Load script generates traffic
- dashboard_panel data_proof: JSON snapshot or screenshot ref path

### Validation
- /metrics returns prometheus format
- dashboard_panel has data
- DC-D6-01 through DC-D6-02 pass

### Failure Conditions
- METRICS_FAILED
- DASHBOARD_NO_DATA
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/D/D6_blueprint.md`

### Agent Spec Path
`agents/infra_devops/D6_observability_bolt_on_agent.md`
