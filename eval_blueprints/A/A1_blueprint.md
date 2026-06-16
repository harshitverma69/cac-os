# Eval Blueprint: A1 — Multi-Worktree Plan Agent

## Eval Source
PML/OCL Coding Agent Eval Document (May 2026)

## Time Budget
45 minutes

## Agent Spec
`agents/advanced/A1_multi_worktree_plan_agent.md`

## Prerequisites
Depends on: None

## Execution Steps

1. Read agent spec: `agents/advanced/A1_multi_worktree_plan_agent.md`
2. Load upstream artifacts from `generated_projects/{run_id}/`
3. Apply deterministic rules (DT-01 through DT-10 from `core/execution_rules.md`)
4. Write output to `generated_projects/{run_id}/A1/worktree_plan.json`
5. Run validation from agent spec and `core/validation_matrix.md`

## Deliverables Checklist
- [ ] Task decomposition
- [ ] Worktree names
- [ ] Agent prompts
- [ ] Constraints
- [ ] Merge order
- [ ] Conflict plan

## Success Criteria
- [ ] lanes have disjoint scopes
- [ ] merge_order defined
- [ ] DC-A1-01 through DC-A1-02 pass

## Failure Conditions
- INPUT_CONTRACT_VIOLATION
- OVERLAPPING_LANE_SCOPE
- OUTPUT_SCHEMA_VIOLATION

## Non-Goals
- No LLM reasoning in output JSON
- No runtime agent framework
- Prefer local/dry-run verification over cloud spend (Infra tasks)
