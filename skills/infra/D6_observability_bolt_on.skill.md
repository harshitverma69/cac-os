## Skill: Observability Bolt-On Agent

### Task ID
`D6`

### Level
`INFRA`

### Objective
Add structured logging and /metrics endpoint; stand up Prometheus + Grafana with working dashboard panel.

### Depends On
- I5

### Input Contract
```json
{
  "service_path": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/infra_devops/D6_observability_bolt_on_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/D6/output.json`
- Validate output against Output Contract
- Run `make skill-done RUN_ID={run_id} SKILL=D6` to open the report UI

### Output Contract (STRICT JSON)
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

### Validation Rules
- /metrics returns prometheus format
- dashboard_panel has data
- DC-D6-01 through DC-D6-02 pass

### Failure Conditions
- METRICS_FAILED
- DASHBOARD_NO_DATA
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/infra_devops/D6_observability_bolt_on_agent.md`
- Blueprint: `eval_blueprints/D/D6_blueprint.md`
- Skill: `skills/infra/D6_observability_bolt_on.skill.md`
