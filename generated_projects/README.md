# CAC-OS Run Outputs

This directory holds **execution outputs** from CAC-OS eval runs.

## Layout

```
generated_projects/
├── _golden/              # Reference JSON examples (one per task) — DO NOT DELETE
│   ├── manifest.json
│   ├── B1/inventory_report.json
│   ├── B2/api_map_report.json
│   └── … (24 tasks)
└── {run_id}/             # Your actual runs
    ├── manifest.json
    ├── B1/inventory_report.json
    └── …
```

## `_golden/`

Deterministic reference outputs showing the **expected JSON shape** for each of the 24 PML/OCL eval tasks. Used by:

```bash
make validate
python3 scripts/cac_os.py validate-registry
```

These are **not** from live builds — they are schema/reference examples. When you complete a real eval task, your output should match the same keys and proof fields.

## `{run_id}/`

Create a new run folder per eval session:

```bash
export RUN_ID="run-$(date +%Y%m%d-%H%M%S)"
mkdir -p "generated_projects/$RUN_ID"

# Plan tasks
python3 scripts/cac_os.py route --intent trace_flow --run-id "$RUN_ID"

# After completing tasks, validate
python3 scripts/cac_os.py validate-run "generated_projects/$RUN_ID"
```

## Proof Fields

Build/run tasks (B4–B6, I3–I6, A2–A4, A6, D1–D6) must include proof objects with `exit_code`. See `verification/output_contracts.md`.
