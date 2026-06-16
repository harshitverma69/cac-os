# Eval Blueprint: I6 — Bug Diagnosis Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
60 minutes

## Agent Spec
`agents/intermediate/I6_bug_diagnosis_agent.md`

## Prerequisites
Depends on: I2

## Execution Steps

1. Read agent spec: `agents/intermediate/I6_bug_diagnosis_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/I6/bug_fix_report.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Reproduction
- [ ] Root cause paths
- [ ] Minimal fix
- [ ] Verification result
- [ ] Agent vs verified

## Success Criteria
- [ ] root_cause.file_path exists
- [ ] verification.exit_code == 0
- [ ] DC-I6-01 through DC-I6-03 pass

## Failure Conditions
- REPRODUCTION_FAILED
- FIX_FAILED
- VERIFICATION_FAILED
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
