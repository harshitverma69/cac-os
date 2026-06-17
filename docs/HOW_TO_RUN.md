# Repo-Analyser — How to Run

> Single guide for setup, commands, and all 24 skills. Regenerate with `make build-skills`.

## What is Repo-Analyser?

Repo-Analyser is a **deterministic Markdown execution framework** — not a runtime AI system.
Agent specs define inputs, outputs, and rules. Cursor (or you) execute them and write JSON.

**Total skills:** 24 (B1–B6, I1–I6, A1–A6, D1–D6)

---

## 1. Prerequisites

- Python 3.10+
- No external AI services required for validation/runtime

Optional for tests:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install pytest pytest-cov
```

---

## 2. First-time setup

```bash
cd Repo-Analyser
make build-skills          # compile agent specs → .skill.md + core/skill_registry.json
make expand-agent-specs    # expand agents/ to full procedural specs (optional)
make install-cursor-skills # install 24 skills into Cursor / menu
make build-frontend        # build local agent guide UI
make serve-frontend        # open http://127.0.0.1:8765 (no deploy)
make validate              # verify specs, blueprints, golden examples, DAG
```

Restart Cursor after `install-cursor-skills` if `/repo-analyser-*` commands do not appear.

---

## 3. Common commands

| Command | Purpose |
|---------|---------|
| `make build-skills` | Regenerate skill files and registry |
| `make expand-agent-specs` | Expand all 24 agent specs to procedural detail |
| `make install-cursor-skills` | Install skills into Cursor `/` menu |
| `make build-frontend` | Generate local browser guide (`frontend/data/skills.json`) |
| `make serve-frontend` | Open local UI at http://127.0.0.1:8765 |
| `make validate` | Validate all agent specs and DAG |
| `make validate-dag` | Validate skill dependency graph |
| `make run-skill SKILL=B1 RUN_ID=my-run` | Run one skill |
| `make run-pipeline RUN_ID=my-run` | Run all 24 skills in DAG order |
| `make validate-pipeline RUN_ID=my-run` | Validate a pipeline run |
| `make harden` | Full production check (tests + determinism) |
| `make test` | Run test suite |

### Run one skill in Cursor

1. Type `/repo-analyser-repo-inventory` (or any skill below) in chat
2. Follow the agent spec and skill spec
3. Write output, **output.md**, and auto-open CLI UI:

```bash
python3 -m runtime.skill_finish write --run-id <run_id> --skill B1 --payload-file payload.json
```

If the terminal UI does not appear, open `generated_projects/<run_id>/B1/output.md`.

Or if `output.json` already exists: `python3 -m runtime.skill_finish --run-id <run_id> --skill B1`

### Run via deterministic runtime

```bash
make run-skill SKILL=B2 RUN_ID=demo
make run-pipeline RUN_ID=full-run
python -m runtime.validate_pipeline --run-id full-run
```

---

## 4. Repository layout

| Path | Role |
|------|------|
| `agents/` | Source agent specs (inputs, outputs, rules) |
| `skills/` | Compiled skill specs (`.skill.md`) for execution |
| `core/skill_registry.json` | Machine-readable index of all 24 skills |
| `eval_blueprints/` | Step-by-step eval runbooks |
| `runtime/` | Deterministic orchestrator, runner, validator |
| `generated_projects/_golden/` | Reference JSON outputs |
| `generated_projects/{run_id}/` | Your run outputs |
| `frontend/` | Local browser guide for all 24 agents |
| `tools/install_cursor_skills.py` | Installs Cursor `/repo-analyser-*` skills |

---

## 5. All 24 skills

### Basic (B1–B6) — Repo reading and greenfield builds

#### B1 — Repo Artifact Inventory

**Role:** Inspect an unfamiliar repository and produce a deterministic inventory of classes, interfaces, services, controllers, models, repositories, jobs, consumers, configs, and utilities.

**Depends on:** none

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-repo-inventory` |
| Agent spec | `agents/basics/B1_repo_artifact_inventory_agent.md` |
| Skill spec | `skills/basics/B1_repo_artifact_inventory.skill.md` |
| Eval blueprint | `eval_blueprints/B/B1_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/B1/output.json` |
| Golden reference | `generated_projects/_golden/B1/inventory_report.json` |

#### B2 — Api Endpoint Map

