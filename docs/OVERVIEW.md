# CAC-OS Overview

## Problem

Coding agents can do far more than most teams use them for — repo understanding, multi-language builds, parallel worktrees, infra artifacts. The PML/OCL eval document lists **24 concrete capabilities** engineers should be able to demonstrate.

CAC-OS turns that eval into a **repeatable, deterministic system** that Cursor (or any engineer) can follow without inventing structure each time.

## Design Principles

1. **Markdown agent specs, not runtime agents** — Each task is an `*_agent.md` file with strict JSON output contracts.
2. **Deterministic only** — Rules DT-01..DT-10 in `core/execution_rules.md`; no LLM logic in outputs.
3. **DAG execution** — Tasks depend on each other acyclically; parallel lanes where safe.
4. **Proof over prose** — Build/run tasks require `exit_code` proof fields, not claims.
5. **Testable outputs** — Golden examples in `generated_projects/_golden/`; validator in `scripts/cac_os.py`.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PML/OCL Eval Document                     │
│              (24 tasks: B1-B6, I1-I6, A1-A6, D1-D6)          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      CAC-OS Core Layer                       │
│  capability_registry │ execution_rules │ validation_matrix   │
│  self_eval_checklist │ eval_source                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
   agents/*_agent.md  eval_blueprints/  execution_models/
          │                │                │
          └────────────────┼────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   verification/ layer                        │
│         output_contracts.md │ deterministic_checks.md        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              generated_projects/{run_id}/                    │
│         Strict JSON artifacts + manifest.json                │
└─────────────────────────────────────────────────────────────┘
```

## How Cursor Operates CAC-OS

1. **Route** — `scripts/cac_os.py route --intent <name>` or read `execution_models/task_router.md`
2. **Read spec** — Open `agents/{level}/{ID}_{slug}_agent.md`
3. **Load upstream** — Read JSON from prior tasks in the run folder
4. **Execute** — Apply deterministic rules; produce code/files if greenfield/infra task
5. **Emit JSON** — Write to `generated_projects/{run_id}/{ID}/{output_file}`
6. **Validate** — `scripts/cac_os.py validate-run <run_dir>`

## Task Levels

### B — Repo Reader and Simple Builder (B1–B6)

Understand unfamiliar repos; discover tests; build FastAPI, Node, and Rust from scratch.

### I — Repo Operator and Polyglot Builder (I1–I6)

ER diagrams, flow traces, safe diffs, polyglot pairs, Docker, bug fixes with proof.

### A — Parallel Agent Operator (A1–A6)

Worktree planning/execution, fraud mini-system, modernization with first step, adversarial review, measured perf improvement.

### D — Infra and DevOps (D1–D6)

Terraform, docker-compose E2E, CI pipelines, Kubernetes local deploy, bootstrap from clone, Prometheus/Grafana.

## Parallel Execution

Independent tasks can run in parallel (see `execution_models/parallel_execution_model.md`):

- **Wave 0:** B1, B3, B4, B6, A1, A5, A6, D1, I5 (no shared deps)
- **Post-B1:** B2 and I1 in parallel
- **Post-I5:** D2, D4, D6 in parallel

## Integration with RepoLens

RepoLens provides **static analysis** for B1, B2, I1, I2, I6 (diagnosis). CAC-OS defines the **eval contract** and proof requirements. See [repolens_bridge.md](repolens_bridge.md).

## File Naming Convention

Agent specs live under `agents/` with suffix `_agent.md`:

```
agents/basics/B1_repo_artifact_inventory_agent.md
agents/intermediate/I5_dockerize_agent.md
agents/advanced/A3_polyglot_fraud_system_agent.md
agents/infra_devops/D1_terraform_plan_agent.md
```

Machine-readable registry: `scripts/task_registry.json`
