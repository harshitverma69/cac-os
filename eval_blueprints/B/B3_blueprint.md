# Eval Blueprint: B3 — Test Discovery Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
15 minutes

## Agent Spec
`agents/basics/B3_test_discovery_agent.md`

## Prerequisites
Depends on: None

## Execution Steps

1. Read agent spec: `agents/basics/B3_test_discovery_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/B3/test_discovery_report.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Test framework and config
- [ ] Relevant test files
- [ ] Exact commands
- [ ] Command result
- [ ] Failure interpretation

## Success Criteria
- [ ] framework is non-empty for repos with tests
- [ ] At least one test command defined
- [ ] test_files paths exist on disk
- [ ] DC-B3-01 through DC-B3-03 pass

## Failure Conditions
- INPUT_CONTRACT_VIOLATION
- ZERO_ARTIFACTS: no test framework detected
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