**Role:** Identify every externally exposed API route and frontend route; map each to handler and controller via static inspection.

**Depends on:** B1

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-api-mapping` |
| Agent spec | `agents/basics/B2_api_endpoint_map_agent.md` |
| Skill spec | `skills/basics/B2_api_endpoint_map.skill.md` |
| Eval blueprint | `eval_blueprints/B/B2_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/B2/output.json` |
| Golden reference | `generated_projects/_golden/B2/api_map_report.json` |

#### B3 — Test Discovery

**Role:** Find test framework, config file, relevant test files, and exact commands to run tests for a module.

**Depends on:** none

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-test-discovery` |
| Agent spec | `agents/basics/B3_test_discovery_agent.md` |
| Skill spec | `skills/basics/B3_test_discovery.skill.md` |
| Eval blueprint | `eval_blueprints/B/B3_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/B3/output.json` |
| Golden reference | `generated_projects/_golden/B3/test_discovery_report.json` |

#### B4 — Fastapi Greenfield

**Role:** Build a small Python FastAPI service from scratch with POST/GET endpoints, input validation, tests, and README.

**Depends on:** none

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-fastapi-greenfield` |
| Agent spec | `agents/basics/B4_fastapi_greenfield_agent.md` |
| Skill spec | `skills/basics/B4_fastapi_greenfield.skill.md` |
| Eval blueprint | `eval_blueprints/B/B4_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/B4/output.json` |
| Golden reference | `generated_projects/_golden/B4/greenfield_manifest.json` |

#### B5 — Nodejs Greenfield

**Role:** Build equivalent transaction/balance service as Node.js API or CLI with tests and README.

**Depends on:** B4

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-node-greenfield` |
| Agent spec | `agents/basics/B5_nodejs_greenfield_agent.md` |
| Skill spec | `skills/basics/B5_nodejs_greenfield.skill.md` |
| Eval blueprint | `eval_blueprints/B/B5_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/B5/output.json` |
| Golden reference | `generated_projects/_golden/B5/greenfield_manifest.json` |

#### B6 — Rust Greenfield

**Role:** Build Rust CLI that accepts file path, counts INFO/WARN/ERROR lines, handles missing file gracefully, with tests and README.

**Depends on:** none

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-rust-greenfield` |
| Agent spec | `agents/basics/B6_rust_greenfield_agent.md` |
| Skill spec | `skills/basics/B6_rust_greenfield.skill.md` |
| Eval blueprint | `eval_blueprints/B/B6_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/B6/output.json` |
| Golden reference | `generated_projects/_golden/B6/greenfield_manifest.json` |

### Intermediate (I1–I6) — Repo operations and polyglot work

#### I1 — Er Diagram

**Role:** Build ER diagram for all tables and entities from repo source only; cite source file for every claim.

**Depends on:** B1

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-er-diagram` |
| Agent spec | `agents/intermediate/I1_er_diagram_agent.md` |
| Skill spec | `skills/intermediate/I1_er_diagram.skill.md` |
| Eval blueprint | `eval_blueprints/I/I1_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/I1/output.json` |
| Golden reference | `generated_projects/_golden/I1/schema_report.json` |

#### I2 — Flow Trace

**Role:** Trace one endpoint, event, or cron job end-to-end from entry point to final DB/API/queue side effect.

**Depends on:** B2

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-flow-trace` |
| Agent spec | `agents/intermediate/I2_flow_trace_agent.md` |
| Skill spec | `skills/intermediate/I2_flow_trace.skill.md` |
| Eval blueprint | `eval_blueprints/I/I2_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/I2/output.json` |
| Golden reference | `generated_projects/_golden/I2/flow_trace_report.json` |

#### I3 — Safe Change

**Role:** Make a small focused change in an unfamiliar module with minimal diff, test update, and verification log.

**Depends on:** B3

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-safe-change` |
| Agent spec | `agents/intermediate/I3_safe_change_agent.md` |
| Skill spec | `skills/intermediate/I3_safe_change.skill.md` |
| Eval blueprint | `eval_blueprints/I/I3_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/I3/output.json` |
| Golden reference | `generated_projects/_golden/I3/change_report.json` |

#### I4 — Polyglot Fastapi Node

**Role:** Build FastAPI /convert service and Node.js CLI client with hardcoded rates, tests, and two-terminal README.

