## Skill: Polyglot Fraud System Agent

### Task ID
`A3`

### Level
`ADVANCED`

### Objective
Build mini fraud-score system: FastAPI ingestion, Node.js worker, Rust scoring engine with tests and README.

### Depends On
- B4
- B5
- B6
- I4

### Input Contract
```json
{
  "output_dir": "required"
}
```

### Execution Steps (DETERMINISTIC ONLY)
- Read agent spec: `agents/advanced/A3_polyglot_fraud_system_agent.md`
- Apply deterministic rules from `core/execution_rules.md`
- Write structured JSON to `generated_projects/{run_id}/A3/output.json`
- Validate output against Output Contract
- Run `make skill-done RUN_ID={run_id} SKILL=A3` to open the report UI

### Output Contract (STRICT JSON)
```json
{
  "task_id": "A3",
  "fastapi": {
    "path": "",
    "endpoint": "POST /transactions"
  },
  "node_worker": {
    "path": "",
    "process": "worker"
  },
  "rust_engine": {
    "path": "",
    "type": "cli|library",
    "binary": ""
  },
  "data_contract": {
    "transaction": {},
    "risk_score": {}
  },
  "tests": {
    "rust_unit": {
      "exit_code": 0
    },
    "integration": {
      "exit_code": 0
    }
  },
  "run_order": []
}
```

### Validation Rules
- All 3 components build
- integration test passes
- DC-A3-01 through DC-A3-02 pass

### Failure Conditions
- BUILD_FAILED
- INTEGRATION_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Sources
- Agent: `agents/advanced/A3_polyglot_fraud_system_agent.md`
- Blueprint: `eval_blueprints/A/A3_blueprint.md`
- Skill: `skills/advanced/A3_polyglot_fraud_system.skill.md`
