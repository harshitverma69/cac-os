# CAC-OS Execution Rules

> Deterministic execution framework. No LLM reasoning. No runtime agents.

## 1. Execution Model

All work follows a **DAG-based execution model**. Tasks are nodes; dependencies are directed edges. Cycles are forbidden.

### 1.1 Task Selection

1. Read `core/capability_registry.md` and `core/eval_source.md` for the full task list.
2. Read `execution_models/task_router.md` to resolve which tasks apply to the current request.
3. Open the agent spec at `agents/{level}/{task_id}_{slug}_agent.md`.
4. Compute the transitive closure of dependencies for requested tasks.
5. Topologically sort the closure. Tie-break by task ID ascending (B1 < B2 < … < D6).

### 1.2 Execution Order

```
PHASE 0: Resolve inputs (repository_path, endpoint_id?, diff_base?, error_context?)
PHASE 1: Execute all tasks with in-degree 0 (typically B1)
PHASE 2: Execute tasks whose dependencies are all COMPLETE
PHASE 3: Repeat until all requested tasks COMPLETE or FAIL
PHASE 4: Run cross-task validation (validation_matrix.md)
PHASE 5: Emit final manifest to generated_projects/{run_id}/
```

### 1.3 Parallel Execution

Parallel execution is allowed **only** when:

- Tasks share no dependency edge (direct or transitive).
- Tasks do not write the same output artifact.
- Tasks are marked `parallel_safe: true` in the registry.

Canonical parallel lanes (from A1):

| Lane | Tasks | Shared Input |
|------|-------|--------------|
| Lane A | B1 | repository_path |
| Lane B | B2 | B1.inventory_report.json |
| Lane C | B3 | B1.inventory_report.json |
| Lane D | B4..B7 | endpoint-scoped, after B2/B3 |

Merge rule: collect lane outputs into `generated_projects/{run_id}/manifest.json` keyed by task_id.

---

## 2. Input Contract Rules

Every task MUST receive inputs matching its agent spec `### Inputs` section.

| Input | Type | Required | Source |
|-------|------|----------|--------|
| `repository_path` | string (absolute path) | always | caller |
| `endpoint_id` | string (`METHOD:/path`) | endpoint-scoped tasks | caller |
| `inventory_report` | JSON file ref | B2+ | B1 output |
| `api_map_report` | JSON file ref | B4+ | B2 output |
| `schema_report` | JSON file ref | B6+ | B3 output |
| `flow_trace_report` | JSON file ref | B5, B7+ | B4 output |
| `error_context` | object | B5, I2 | caller (exception, stack_trace, logs) |
| `changed_files` | string[] | D3 | git diff |

Missing required input → **FAIL** with code `INPUT_CONTRACT_VIOLATION`.

---

## 3. Output Contract Rules

Every task MUST produce output matching its agent spec `### Outputs (STRICT JSON)` section.

### 3.1 Output Location

```
generated_projects/{run_id}/{task_id}/{artifact_name}.json
```

### 3.2 Output Constraints

- JSON only. No markdown, no prose, no explanation fields.
- All paths must be relative to `repository_path` or absolute with evidence.
- All counts must be integers derived from enumeration, not estimation.
- Confidence scores (where present) must be one of: `0.0`, `0.25`, `0.5`, `0.75`, `1.0`.
- Status fields must be one of: `verified`, `assumed`, `inferred`, `unknown`.

### 3.3 Partial Execution

When a source file fails to parse:

- Log warning in `warnings[]` array on the output object.
- Continue scanning remaining files.
- Set `scan_complete: false` if any file failed.
- Do NOT fail the entire task unless zero artifacts were produced.

---

## 4. Deterministic Transformation Rules

| Rule ID | Description |
|---------|-------------|
| DT-01 | Extract only from parseable source files matching known extensions (.java, .py, .ts, .js) |
| DT-02 | HTTP routes resolved by static annotation/decorator inspection only |
| DT-03 | Entity/table names resolved by ORM annotation or DDL inspection only |
| DT-04 | Call chains resolved by import + method invocation graph, max depth 20 |
| DT-05 | No cross-repository inference |
| DT-06 | No runtime execution, profiling, or network calls |
| DT-07 | Duplicate endpoints deduplicated by `(method, normalized_path)` |
| DT-08 | File paths normalized to forward slashes, relative to repository root |
| DT-09 | Timestamps in ISO-8601 UTC, set once at task start |
| DT-10 | Sort all arrays by primary key ascending for reproducibility |

---

## 5. Failure Conditions

| Code | Condition | Action |
|------|-----------|--------|
| `INPUT_CONTRACT_VIOLATION` | Required input missing or malformed | FAIL task, halt dependents |
| `OUTPUT_SCHEMA_VIOLATION` | Output fails JSON schema check | FAIL task |
| `ZERO_ARTIFACTS` | Scan produced empty result set on non-empty repo | FAIL task |
| `DEPENDENCY_FAILED` | Upstream task FAILED | SKIP task, mark `skipped_dependency_failure` |
| `CYCLE_DETECTED` | Dependency graph has cycle | FAIL run immediately |
| `CROSS_TASK_INCONSISTENCY` | Validation matrix check failed | FAIL run after all tasks complete |

---

## 6. Cursor Operating Instructions

1. Read the `*_agent.md` spec for the target task under `agents/`.
2. Read upstream output JSON from `generated_projects/{run_id}/`.
3. Apply deterministic rules (DT-01 through DT-10).
4. Write output JSON to the prescribed path.
5. Run validation rules from the agent spec and `verification/deterministic_checks.md`.
6. Update run manifest with task status.

No improvisation. No natural-language reasoning in outputs.
