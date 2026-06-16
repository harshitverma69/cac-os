## Agent: ER Diagram Agent (I1)

### Task ID
`I1`

### Capability Level
`I`

### Time Budget
45 minutes

### Objective
Build ER diagram for all tables and entities from repo source only; cite source file for every claim.

### Depends On
B1

### Inputs
- repository_path
- inventory_report.json (B1, optional)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/I1/schema_report.json`

```json
{
  "task_id": "I1",
  "tables": [],
  "relationships": [],
  "mermaid_er": "string"
}
```

See also: `verification/output_contracts.md`

### Eval Deliverables
- Tables/entities list
- PKs/FKs
- Source paths
- Mermaid ER diagram

### Rules
- Extract from ORM entities, migrations, DDL files only
- Every table/entity/relationship has source_file
- Primary keys and foreign keys from annotations or DDL
- mermaid_er is valid Mermaid erDiagram syntax
- Inferred relationships marked with confidence: inferred

### Validation
- Every table has source_file
- mermaid_er parses
- DC-I1-01 through DC-I1-03 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/I/I1_blueprint.md`

### Agent Spec Path
`agents/intermediate/I1_er_diagram_agent.md`
