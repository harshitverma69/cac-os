# CAC-OS Validation Matrix

> Cross-task validation for 24 PML/OCL eval tasks.

## Coverage

| Level | Tasks | Validation Rules |
|-------|-------|------------------|
| B | B1–B6 | 6/6 |
| I | I1–I6 | 6/6 |
| A | A1–A6 | 6/6 |
| D | D1–D6 | 6/6 |
| **Total** | **24/24** | **100%** |

---

## L1: Schema Validation (All Tasks)

| Check ID | Rule | Fail Code |
|----------|------|-----------|
| SCH-01 | Output is valid JSON | `OUTPUT_SCHEMA_VIOLATION` |
| SCH-02 | Required keys per `verification/output_contracts.md` | `OUTPUT_SCHEMA_VIOLATION` |
| SCH-03 | Proof fields include exit_code where required | `OUTPUT_SCHEMA_VIOLATION` |
| SCH-04 | Enum fields match allowed values | `OUTPUT_SCHEMA_VIOLATION` |
| SCH-05 | No prose-only outputs (must be structured JSON) | `OUTPUT_SCHEMA_VIOLATION` |

---

## L2: Per-Task Validation

| Task | Key Rules |
|------|-----------|
| B1 | files_scanned >= 1; every artifact has file_path |
| B2 | Unique (method, route); handler + source_file required |
| B3 | framework + test command; command_result if executed |
| B4 | 3+ tests; run_proof.exit_code == 0; 3 endpoints |
| B5 | 3+ tests; mirrors B4 contract |
| B6 | 3+ cargo tests; missing file graceful |
| I1 | Every table has source_file; valid mermaid_er |
| I2 | Entry point first step; sequence diagram present |
| I3 | verification_log splits agent vs manual; tests pass |
| I4 | Both FastAPI + Node components; integration passes |
| I5 | docker build + health check 200 |
| I6 | root_cause file_path; verification after fix |
| A1 | Disjoint lane scopes; merge_order defined |
| A2 | 2 worktrees; test after merge |
| A3 | 3 components + integration test |
| A4 | first_step implemented; verification passes |
| A5 | Issues have category, severity, suggested_fix |
| A6 | after < baseline OR improvement_pct > 0; tests pass |
| D1 | terraform validate + plan pass |
| D2 | E2E test green; teardown + re-up |
| D3 | Pipeline green + failure demo documented |
| D4 | dry-run pass; curl 200 on local cluster |
| D5 | Single bootstrap command; tests pass |
| D6 | /metrics works; dashboard has data |

---

## L3: Cross-Task Consistency

| Check ID | Rule |
|----------|------|
| XTC-01 | B2 routes traceable to B1 artifacts or warnings |
| XTC-02 | I2 entry_point exists in B2 (if endpoint type) |
| XTC-03 | I6 root_cause aligns with I2 steps (if I2 available) |
| XTC-04 | B5 mirrors B4 endpoint contract |
| XTC-05 | I4 uses B4/B5 patterns |
| XTC-06 | A3 data_contract consistent with I4 |
| XTC-07 | D2/D3/D4/D6 build on I5 docker patterns |
| XTC-08 | D5 test command matches B3 discovery |
| XTC-09 | A2 execution matches A1 plan worktrees |
| XTC-10 | I3/I6 verification_log format consistent |

---

## L4: Run-Wide

| Check ID | Rule |
|----------|------|
| RW-01 | manifest.json lists all requested tasks |
| RW-02 | COMPLETE tasks have output files |
| RW-03 | Proof exit_codes recorded for build/run tasks |
| RW-04 | Time budget noted per task (informational) |

---

## Proof Requirement Matrix

Tasks requiring **executable proof** (not plan-only):

| Task | Required Proof |
|------|----------------|
| B3 | test command result (optional if discovery-only) |
| B4, B5, B6 | run_proof + test exit_code 0 |
| I3, I6 | test/verification exit_code 0 |
| I4, I5 | integration/health check |
| A2, A3, A4 | test/build exit_code 0 |
| A6 | baseline + after measurements |
| D1–D6 | validate/plan/apply/curl/E2E as specified |
