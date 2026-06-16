# Eval Blueprint: I4 — Polyglot FastAPI Node Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
90 minutes

## Agent Spec
`agents/intermediate/I4_polyglot_fastapi_node_agent.md`

## Prerequisites
Depends on: B4, B5

## Execution Steps

1. Read agent spec: `agents/intermediate/I4_polyglot_fastapi_node_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/I4/polyglot_manifest.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] FastAPI /convert
- [ ] Node CLI client
- [ ] Validation
- [ ] Tests
- [ ] Two-terminal README

## Success Criteria
- [ ] Both components run
- [ ] Integration script passes
- [ ] DC-I4-01 through DC-I4-02 pass

## Failure Conditions
- BUILD_FAILED
- INTEGRATION_FAILED
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