**Depends on:** B4, B5

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-polyglot-pair` |
| Agent spec | `agents/intermediate/I4_polyglot_fastapi_node_agent.md` |
| Skill spec | `skills/intermediate/I4_polyglot_fastapi_node.skill.md` |
| Eval blueprint | `eval_blueprints/I/I4_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/I4/output.json` |
| Golden reference | `generated_projects/_golden/I4/polyglot_manifest.json` |

#### I5 — Dockerize

**Role:** Containerize a service so it builds and runs cleanly in Docker with health check proof.

**Depends on:** none

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-dockerize` |
| Agent spec | `agents/intermediate/I5_dockerize_agent.md` |
| Skill spec | `skills/intermediate/I5_dockerize.skill.md` |
| Eval blueprint | `eval_blueprints/I/I5_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/I5/output.json` |
| Golden reference | `generated_projects/_golden/I5/docker_manifest.json` |

#### I6 — Bug Diagnosis

**Role:** Reproduce seeded bug, identify root cause with file paths, apply minimal fix, verify with command proof.

**Depends on:** I2

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-bug-diagnosis` |
| Agent spec | `agents/intermediate/I6_bug_diagnosis_agent.md` |
| Skill spec | `skills/intermediate/I6_bug_diagnosis.skill.md` |
| Eval blueprint | `eval_blueprints/I/I6_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/I6/output.json` |
| Golden reference | `generated_projects/_golden/I6/bug_fix_report.json` |

### Advanced (A1–A6) — Parallel work and system building

#### A1 — Multi Worktree Plan

**Role:** Split one feature/analysis task into parallel worktrees or agent sessions without merge chaos.

**Depends on:** none

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-worktree-plan` |
| Agent spec | `agents/advanced/A1_multi_worktree_plan_agent.md` |
| Skill spec | `skills/advanced/A1_multi_worktree_plan.skill.md` |
| Eval blueprint | `eval_blueprints/A/A1_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/A1/output.json` |
| Golden reference | `generated_projects/_golden/A1/worktree_plan.json` |

#### A2 — Parallel Worktrees Execute

**Role:** Create two parallel worktrees, make independent changes, reconcile cleanly with test proof.

**Depends on:** A1

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-worktree-execute` |
| Agent spec | `agents/advanced/A2_parallel_worktrees_execute_agent.md` |
| Skill spec | `skills/advanced/A2_parallel_worktrees_execute.skill.md` |
| Eval blueprint | `eval_blueprints/A/A2_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/A2/output.json` |
| Golden reference | `generated_projects/_golden/A2/worktree_execution_report.json` |

#### A3 — Polyglot Fraud System

**Role:** Build mini fraud-score system: FastAPI ingestion, Node.js worker, Rust scoring engine with tests and README.

**Depends on:** B4, B5, B6, I4

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-fraud-system` |
| Agent spec | `agents/advanced/A3_polyglot_fraud_system_agent.md` |
| Skill spec | `skills/advanced/A3_polyglot_fraud_system.skill.md` |
| Eval blueprint | `eval_blueprints/A/A3_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/A3/output.json` |
| Golden reference | `generated_projects/_golden/A3/fraud_system_manifest.json` |

#### A4 — Modernization Executable

**Role:** Analyze repo for modernization opportunities, prioritize, implement highest-value lowest-risk first step.

**Depends on:** B1, B3

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-modernization` |
| Agent spec | `agents/advanced/A4_modernization_executable_agent.md` |
| Skill spec | `skills/advanced/A4_modernization_executable.skill.md` |
| Eval blueprint | `eval_blueprints/A/A4_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/A4/output.json` |
| Golden reference | `generated_projects/_golden/A4/modernization_report.json` |

#### A5 — Adversarial Code Review

**Role:** Review agent-generated PR for correctness, security, test, performance, maintainability issues; propose fixes.

**Depends on:** none

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-code-review` |
| Agent spec | `agents/advanced/A5_adversarial_code_review_agent.md` |
| Skill spec | `skills/advanced/A5_adversarial_code_review.skill.md` |
| Eval blueprint | `eval_blueprints/A/A5_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/A5/output.json` |
| Golden reference | `generated_projects/_golden/A5/code_review_report.json` |

#### A6 — Performance Improvement

