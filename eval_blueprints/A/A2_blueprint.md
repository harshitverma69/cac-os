# Eval Blueprint: A2 — Parallel Worktrees Execute Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
90 minutes

## Agent Spec
`agents/advanced/A2_parallel_worktrees_execute_agent.md`

## Prerequisites
Depends on: A1

## Execution Steps

1. Read agent spec: `agents/advanced/A2_parallel_worktrees_execute_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/A2/worktree_execution_report.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Worktree commands
- [ ] Branch names
- [ ] Lane outputs
- [ ] Merge steps
- [ ] Test result
- [ ] Conflicts

## Success Criteria
- [ ] 2 worktrees created
- [ ] test_result.exit_code == 0
- [ ] DC-A2-01 through DC-A2-02 pass

## Failure Conditions
- WORKTREE_CREATE_FAILED
- MERGE_CONFLICT_UNRESOLVED
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
