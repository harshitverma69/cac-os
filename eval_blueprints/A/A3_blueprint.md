# Eval Blueprint: A3 — Polyglot Fraud System Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
150 minutes

## Agent Spec
`agents/advanced/A3_polyglot_fraud_system_agent.md`

## Prerequisites
Depends on: B4, B5, B6, I4

## Execution Steps

1. Read agent spec: `agents/advanced/A3_polyglot_fraud_system_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/A3/fraud_system_manifest.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] FastAPI ingestion
- [ ] Node worker
- [ ] Rust scorer
- [ ] Data contract
- [ ] Tests
- [ ] Run order README

## Success Criteria
- [ ] All 3 components build
- [ ] integration test passes
- [ ] DC-A3-01 through DC-A3-02 pass

## Failure Conditions
- BUILD_FAILED
- INTEGRATION_FAILED
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