**Role:** Find real performance bottleneck, make measurable minimal improvement, prove behavior unchanged.

**Depends on:** none

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-performance-tuning` |
| Agent spec | `agents/advanced/A6_performance_improvement_agent.md` |
| Skill spec | `skills/advanced/A6_performance_improvement.skill.md` |
| Eval blueprint | `eval_blueprints/A/A6_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/A6/output.json` |
| Golden reference | `generated_projects/_golden/A6/performance_report.json` |

### Infra (D1–D6) — DevOps and infrastructure

#### D1 — Terraform Plan

**Role:** Write Terraform for small service that passes validate and produces clean plan against test backend.

**Depends on:** none

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-terraform` |
| Agent spec | `agents/infra_devops/D1_terraform_plan_agent.md` |
| Skill spec | `skills/infra/D1_terraform_plan.skill.md` |
| Eval blueprint | `eval_blueprints/D/D1_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/D1/output.json` |
| Golden reference | `generated_projects/_golden/D1/terraform_manifest.json` |

#### D2 — Docker Compose Stack

**Role:** Stand up multi-service stack (API + DB + worker) with docker-compose, seed data, and E2E test script.

**Depends on:** I5

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-compose-stack` |
| Agent spec | `agents/infra_devops/D2_docker_compose_stack_agent.md` |
| Skill spec | `skills/infra/D2_docker_compose_stack.skill.md` |
| Eval blueprint | `eval_blueprints/D/D2_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/D2/output.json` |
| Golden reference | `generated_projects/_golden/D2/compose_manifest.json` |

#### D3 — Ci Pipeline

**Role:** Write CI workflow that lints, tests, builds and tags container image with green run proof.

**Depends on:** B3, I5

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-ci-pipeline` |
| Agent spec | `agents/infra_devops/D3_ci_pipeline_agent.md` |
| Skill spec | `skills/infra/D3_ci_pipeline.skill.md` |
| Eval blueprint | `eval_blueprints/D/D3_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/D3/output.json` |
| Golden reference | `generated_projects/_golden/D3/ci_manifest.json` |

#### D4 — Kubernetes Manifests

**Role:** Write K8s manifests, validate with dry-run/kubeval, deploy on kind/minikube with curl proof.

**Depends on:** I5

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-kubernetes` |
| Agent spec | `agents/infra_devops/D4_kubernetes_manifests_agent.md` |
| Skill spec | `skills/infra/D4_kubernetes_manifests.skill.md` |
| Eval blueprint | `eval_blueprints/D/D4_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/D4/output.json` |
| Golden reference | `generated_projects/_golden/D4/k8s_manifest.json` |

#### D5 — Reproducible Dev Env

**Role:** Bootstrap repo from fresh clone with single command; tests pass on clean machine.

**Depends on:** B3

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-dev-bootstrap` |
| Agent spec | `agents/infra_devops/D5_reproducible_dev_env_agent.md` |
| Skill spec | `skills/infra/D5_reproducible_dev_env.skill.md` |
| Eval blueprint | `eval_blueprints/D/D5_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/D5/output.json` |
| Golden reference | `generated_projects/_golden/D5/bootstrap_manifest.json` |

#### D6 — Observability Bolt On

**Role:** Add structured logging and /metrics endpoint; stand up Prometheus + Grafana with working dashboard panel.

**Depends on:** I5

| Item | Location |
|------|----------|
| Cursor command | `/repo-analyser-observability` |
| Agent spec | `agents/infra_devops/D6_observability_bolt_on_agent.md` |
| Skill spec | `skills/infra/D6_observability_bolt_on.skill.md` |
| Eval blueprint | `eval_blueprints/D/D6_blueprint.md` |
| Output JSON | `generated_projects/{run_id}/D6/output.json` |
| Golden reference | `generated_projects/_golden/D6/observability_manifest.json` |

### Master pipeline

**Role:** Run all 24 skills in DAG order with deterministic outputs.

| Item | Location |
|------|----------|
| Skill spec | `skills/run_all_skills.skill.md` |
| Run command | `make run-pipeline RUN_ID=my-run` |

---

## 6. System rules

- No runtime AI agents inside Repo-Analyser itself
- No inference or probabilistic logic in the runtime
- Markdown specs are the program; JSON is the output
- Execution order follows the DAG in `execution_models/dependency_graph.md`

