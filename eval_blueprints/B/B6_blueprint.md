# Eval Blueprint: B6 — Rust Greenfield CLI Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
60 minutes

## Agent Spec
`agents/basics/B6_rust_greenfield_agent.md`

## Prerequisites
Depends on: None

## Execution Steps

1. Read agent spec: `agents/basics/B6_rust_greenfield_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/B6/greenfield_manifest.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Cargo project
- [ ] CLI file path arg
- [ ] INFO/WARN/ERROR counts
- [ ] Missing file handling
- [ ] 3+ tests

## Success Criteria
- [ ] tests.count >= 3
- [ ] missing_file_proof exit graceful
- [ ] DC-B6-01 through DC-B6-03 pass

## Failure Conditions
- INPUT_CONTRACT_VIOLATION
- BUILD_FAILED
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
