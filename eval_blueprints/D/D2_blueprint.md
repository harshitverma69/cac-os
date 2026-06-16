# Eval Blueprint: D2 — Docker Compose Stack Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
90 minutes

## Agent Spec
`agents/infra_devops/D2_docker_compose_stack_agent.md`

## Prerequisites
Depends on: I5

## Execution Steps

1. Read agent spec: `agents/infra_devops/D2_docker_compose_stack_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/D2/compose_manifest.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] compose.yml
- [ ] Dockerfiles
- [ ] Seed script
- [ ] E2E test output
- [ ] Logs
- [ ] Teardown/re-up

## Success Criteria
- [ ] test_run.exit_code == 0
- [ ] reup_proof.exit_code == 0
- [ ] DC-D2-01 through DC-D2-02 pass

## Failure Conditions
- COMPOSE_UP_FAILED
- E2E_TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
