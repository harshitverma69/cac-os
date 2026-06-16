## Agent: API Endpoint Map Agent (B2)

### Task ID
`B2`

### Capability Level
`B`

### Time Budget
30 minutes

### Objective
Identify every externally exposed API route and frontend route; map each to handler and controller via static inspection.

### Depends On
B1

### Inputs
- repository_path
- inventory_report.json (from B1, optional)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/B2/api_map_report.json`

```json
{
  "task_id": "B2",
  "endpoints": [],
  "frontend_routes": [],
  "controllers": [],
  "mapping": {}
}
```

See also: `verification/output_contracts.md`

### Eval Deliverables
- HTTP method
- Route
- Controller
- Handler method
- Source file path

### Rules
- Resolve HTTP routes from framework annotations/decorators only
- Resolve frontend routes from router config files
- Deduplicate by (method, normalized_path) or (route_type, path)
- Include source_file and line for every route
- No inference beyond code inspection

### Validation
- Endpoint count matches unique (method, route) pairs
- Every endpoint has handler_method and source_file
- DC-B2-01 through DC-B2-04 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION
- ZERO_ARTIFACTS on known API repos
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/B/B2_blueprint.md`

### Agent Spec Path
`agents/basics/B2_api_endpoint_map_agent.md`
