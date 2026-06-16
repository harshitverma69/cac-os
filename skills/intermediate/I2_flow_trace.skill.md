## Skill: Flow Trace Agent

### Task ID
`I2`

### Level
`INTERMEDIATE`

### Objective
Trace one endpoint, event, or cron job end-to-end from entry point to final DB/API/queue side effect.

### Depends On
- B2

### Input Contract
```json
{
  "repository_path": "required",
  "entry_point_id": "required",
  "api_map_report.json": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/intermediate/I2_flow_trace_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/I2/output.json`
- Validate output against Output Contract

### Output Contract (STRICT JSON)
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

### Validation Rules
- steps[0] is entry point
- All steps have file_path
- DC-I2-01 through DC-I2-04 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION: entry_point not found
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/intermediate/I2_flow_trace_agent.md`
- Blueprint: `eval_blueprints/I/I2_blueprint.md`
- Skill: `skills/intermediate/I2_flow_trace.skill.md`
