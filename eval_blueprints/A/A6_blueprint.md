# Eval Blueprint: A6 — Performance Improvement Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
90 minutes

## Agent Spec
`agents/advanced/A6_performance_improvement_agent.md`

## Prerequisites
Depends on: None

## Execution Steps

1. Read agent spec: `agents/advanced/A6_performance_improvement_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/A6/performance_report.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Baseline numbers
- [ ] Profile results
- [ ] Bottleneck
- [ ] Targeted change
- [ ] After numbers
- [ ] Behavior proof

## Success Criteria
- [ ] after.value < baseline.value OR improvement_pct > 0
- [ ] behavior_proof.exit_code == 0
- [ ] DC-A6-01 through DC-A6-03 pass

## Failure Conditions
- BASELINE_FAILED
- NO_IMPROVEMENT
- BEHAVIOR_REGRESSION
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
