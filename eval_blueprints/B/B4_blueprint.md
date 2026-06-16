# Eval Blueprint: B4 — FastAPI Greenfield Service Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
60 minutes

## Agent Spec
`agents/basics/B4_fastapi_greenfield_agent.md`

## Prerequisites
Depends on: None

## Execution Steps

1. Read agent spec: `agents/basics/B4_fastapi_greenfield_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/B4/greenfield_manifest.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] FastAPI app
- [ ] POST/GET endpoints
- [ ] Input validation
- [ ] 3+ tests
- [ ] README commands

## Success Criteria
- [ ] files_created includes main.py, requirements.txt, README.md, tests/
- [ ] tests.count >= 3
- [ ] run_proof.exit_code == 0
- [ ] DC-B4-01 through DC-B4-03 pass

## Failure Conditions
- INPUT_CONTRACT_VIOLATION
- BUILD_FAILED
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
