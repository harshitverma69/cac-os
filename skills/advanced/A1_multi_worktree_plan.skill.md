## Skill: Multi-Worktree Plan Agent

### Task ID
`A1`

### Level
`ADVANCED`

### Objective
Split one feature/analysis task into parallel worktrees or agent sessions without merge chaos.

### Depends On
None

### Input Contract
```json
{
  "repository_path": "required",
  "task_description": "required",
  "lanes": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/advanced/A1_multi_worktree_plan_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/A1/output.json`
- Validate output against Output Contract

### Output Contract (STRICT JSON)
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

### Validation Rules
- lanes have disjoint scopes
- merge_order defined
- DC-A1-01 through DC-A1-02 pass

### Failure Conditions
- INPUT_CONTRACT_VIOLATION
- OVERLAPPING_LANE_SCOPE
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/advanced/A1_multi_worktree_plan_agent.md`
- Blueprint: `eval_blueprints/A/A1_blueprint.md`
- Skill: `skills/advanced/A1_multi_worktree_plan.skill.md`
