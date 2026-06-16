# Deterministic Checks

> Per-task checks for 24 PML/OCL eval tasks. Proof-bearing tasks require exit_code fields.

## Universal (DC-U01..U10)

| Check | Pass Condition |
|-------|----------------|
| DC-U01 | Valid JSON |
| DC-U02 | task_id matches |
| DC-U03 | generated_at ISO-8601 |
| DC-U04 | warnings is array |
| DC-U05 | file_path values exist on disk |
| DC-U06 | Proof exit_code present for build/run tasks |
| DC-U07 | No free-text-only output blobs |
| DC-U08 | Arrays sorted ascending where specified |
| DC-U09 | Enum values in allowed sets |
| DC-U10 | verification_log present where required (I3, I6) |

## Per-Task Summary

| Task | Checks |
|------|--------|
| B1 | DC-B1-01 files_scanned >= 1; DC-B1-02 artifact file_paths |
| B2 | DC-B2-01 unique routes; DC-B2-02 handler required |
| B3 | DC-B3-01 framework detected; DC-B3-02 commands executable |
| B4 | DC-B4-01 tests >= 3; DC-B4-02 run_proof exit 0 |
| B5 | DC-B5-01 mirrors B4 contract |
| B6 | DC-B6-01 tests >= 3; DC-B6-02 missing file graceful |
| I1 | DC-I1-01 source_file per table; DC-I1-02 mermaid valid |
| I2 | DC-I2-01 entry first; DC-I2-02 side_effects tagged |
| I3 | DC-I3-01 test pass; DC-I3-02 verification_log split |
| I4 | DC-I4-01 both components; DC-I4-02 integration pass |
| I5 | DC-I5-01 docker build; DC-I5-02 health 200 |
| I6 | DC-I6-01 root cause path; DC-I6-02 fix verified |
| A1 | DC-A1-01 disjoint lanes |
| A2 | DC-A2-01 merge + test pass |
| A3 | DC-A3-01 three components + integration |
| A4 | DC-A4-01 first step + verification |
| A5 | DC-A5-01 issues complete |
| A6 | DC-A6-01 measurable improvement |
| D1 | DC-D1-01 validate + plan |
| D2 | DC-D2-01 E2E green |
| D3 | DC-D3-01 pipeline green |
| D4 | DC-D4-01 curl proof |
| D5 | DC-D5-01 bootstrap + tests |
| D6 | DC-D6-01 metrics + dashboard data |

See `core/validation_matrix.md` for cross-task checks (XTC-*).
