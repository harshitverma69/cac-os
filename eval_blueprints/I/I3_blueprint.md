# Eval Blueprint: I3 — Safe Change Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
60 minutes

## Agent Spec
`agents/intermediate/I3_safe_change_agent.md`

## Prerequisites
Depends on: B3

## Execution Steps

1. Read agent spec: `agents/intermediate/I3_safe_change_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/I3/change_report.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Diff/branch
- [ ] Files changed
- [ ] Why these files
- [ ] Test result
- [ ] Risk
- [ ] Agent vs verified

## Success Criteria
- [ ] files_changed non-empty
- [ ] test_result.exit_code == 0
- [ ] verification_log populated
- [ ] DC-I3-01 through DC-I3-03 pass

## Failure Conditions
- INPUT_CONTRACT_VIOLATION
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
