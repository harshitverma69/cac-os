# Self-Eval Checklist

> From PML/OCL Coding Agent Eval (May 2026). Motivation and skill journey — not a pass/fail gate.

Use this to track whether you can independently use coding agents for each capability. Map each row to a CAC-OS task spec under `agents/`.

## Quick Self-Eval

| Category | Question | CAC-OS Task | Self-Eval (yes / no) |
|----------|----------|-------------|----------------------|
| Repo discovery | Inspect an unfamiliar repo and produce class/service/module inventory in 30 min? | B1 | |
| Data model | Produce ER diagram from code/ORM/migrations in 45 min? | I1 | |
| API mapping | Map all API endpoints to handlers/controllers in 30 min? | B2 | |
| Flow tracing | Trace one endpoint/event/cron end-to-end in 45 min? | I2 | |
| Testing | Find test framework, files, and exact test command in 30 min? | B3 | |
| Greenfield build | Build small FastAPI service with tests in 60 min? | B4 | |
| Node.js build | Build small Node.js service/CLI with tests in 60 min? | B5 | |
| Rust build | Build small Rust CLI/library with tests in 60 min? | B6 | |
| Parallel work | Split task across worktrees/agent sessions safely? | A1, A2 | |
| Verification | Separate agent suggestions from manual verification? | I3, I6, A5 | |

---

## Detailed Eval Tasks

### Basics (B1–B6)

| ID | Task | Time | Agent Spec | Done? |
|----|------|------|------------|-------|
| B1 | Repo artifact inventory | 30m | `agents/basics/B1_repo_artifact_inventory_agent.md` | |
| B2 | API endpoint map | 30m | `agents/basics/B2_api_endpoint_map_agent.md` | |
| B3 | Test discovery and execution | 15m | `agents/basics/B3_test_discovery_agent.md` | |
| B4 | FastAPI greenfield service | 60m | `agents/basics/B4_fastapi_greenfield_agent.md` | |
| B5 | Node.js greenfield API/CLI | 60m | `agents/basics/B5_nodejs_greenfield_agent.md` | |
| B6 | Rust greenfield CLI | 60m | `agents/basics/B6_rust_greenfield_agent.md` | |

### Intermediate (I1–I6)

| ID | Task | Time | Agent Spec | Done? |
|----|------|------|------------|-------|
| I1 | ER diagram from repo | 45m | `agents/intermediate/I1_er_diagram_agent.md` | |
| I2 | End-to-end flow trace | 45m | `agents/intermediate/I2_flow_trace_agent.md` | |
| I3 | Small safe change | 60m | `agents/intermediate/I3_safe_change_agent.md` | |
| I4 | Polyglot FastAPI + Node client | 90m | `agents/intermediate/I4_polyglot_fastapi_node_agent.md` | |
| I5 | Dockerize and run | 60m | `agents/intermediate/I5_dockerize_agent.md` | |
| I6 | Bug diagnosis with fix | 60m | `agents/intermediate/I6_bug_diagnosis_agent.md` | |

### Advanced (A1–A6)

| ID | Task | Time | Agent Spec | Done? |
|----|------|------|------------|-------|
| A1 | Multi-worktree parallel plan | 45m | `agents/advanced/A1_multi_worktree_plan_agent.md` | |
| A2 | Execute two parallel worktrees | 90m | `agents/advanced/A2_parallel_worktrees_execute_agent.md` | |
| A3 | Polyglot fraud mini-system | 150m | `agents/advanced/A3_polyglot_fraud_system_agent.md` | |
| A4 | Modernization + executable first step | 90m | `agents/advanced/A4_modernization_executable_agent.md` | |
| A5 | Adversarial code review | 60m | `agents/advanced/A5_adversarial_code_review_agent.md` | |
| A6 | Performance profiling + improvement | 90m | `agents/advanced/A6_performance_improvement_agent.md` | |

### Infra & DevOps (D1–D6)

| ID | Task | Time | Agent Spec | Done? |
|----|------|------|------------|-------|
| D1 | Terraform plan (validate + plan) | 60m | `agents/infra_devops/D1_terraform_plan_agent.md` | |
| D2 | docker-compose stack + E2E tests | 90m | `agents/infra_devops/D2_docker_compose_stack_agent.md` | |
| D3 | CI pipeline (lint, test, image) | 45m | `agents/infra_devops/D3_ci_pipeline_agent.md` | |
| D4 | Kubernetes manifests (local cluster) | 60m | `agents/infra_devops/D4_kubernetes_manifests_agent.md` | |
| D5 | Reproducible dev environment | 45m | `agents/infra_devops/D5_reproducible_dev_env_agent.md` | |
| D6 | Observability bolt-on | 60m | `agents/infra_devops/D6_observability_bolt_on_agent.md` | |

---

## Eval Sources

- [PML Eval Document](https://docs.google.com/document/d/1VurgqAe_qZlMieK8pA4S2yJjWBd7cnoO8cuvh4zmNZs/edit)
- [OCL Eval Document](https://docs.google.com/document/d/1Y23tu2ePPexkBhh_G0RCK1fNio_NQ3EZuTbgWa_UyPA/edit)

See `core/eval_source.md` for full mapping notes.
