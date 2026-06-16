# Eval Blueprint: D3 — CI Pipeline Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
45 minutes

## Agent Spec
`agents/infra_devops/D3_ci_pipeline_agent.md`

## Prerequisites
Depends on: B3, I5

## Execution Steps

1. Read agent spec: `agents/infra_devops/D3_ci_pipeline_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/D3/ci_manifest.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Workflow YAML
- [ ] Cache/matrix
- [ ] Green run proof
- [ ] Failure mode demo

## Success Criteria
- [ ] pass_proof.exit_code == 0
- [ ] failure_demo documents expected fail
- [ ] DC-D3-01 through DC-D3-02 pass

## Failure Conditions
- WORKFLOW_INVALID
- PIPELINE_FAILED
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
