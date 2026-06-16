## Agent: Multi-Worktree Plan Agent (A1)

### Task ID
`A1`

### Capability Level
`A`

### Time Budget
45 minutes

### Objective
Split one feature/analysis task into parallel worktrees or agent sessions without merge chaos.

### Depends On
None

### Inputs
- repository_path
- task_description (string)
- lanes (integer, default 2)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/A1/worktree_plan.json`

```json
{
  "task_id": "A1",
  "decomposition": [],
  "worktrees": [],
  "agent_prompts": {},
  "shared_constraints": [],
  "merge_order": [],
  "conflict_plan": [],
  "verification_plan": []
}
```

See also: `verification/output_contracts.md`

### Eval Deliverables
- Task decomposition
- Worktree names
- Agent prompts
- Constraints
- Merge order
- Conflict plan

### Rules
- Each lane has disjoint file ownership or feature boundary
- worktree names: wt-{lane_id}-{slug}
- agent_prompts keyed by lane_id
- merge_order is topological by dependency
- Conflict plan identifies shared files upfront

### Validation
- lanes have disjoint scopes
- merge_order defined
- DC-A1-01 through DC-A1-02 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION
- OVERLAPPING_LANE_SCOPE
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/A/A1_blueprint.md`

### Agent Spec Path
`agents/advanced/A1_multi_worktree_plan_agent.md`
