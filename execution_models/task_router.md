# Task Router

> Maps intent to PML/OCL eval task DAG.

## Intent → Task Mapping

| Intent | Tasks |
|--------|-------|
| `discover` | B1 |
| `map_apis` | B1 → B2 |
| `find_tests` | B3 |
| `build_fastapi` | B4 |
| `build_node` | B4 → B5 |
| `build_rust` | B6 |
| `er_diagram` | B1 → I1 |
| `trace_flow` | B1 → B2 → I2 |
| `safe_change` | B3 → I3 |
| `polyglot_pair` | B4 → B5 → I4 |
| `dockerize` | I5 |
| `fix_bug` | B2 → I2 → I6 |
| `worktree_plan` | A1 |
| `worktree_execute` | A1 → A2 |
| `fraud_system` | B4 → B5 → B6 → I4 → A3 |
| `modernize` | B1 → B3 → A4 |
| `review_pr` | A5 |
| `perf_improve` | A6 |
| `terraform` | D1 |
| `compose_stack` | I5 → D2 |
| `ci_pipeline` | B3 → I5 → D3 |
| `kubernetes` | I5 → D4 |
| `bootstrap` | B3 → D5 |
| `observability` | I5 → D6 |
| `full_eval` | All 24 tasks in DAG order |

## Routing Plan Output

```json
{
  "run_id": "uuid",
  "intent": "trace_flow",
  "tasks": ["B1", "B2", "I2"],
  "execution_order": ["B1", "B2", "I2"],
  "parallel_groups": [["B4", "B6"]],
  "eval_source": "core/eval_source.md"
}
```

Agent specs: `agents/{level}/*_agent.md`
