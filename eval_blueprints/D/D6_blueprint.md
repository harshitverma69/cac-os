# Eval Blueprint: D6 — Observability Bolt-On Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
60 minutes

## Agent Spec
`agents/infra_devops/D6_observability_bolt_on_agent.md`

## Prerequisites
Depends on: I5

## Execution Steps

1. Read agent spec: `agents/infra_devops/D6_observability_bolt_on_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/D6/observability_manifest.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Logging/metrics diff
- [ ] Prometheus/Grafana compose
- [ ] Load script
- [ ] Dashboard panel proof
- [ ] README

## Success Criteria
- [ ] /metrics returns prometheus format
- [ ] dashboard_panel has data
- [ ] DC-D6-01 through DC-D6-02 pass

## Failure Conditions
- METRICS_FAILED
- DASHBOARD_NO_DATA
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
