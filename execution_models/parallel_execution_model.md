# Parallel Execution Model

> Fork-join for PML/OCL eval tasks.

## Lane 1: Post-Discovery (after B1)

| Tasks | B2 API Map, I1 ER Diagram |
|-------|---------------------------|
| Shared read | B1/inventory_report.json |
| Exclusive write | B2/api_map_report.json, I1/schema_report.json |

## Lane 2: Greenfield Builds (Wave 0)

| Tasks | B4 FastAPI, B6 Rust CLI |
|-------|-------------------------|
| Constraint | Different output_dir per task |

## Lane 3: Worktree Execution (A1 → A2)

| Property | Value |
|----------|-------|
| Plan | A1 worktree_plan.json |
| Execute | A2 creates N worktrees per plan |
| Merge | Sequential per A1 merge_order |

## Lane 4: Infra Post-Docker (after I5)

| Tasks | D2 Compose, D4 K8s, D6 Observability |
|-------|--------------------------------------|
| Constraint | Different manifest outputs |

## Merge Strategy

`manifest_append` — collect task outputs into `generated_projects/{run_id}/manifest.json`

## Constraints

| Rule | Description |
|------|-------------|
| PE-01 | Max 4 parallel lanes |
| PE-02 | No parallel writes to same output path |
| PE-03 | A2 must complete A1 plan before execution |
| PE-04 | Proof tasks (B4–B6, D1–D6) record exit_code in manifest |
