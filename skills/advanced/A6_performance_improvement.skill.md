## Skill: Performance Improvement Agent

### Task ID
`A6`

### Level
`ADVANCED`

### Objective
Find real performance bottleneck, make measurable minimal improvement, prove behavior unchanged.

### Depends On
None

### Input Contract
```json
{
  "service_path": "required",
  "benchmark_target": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/advanced/A6_performance_improvement_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/A6/output.json`
- Validate output against Output Contract
- Run `make skill-done RUN_ID={run_id} SKILL=A6` to open the report UI

### Output Contract (STRICT JSON)
```json
{
  "task_id": "A6",
  "baseline": {
    "method": "",
    "metric": "",
    "value": 0,
    "unit": ""
  },
  "profiling": {
    "approach": "",
    "bottleneck": "",
    "evidence": []
  },
  "change": {
    "files_changed": [],
    "description": ""
  },
  "after": {
    "method": "",
    "metric": "",
    "value": 0,
    "improvement_pct": 0
  },
  "behavior_proof": {
    "test_command": "",
    "exit_code": 0
  }
}
```

### Validation Rules
- after.value < baseline.value OR improvement_pct > 0
- behavior_proof.exit_code == 0
- DC-A6-01 through DC-A6-03 pass

### Failure Conditions
- BASELINE_FAILED
- NO_IMPROVEMENT
- BEHAVIOR_REGRESSION
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/advanced/A6_performance_improvement_agent.md`
- Blueprint: `eval_blueprints/A/A6_blueprint.md`
- Skill: `skills/advanced/A6_performance_improvement.skill.md`
