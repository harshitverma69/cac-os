## Agent: Parallel Worktrees Execute Agent (A2)

### Task ID
`A2`

### Capability Level
`A`

### Time Budget
90 minutes

### Objective
Create two parallel worktrees, make independent changes, reconcile cleanly with test proof.

### Depends On
A1

### Inputs
- repository_path
- worktree_plan.json (A1)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/A2/worktree_execution_report.json`

```json
{
  "task_id": "A2",
  "commands": [],
  "worktrees": [],
  "lane_outputs": {},
  "merge_steps": [],
  "test_result": {
    "command": "",
    "exit_code": 0
  },
  "conflicts": []
}
```

See also: `verification/output_contracts.md`

### Eval Deliverables
- Worktree commands
- Branch names
- Lane outputs
- Merge steps
- Test result
- Conflicts

### Rules
- Use git worktree add for isolation
- Record exact commands used
- lane_outputs: commit hash + files changed per lane
- Merge steps documented sequentially
- test_result after final merge

### Validation
- 2 worktrees created
- test_result.exit_code == 0
- DC-A2-01 through DC-A2-02 pass

### Failure Conditions
- WORKTREE_CREATE_FAILED
- MERGE_CONFLICT_UNRESOLVED
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/A/A2_blueprint.md`

### Agent Spec Path
`agents/advanced/A2_parallel_worktrees_execute_agent.md`
