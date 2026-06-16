# CAC-OS — Coding Agent Capability OS

**CAC-OS** is a deterministic execution framework that converts coding-agent capabilities into Markdown agent specs, eval blueprints, validation plans, and structured JSON outputs — **without runtime AI agents**.

It is aligned with the **PML/OCL Coding Agent Eval Document** (May 2026): 24 tasks covering repo reading, greenfield builds, polyglot systems, parallel worktrees, and infra/DevOps.

## What This Is

| Component | Purpose |
|-----------|---------|
| `agents/**/*_agent.md` | Executable task specs (inputs, outputs, rules, validation) |
| `eval_blueprints/` | Step-by-step eval runbooks per task |
| `core/` | Registry, execution rules, validation matrix, self-eval checklist |
| `execution_models/` | Task router, dependency DAG, parallel lanes |
| `verification/` | JSON output contracts + deterministic checks |
| `generated_projects/_golden/` | Reference output examples for all 24 tasks |
| `scripts/cac_os.py` | Deterministic validator and task router (no LLM) |

## What This Is Not

- Not a runtime agent framework
- Not an LLM reasoning system
- Not a UI or dashboard
- Not automatic code execution (Cursor or you execute; CAC-OS defines *how*)

## Quick Start

```bash
cd cac-os

# Validate entire registry (specs + blueprints + golden examples + DAG)
make validate

# List all 24 tasks
make list

# Plan an eval run
make route INTENT=trace_flow

# Plan full eval
make route INTENT=full_eval
```

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/OVERVIEW.md](docs/OVERVIEW.md) | Architecture and how Cursor uses CAC-OS |
| [docs/STATUS.md](docs/STATUS.md) | What's done vs what you execute live |
| [core/self_eval_checklist.md](core/self_eval_checklist.md) | PML/OCL self-eval yes/no checklist |
| [core/eval_source.md](core/eval_source.md) | Eval document sources |
| [docs/repolens_bridge.md](docs/repolens_bridge.md) | RepoLens agent mapping |
| [core/capability_registry.md](core/capability_registry.md) | All 24 tasks + dependencies |

## Task Coverage

| Level | Tasks | Coverage |
|-------|-------|----------|
| B — Basics | B1–B6 | 100% |
| I — Intermediate | I1–I6 | 100% |
| A — Advanced | A1–A6 | 100% |
| D — Infra/DevOps | D1–D6 | 100% |

## Eval Sources

- [PML Eval](https://docs.google.com/document/d/1VurgqAe_qZlMieK8pA4S2yJjWBd7cnoO8cuvh4zmNZs/edit)
- [OCL Eval](https://docs.google.com/document/d/1Y23tu2ePPexkBhh_G0RCK1fNio_NQ3EZuTbgWa_UyPA/edit)

## Running an Eval Task (Cursor Workflow)

1. Pick a task from `core/self_eval_checklist.md`
2. Read `agents/{level}/{ID}_{slug}_agent.md`
3. Follow `eval_blueprints/{level}/{ID}_blueprint.md`
4. Write output JSON to `generated_projects/{run_id}/{ID}/`
5. Validate with `make validate-run RUN_DIR=generated_projects/{run_id}`

## Related Projects

- **RepoLens** (`../repolens/`) — Static analysis agents for repo inventory, API map, flow trace. See [docs/repolens_bridge.md](docs/repolens_bridge.md).
