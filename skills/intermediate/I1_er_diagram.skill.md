## Skill: ER Diagram Agent

### Task ID
`I1`

### Level
`INTERMEDIATE`

### Objective
Build ER diagram for all tables and entities from repo source only; cite source file for every claim.

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
- Read agent spec: `agents/intermediate/I1_er_diagram_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/I1/output.json`
- Validate output against Output Contract
- Run `make skill-done RUN_ID={run_id} SKILL=I1` to open the report UI

### Output Contract (STRICT JSON)
```json
{
  "task_id": "I1",
  "tables": [],
  "relationships": [],
  "mermaid_er": "string"
}
```

### Validation Rules
- Every table has source_file
- mermaid_er parses
- DC-I1-01 through DC-I1-03 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/intermediate/I1_er_diagram_agent.md`
- Blueprint: `eval_blueprints/I/I1_blueprint.md`
- Skill: `skills/intermediate/I1_er_diagram.skill.md`
