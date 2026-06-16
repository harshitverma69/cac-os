## Agent: Performance Improvement Agent (A6)

### Task ID
`A6`

### Capability Level
`A`

### Time Budget
90 minutes

### Objective
Find real performance bottleneck, make measurable minimal improvement, prove behavior unchanged.

### Depends On
None

### Inputs
- service_path (absolute path)
- benchmark_target (string)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/A6/performance_report.json`

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

See also: `verification/output_contracts.md`

### Eval Deliverables
- Baseline numbers
- Profile results
- Bottleneck
- Targeted change
- After numbers
- Behavior proof

### Rules
- Baseline measurement with method and numeric value
- Profiling: cProfile, hyperfine, or cargo bench
- Change must be minimal and targeted
- After measurement uses same method as baseline
- behavior_proof: tests pass unchanged

### Validation
- after.value < baseline.value OR improvement_pct > 0
- behavior_proof.exit_code == 0
- DC-A6-01 through DC-A6-03 pass

### Failure Conditions
- BASELINE_FAILED
- NO_IMPROVEMENT
- BEHAVIOR_REGRESSION
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/A/A6_blueprint.md`

### Agent Spec Path
`agents/advanced/A6_performance_improvement_agent.md`
