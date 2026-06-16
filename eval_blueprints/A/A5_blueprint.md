# Eval Blueprint: A5 — Adversarial Code Review Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
60 minutes

## Agent Spec
`agents/advanced/A5_adversarial_code_review_agent.md`

## Prerequisites
Depends on: None

## Execution Steps

1. Read agent spec: `agents/advanced/A5_adversarial_code_review_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/A5/code_review_report.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Issue list
- [ ] Severity classification
- [ ] Suggested fixes
- [ ] Verification steps

## Success Criteria
- [ ] Every issue has category and severity
- [ ] blocking issues have suggested_fix
- [ ] DC-A5-01 through DC-A5-02 pass

## Failure Conditions
- INPUT_CONTRACT_VIOLATION: no diff
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
