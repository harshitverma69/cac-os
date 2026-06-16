# Eval Blueprint: B1 — Repo Artifact Inventory Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
30 minutes

## Agent Spec
`agents/basics/B1_repo_artifact_inventory_agent.md`

## Prerequisites
Depends on: None

## Execution Steps

1. Read agent spec: `agents/basics/B1_repo_artifact_inventory_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/B1/inventory_report.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Total files scanned
- [ ] Major modules discovered
- [ ] Evidence file paths
- [ ] Known limitations

## Success Criteria
- [ ] files_scanned >= 1 for non-empty repositories
- [ ] Every artifact has non-empty file_path
- [ ] Major modules discovered with evidence paths
- [ ] DC-B1-01 through DC-B1-04 pass

## Failure Conditions
- INPUT_CONTRACT_VIOLATION: repository_path missing or not a directory
- ZERO_ARTIFACTS: source files exist but zero artifacts extracted
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
