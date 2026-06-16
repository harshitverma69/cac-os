# Eval Blueprint: B2 — API Endpoint Map Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
30 minutes

## Agent Spec
`agents/basics/B2_api_endpoint_map_agent.md`

## Prerequisites
Depends on: B1

## Execution Steps

1. Read agent spec: `agents/basics/B2_api_endpoint_map_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/B2/api_map_report.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] HTTP method
- [ ] Route
- [ ] Controller
- [ ] Handler method
- [ ] Source file path

## Success Criteria
- [ ] Endpoint count matches unique (method, route) pairs
- [ ] Every endpoint has handler_method and source_file
- [ ] DC-B2-01 through DC-B2-04 pass

## Failure Conditions
- INPUT_CONTRACT_VIOLATION
- ZERO_ARTIFACTS on known API repos
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
