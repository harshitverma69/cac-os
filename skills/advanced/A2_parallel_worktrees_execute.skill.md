## Skill: Parallel Worktrees Execute Agent

### Task ID
`A2`

### Level
`ADVANCED`

### Objective
Create two parallel worktrees, make independent changes, reconcile cleanly with test proof.

### Depends On
- A1

### Input Contract
```json
{
  "repository_path": "required",
  "worktree_plan.json": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/advanced/A2_parallel_worktrees_execute_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/A2/output.json`
- Validate output against Output Contract

### Output Contract (STRICT JSON)
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

### Validation Rules
- 2 worktrees created
- test_result.exit_code == 0
- DC-A2-01 through DC-A2-02 pass

### Failure Conditions
- WORKTREE_CREATE_FAILED
- MERGE_CONFLICT_UNRESOLVED
- TEST_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/advanced/A2_parallel_worktrees_execute_agent.md`
- Blueprint: `eval_blueprints/A/A2_blueprint.md`
- Skill: `skills/advanced/A2_parallel_worktrees_execute.skill.md`
