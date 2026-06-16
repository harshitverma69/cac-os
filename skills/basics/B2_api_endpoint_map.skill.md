## Skill: API Endpoint Map Agent

### Task ID
`B2`

### Level
`BASIC`

### Objective
Identify every externally exposed API route and frontend route; map each to handler and controller via static inspection.

### Depends On
- B1

### Input Contract
```json
{
  "repository_path": "required",
  "inventory_report.json": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/basics/B2_api_endpoint_map_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/B2/output.json`
- Validate output against Output Contract

### Output Contract (STRICT JSON)
```json
{
  "task_id": "B2",
  "endpoints": [],
  "frontend_routes": [],
  "controllers": [],
  "mapping": {}
}
```

### Validation Rules
- Endpoint count matches unique (method, route) pairs
- Every endpoint has handler_method and source_file
- DC-B2-01 through DC-B2-04 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION
- ZERO_ARTIFACTS on known API repos
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/basics/B2_api_endpoint_map_agent.md`
- Blueprint: `eval_blueprints/B/B2_blueprint.md`
- Skill: `skills/basics/B2_api_endpoint_map.skill.md`
