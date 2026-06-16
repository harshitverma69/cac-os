# CAC-OS Skill Catalog

> What each skill does and where it lives. Regenerate with `python runtime/skill_registry_builder.py`.

Total skills: **24**

## Basic Skills (B1–B6)

| ID | Name | Works On | Depends On | Skill File |
|----|------|----------|------------|------------|
| B1 | Repo Artifact Inventory Agent | Inspect an unfamiliar repository and produce a deterministic inventory of classes, interfaces, services, controllers, models, repositories, jobs, consumers, configs, and utilities. | — | `skills/basics/B1_repo_artifact_inventory.skill.md` |
| B2 | API Endpoint Map Agent | Identify every externally exposed API route and frontend route; map each to handler and controller via static inspection. | B1 | `skills/basics/B2_api_endpoint_map.skill.md` |
| B3 | Test Discovery Agent | Find test framework, config file, relevant test files, and exact commands to run tests for a module. | — | `skills/basics/B3_test_discovery.skill.md` |
| B4 | FastAPI Greenfield Service Agent | Build a small Python FastAPI service from scratch with POST/GET endpoints, input validation, tests, and README. | — | `skills/basics/B4_fastapi_greenfield.skill.md` |
| B5 | Node.js Greenfield API Agent | Build equivalent transaction/balance service as Node.js API or CLI with tests and README. | B4 | `skills/basics/B5_nodejs_greenfield.skill.md` |
| B6 | Rust Greenfield CLI Agent | Build Rust CLI that accepts file path, counts INFO/WARN/ERROR lines, handles missing file gracefully, with tests and README. | — | `skills/basics/B6_rust_greenfield.skill.md` |

## Intermediate Skills (I1–I6)

| ID | Name | Works On | Depends On | Skill File |
|----|------|----------|------------|------------|
| I1 | ER Diagram Agent | Build ER diagram for all tables and entities from repo source only; cite source file for every claim. | B1 | `skills/intermediate/I1_er_diagram.skill.md` |
| I2 | Flow Trace Agent | Trace one endpoint, event, or cron job end-to-end from entry point to final DB/API/queue side effect. | B2 | `skills/intermediate/I2_flow_trace.skill.md` |
| I3 | Safe Change Agent | Make a small focused change in an unfamiliar module with minimal diff, test update, and verification log. | B3 | `skills/intermediate/I3_safe_change.skill.md` |
| I4 | Polyglot FastAPI Node Agent | Build FastAPI /convert service and Node.js CLI client with hardcoded rates, tests, and two-terminal README. | B4, B5 | `skills/intermediate/I4_polyglot_fastapi_node.skill.md` |
| I5 | Dockerize Agent | Containerize a service so it builds and runs cleanly in Docker with health check proof. | — | `skills/intermediate/I5_dockerize.skill.md` |
| I6 | Bug Diagnosis Agent | Reproduce seeded bug, identify root cause with file paths, apply minimal fix, verify with command proof. | I2 | `skills/intermediate/I6_bug_diagnosis.skill.md` |

## Advanced Skills (A1–A6)

| ID | Name | Works On | Depends On | Skill File |
|----|------|----------|------------|------------|
| A1 | Multi-Worktree Plan Agent | Split one feature/analysis task into parallel worktrees or agent sessions without merge chaos. | — | `skills/advanced/A1_multi_worktree_plan.skill.md` |
| A2 | Parallel Worktrees Execute Agent | Create two parallel worktrees, make independent changes, reconcile cleanly with test proof. | A1 | `skills/advanced/A2_parallel_worktrees_execute.skill.md` |
| A3 | Polyglot Fraud System Agent | Build mini fraud-score system: FastAPI ingestion, Node.js worker, Rust scoring engine with tests and README. | B4, B5, B6, I4 | `skills/advanced/A3_polyglot_fraud_system.skill.md` |
| A4 | Modernization Executable Agent | Analyze repo for modernization opportunities, prioritize, implement highest-value lowest-risk first step. | B1, B3 | `skills/advanced/A4_modernization_executable.skill.md` |
| A5 | Adversarial Code Review Agent | Review agent-generated PR for correctness, security, test, performance, maintainability issues; propose fixes. | — | `skills/advanced/A5_adversarial_code_review.skill.md` |
| A6 | Performance Improvement Agent | Find real performance bottleneck, make measurable minimal improvement, prove behavior unchanged. | — | `skills/advanced/A6_performance_improvement.skill.md` |

## Infra Skills (D1–D6)

| ID | Name | Works On | Depends On | Skill File |
|----|------|----------|------------|------------|
| D1 | Terraform Plan Agent | Write Terraform for small service that passes validate and produces clean plan against test backend. | — | `skills/infra/D1_terraform_plan.skill.md` |
| D2 | Docker Compose Stack Agent | Stand up multi-service stack (API + DB + worker) with docker-compose, seed data, and E2E test script. | I5 | `skills/infra/D2_docker_compose_stack.skill.md` |
| D3 | CI Pipeline Agent | Write CI workflow that lints, tests, builds and tags container image with green run proof. | B3, I5 | `skills/infra/D3_ci_pipeline.skill.md` |
| D4 | Kubernetes Manifests Agent | Write K8s manifests, validate with dry-run/kubeval, deploy on kind/minikube with curl proof. | I5 | `skills/infra/D4_kubernetes_manifests.skill.md` |
| D5 | Reproducible Dev Environment Agent | Bootstrap repo from fresh clone with single command; tests pass on clean machine. | B3 | `skills/infra/D5_reproducible_dev_env.skill.md` |
| D6 | Observability Bolt-On Agent | Add structured logging and /metrics endpoint; stand up Prometheus + Grafana with working dashboard panel. | I5 | `skills/infra/D6_observability_bolt_on.skill.md` |

## Master Pipeline Skill

| ID | Name | Works On | Skill File |
|----|------|----------|------------|
| ALL | Full Pipeline | Runs all 24 skills in DAG order with deterministic golden outputs | `skills/run_all_skills.skill.md` |

## How Skills Execute

1. `runtime/skill_registry_builder.py` compiles agent specs → `.skill.md` + `core/skill_registry.json`
2. `runtime/skill_orchestrator.py` builds the DAG and execution plan
3. `runtime/skill_runner.py` executes each skill deterministically (golden reference, no LLM)
4. Outputs land in `generated_projects/{run_id}/{skill_id}/output.json`

