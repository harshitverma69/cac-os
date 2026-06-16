# CAC-OS Capability Registry

> 24 tasks from PML/OCL Coding Agent Eval (May 2026). Agent specs live in `agents/` with `*_agent.md` naming.

## Registry Schema

```json
{
  "task_id": "B1",
  "level": "B",
  "name": "Repo Artifact Inventory Agent",
  "agent_spec": "agents/basics/B1_repo_artifact_inventory_agent.md",
  "eval_blueprint": "eval_blueprints/B/B1_blueprint.md",
  "depends_on": [],
  "produces": ["inventory_report.json"],
  "time_budget_min": 30,
  "parallel_safe": true,
  "requires_endpoint": false
}
```

---

## Level B — Repo Reader and Simple Builder (B1–B6)

| Task ID | Agent Spec | Time | Depends On | Produces |
|---------|------------|------|------------|----------|
| B1 | `B1_repo_artifact_inventory_agent.md` | 30m | — | `inventory_report.json` |
| B2 | `B2_api_endpoint_map_agent.md` | 30m | B1 | `api_map_report.json` |
| B3 | `B3_test_discovery_agent.md` | 15m | — | `test_discovery_report.json` |
| B4 | `B4_fastapi_greenfield_agent.md` | 60m | — | `greenfield_manifest.json` |
| B5 | `B5_nodejs_greenfield_agent.md` | 60m | B4 | `greenfield_manifest.json` |
| B6 | `B6_rust_greenfield_agent.md` | 60m | — | `greenfield_manifest.json` |

---

## Level I — Repo Operator and Polyglot Builder (I1–I6)

| Task ID | Agent Spec | Time | Depends On | Produces |
|---------|------------|------|------------|----------|
| I1 | `I1_er_diagram_agent.md` | 45m | B1 | `schema_report.json` |
| I2 | `I2_flow_trace_agent.md` | 45m | B2 | `flow_trace_report.json` |
| I3 | `I3_safe_change_agent.md` | 60m | B3 | `change_report.json` |
| I4 | `I4_polyglot_fastapi_node_agent.md` | 90m | B4, B5 | `polyglot_manifest.json` |
| I5 | `I5_dockerize_agent.md` | 60m | — | `docker_manifest.json` |
| I6 | `I6_bug_diagnosis_agent.md` | 60m | I2 | `bug_fix_report.json` |

---

## Level A — Parallel Agent Operator and System Builder (A1–A6)

| Task ID | Agent Spec | Time | Depends On | Produces |
|---------|------------|------|------------|----------|
| A1 | `A1_multi_worktree_plan_agent.md` | 45m | — | `worktree_plan.json` |
| A2 | `A2_parallel_worktrees_execute_agent.md` | 90m | A1 | `worktree_execution_report.json` |
| A3 | `A3_polyglot_fraud_system_agent.md` | 150m | B4, B5, B6, I4 | `fraud_system_manifest.json` |
| A4 | `A4_modernization_executable_agent.md` | 90m | B1, B3 | `modernization_report.json` |
| A5 | `A5_adversarial_code_review_agent.md` | 60m | — | `code_review_report.json` |
| A6 | `A6_performance_improvement_agent.md` | 90m | — | `performance_report.json` |

---

## Level D — Infra and DevOps (D1–D6)

| Task ID | Agent Spec | Time | Depends On | Produces |
|---------|------------|------|------------|----------|
| D1 | `D1_terraform_plan_agent.md` | 60m | — | `terraform_manifest.json` |
| D2 | `D2_docker_compose_stack_agent.md` | 90m | I5 | `compose_manifest.json` |
| D3 | `D3_ci_pipeline_agent.md` | 45m | B3, I5 | `ci_manifest.json` |
| D4 | `D4_kubernetes_manifests_agent.md` | 60m | I5 | `k8s_manifest.json` |
| D5 | `D5_reproducible_dev_env_agent.md` | 45m | B3 | `bootstrap_manifest.json` |
| D6 | `D6_observability_bolt_on_agent.md` | 60m | I5 | `observability_manifest.json` |

---

## Dependency Graph (Acyclic)

```
B1 ── B2 ── I2 ── I6
B1 ── I1
B2 ── (I2)
B3 ── I3, A4, D3, D5
B4 ── B5 ── I4 ── A3
B6 ── A3
I5 ── D2, D3, D4, D6
A1 ── A2
```

Full DAG: `execution_models/dependency_graph.md`

---

## Coverage (PML/OCL Eval)

| Level | Tasks | Specs | Blueprints | Coverage |
|-------|-------|-------|------------|----------|
| B | B1–B6 | 6/6 | 6/6 | 100% |
| I | I1–I6 | 6/6 | 6/6 | 100% |
| A | A1–A6 | 6/6 | 6/6 | 100% |
| D | D1–D6 | 6/6 | 6/6 | 100% |
| **Total** | **24** | **24/24** | **24/24** | **100%** |

---

## Index

- Agent specs: `agents/{basics,intermediate,advanced,infra_devops}/*_agent.md`
- Eval blueprints: `eval_blueprints/{B,I,A,D}/`
- Eval source: `core/eval_source.md`
- Self-eval checklist: `core/self_eval_checklist.md`
- Golden examples: `generated_projects/_golden/`
- Runner: `scripts/cac_os.py` (`make validate`, `make route`)
- Status: `docs/STATUS.md`
