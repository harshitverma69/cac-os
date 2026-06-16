## Agent: Polyglot Fraud System Agent (A3)

### Task ID
`A3`

### Capability Level
`A`

### Time Budget
150 minutes

### Objective
Build mini fraud-score system: FastAPI ingestion, Node.js worker, Rust scoring engine with tests and README.

### Depends On
B4, B5, B6, I4

### Inputs
- output_dir (absolute path)

### Outputs (STRICT JSON)
Output file: `generated_projects/{run_id}/A3/fraud_system_manifest.json`

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

See also: `verification/output_contracts.md`

### Eval Deliverables
- FastAPI ingestion
- Node worker
- Rust scorer
- Data contract
- Tests
- Run order README

### Rules
- FastAPI accepts transactions POST
- Node worker polls or subscribes and forwards to Rust scorer
- Rust computes risk score from rules
- data_contract JSON schema shared across components
- Integration test covers at least one full path

### Validation
- All 3 components build
- integration test passes
- DC-A3-01 through DC-A3-02 pass

### Failure Conditions
- BUILD_FAILED
- INTEGRATION_FAILED
- OUTPUT_SCHEMA_VIOLATION

### Eval Blueprint
`eval_blueprints/A/A3_blueprint.md`

### Agent Spec Path
`agents/advanced/A3_polyglot_fraud_system_agent.md`
