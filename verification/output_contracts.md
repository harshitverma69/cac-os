# Output Contracts

> Strict JSON schemas for PML/OCL eval tasks (24 total). See each `agents/**/*_agent.md` for task-specific schema.

## Common Envelope

```json
{
  "task_id": "string",
  "level": "B|I|A|D",
  "generated_at": "ISO-8601 UTC",
  "scan_complete": true,
  "warnings": []
}
```

## Proof Object (build/run tasks)

```json
{
  "command": "string",
  "exit_code": 0,
  "stdout_hash": "sha256 optional",
  "stderr_hash": "sha256 optional"
}
```

## Verification Log (I3, I6, A5)

```json
{
  "agent_suggested": ["string"],
  "manually_verified": ["string"],
  "uncertain": ["string"]
}
```

---

## Task → Output File Map

| Task | Output File | Key Proof Fields |
|------|-------------|------------------|
| B1 | inventory_report.json | files_scanned, artifacts |
| B2 | api_map_report.json | endpoints, mapping |
| B3 | test_discovery_report.json | framework, commands, command_result |
| B4 | greenfield_manifest.json | tests, run_proof |
| B5 | greenfield_manifest.json | tests, run_proof |
| B6 | greenfield_manifest.json | tests, missing_file_proof |
| I1 | schema_report.json | tables, mermaid_er |
| I2 | flow_trace_report.json | steps, sequence_diagram_mermaid |
| I3 | change_report.json | test_result, verification_log |
| I4 | polyglot_manifest.json | fastapi_service, node_client |
| I5 | docker_manifest.json | build_proof, health_check |
| I6 | bug_fix_report.json | root_cause, verification |
| A1 | worktree_plan.json | worktrees, merge_order |
| A2 | worktree_execution_report.json | test_result, conflicts |
| A3 | fraud_system_manifest.json | tests.integration |
| A4 | modernization_report.json | first_step, verification |
| A5 | code_review_report.json | issues[] |
| A6 | performance_report.json | baseline, after, behavior_proof |
| D1 | terraform_manifest.json | validate_proof, plan_proof |
| D2 | compose_manifest.json | test_run, teardown |
| D3 | ci_manifest.json | pass_proof, failure_demo |
| D4 | k8s_manifest.json | dry_run_proof, curl_proof |
| D5 | bootstrap_manifest.json | bootstrap_proof, test_proof |
| D6 | observability_manifest.json | dashboard_panel |

Full schemas inline in each agent spec under `agents/`.

## Run Manifest

```json
{
  "run_id": "uuid",
  "eval_source": "core/eval_source.md",
  "repository_path": "string",
  "tasks": [{"task_id": "string", "status": "complete|failed|skipped", "output_path": "string", "agent_spec": "agents/.../X_agent.md"}]
}
```
