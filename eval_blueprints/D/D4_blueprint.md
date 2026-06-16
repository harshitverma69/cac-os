# Eval Blueprint: D4 — Kubernetes Manifests Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
60 minutes

## Agent Spec
`agents/infra_devops/D4_kubernetes_manifests_agent.md`

## Prerequisites
Depends on: I5

## Execution Steps

1. Read agent spec: `agents/infra_devops/D4_kubernetes_manifests_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/D4/k8s_manifest.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Manifest YAML
- [ ] Dry-run output
- [ ] kubectl apply
- [ ] curl proof
- [ ] README

## Success Criteria
- [ ] dry_run_proof.exit_code == 0
- [ ] curl_proof.response_status == 200
- [ ] DC-D4-01 through DC-D4-02 pass

## Failure Conditions
- VALIDATION_FAILED
- APPLY_FAILED
- CURL_FAILED
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
