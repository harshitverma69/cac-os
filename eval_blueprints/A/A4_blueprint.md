# Eval Blueprint: A4 — Modernization Executable Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
90 minutes

## Agent Spec
`agents/advanced/A4_modernization_executable_agent.md`

## Prerequisites
Depends on: B1, B3

## Execution Steps

1. Read agent spec: `agents/advanced/A4_modernization_executable_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/A4/modernization_report.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Findings with evidence
- [ ] Prioritized plan
- [ ] First step implemented
- [ ] Verification
- [ ] Rollback

## Success Criteria
- [ ] first_step.files_changed non-empty
- [ ] verification.exit_code == 0
- [ ] DC-A4-01 through DC-A4-02 pass

## Failure Conditions
- NO_FINDINGS
- IMPLEMENTATION_FAILED
- VERIFICATION_FAILED
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
