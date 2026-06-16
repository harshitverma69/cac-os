## Agent: Flow Trace Agent (I2)

### Task ID
`I2`

### Capability Level
`I`

### Time Budget
45 minutes

### Objective
Trace one endpoint, event, or cron job end-to-end from entry point to final DB/API/queue side effect.

### Depends On
B2

### Inputs
- repository_path
- entry_point_id (METHOD:/path | event:name | cron:expression)
- api_map_report.json (B2, if endpoint)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/I2/flow_trace_report.json`

```json
{
  "task_id": "I2",
  "entry_point_id": "",
  "entry_type": "endpoint|event|cron",
  "steps": [],
  "external_dependencies": [],
  "side_effects": [],
  "sequence_diagram_mermaid": "",
  "uncertainties": []
}
```

See also: `verification/output_contracts.md`

### Eval Deliverables
- Entry point
- Step-by-step path
- External deps
- Side effects
- Sequence diagram
- Uncertainties

### Rules
- Static call graph traversal, max depth 20
- Every step: file_path, function_name, line
- Side effects: db_read, db_write, http_call, queue_publish
- sequence_diagram_mermaid valid Mermaid sequenceDiagram
- Uncertainties for unresolvable dynamic calls

### Validation
- steps[0] is entry point
- All steps have file_path
- DC-I2-01 through DC-I2-04 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION: entry_point not found
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/I/I2_blueprint.md`

### Agent Spec Path
`agents/intermediate/I2_flow_trace_agent.md`
