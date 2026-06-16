# Eval Blueprint: D5 — Reproducible Dev Environment Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
45 minutes

## Agent Spec
`agents/infra_devops/D5_reproducible_dev_env_agent.md`

## Prerequisites
Depends on: B3

## Execution Steps

1. Read agent spec: `agents/infra_devops/D5_reproducible_dev_env_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/D5/bootstrap_manifest.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Bootstrap config
- [ ] Single command output
- [ ] Passing tests
- [ ] Implicit deps notes

## Success Criteria
- [ ] bootstrap_proof.exit_code == 0
- [ ] test_proof.exit_code == 0
- [ ] DC-D5-01 through DC-D5-02 pass

## Failure Conditions
- BOOTSTRAP_FAILED
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
