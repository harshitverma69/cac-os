# Eval Blueprint: I1 — ER Diagram Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
45 minutes

## Agent Spec
`agents/intermediate/I1_er_diagram_agent.md`

## Prerequisites
Depends on: B1

## Execution Steps

1. Read agent spec: `agents/intermediate/I1_er_diagram_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/I1/schema_report.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Tables/entities list
- [ ] PKs/FKs
- [ ] Source paths
- [ ] Mermaid ER diagram

## Success Criteria
- [ ] Every table has source_file
- [ ] mermaid_er parses
- [ ] DC-I1-01 through DC-I1-03 pass

## Failure Conditions
- INPUT_CONTRACT_VIOLATION
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
