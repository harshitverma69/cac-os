# Eval Blueprint: I5 — Dockerize Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
60 minutes

## Agent Spec
`agents/intermediate/I5_dockerize_agent.md`

## Prerequisites
Depends on: None

## Execution Steps

1. Read agent spec: `agents/intermediate/I5_dockerize_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/I5/docker_manifest.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Dockerfile
- [ ] Build proof
- [ ] Container run proof
- [ ] Health/curl proof
- [ ] README

## Success Criteria
- [ ] build_proof.exit_code == 0
- [ ] health_check.response_status == 200
- [ ] DC-I5-01 through DC-I5-02 pass

## Failure Conditions
- BUILD_FAILED
- RUN_FAILED
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
