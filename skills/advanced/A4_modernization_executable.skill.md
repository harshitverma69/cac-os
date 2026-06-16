## Skill: Modernization Executable Agent

### Task ID
`A4`

### Level
`ADVANCED`

### Objective
Analyze repo for modernization opportunities, prioritize, implement highest-value lowest-risk first step.

### Depends On
- B1
- B3

### Input Contract
```json
{
  "repository_path": "required",
  "inventory_report.json": "required",
  "test_discovery_report.json": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/advanced/A4_modernization_executable_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/A4/output.json`
- Validate output against Output Contract
- Run `make skill-done RUN_ID={run_id} SKILL=A4` to open the report UI

### Output Contract (STRICT JSON)
```json
{
  "task_id": "A4",
  "findings": [],
  "prioritized_plan": [],
  "first_step": {
    "action": "",
    "files_changed": [],
    "evidence": []
  },
  "verification": {
    "command": "",
    "exit_code": 0
  },
  "rollback_notes": []
}
```

### Validation Rules
- first_step.files_changed non-empty
- verification.exit_code == 0
- DC-A4-01 through DC-A4-02 pass

### Failure Conditions
- NO_FINDINGS
- IMPLEMENTATION_FAILED
- VERIFICATION_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/advanced/A4_modernization_executable_agent.md`
- Blueprint: `eval_blueprints/A/A4_blueprint.md`
- Skill: `skills/advanced/A4_modernization_executable.skill.md`
