# Eval Blueprint: I2 — Flow Trace Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
45 minutes

## Agent Spec
`agents/intermediate/I2_flow_trace_agent.md`

## Prerequisites
Depends on: B2

## Execution Steps

1. Read agent spec: `agents/intermediate/I2_flow_trace_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/I2/flow_trace_report.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Entry point
- [ ] Step-by-step path
- [ ] External deps
- [ ] Side effects
- [ ] Sequence diagram
- [ ] Uncertainties

## Success Criteria
- [ ] steps[0] is entry point
- [ ] All steps have file_path
- [ ] DC-I2-01 through DC-I2-04 pass

## Failure Conditions
- INPUT_CONTRACT_VIOLATION: entry_point not found
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
