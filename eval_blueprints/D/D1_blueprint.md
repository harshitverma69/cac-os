# Eval Blueprint: D1 — Terraform Plan Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
60 minutes

## Agent Spec
`agents/infra_devops/D1_terraform_plan_agent.md`

## Prerequisites
Depends on: None

## Execution Steps

1. Read agent spec: `agents/infra_devops/D1_terraform_plan_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/D1/terraform_manifest.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] .tf files
- [ ] Provider/backend
- [ ] validate output
- [ ] plan output
- [ ] README

## Success Criteria
- [ ] validate_proof.exit_code == 0
- [ ] plan_proof.exit_code == 0
- [ ] DC-D1-01 through DC-D1-02 pass

## Failure Conditions
- VALIDATE_FAILED
- PLAN_FAILED
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
