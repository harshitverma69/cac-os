# Eval Source

> Authoritative eval document for CAC-OS task definitions.

## Primary Source

**Coding Agent Eval Document** — May 2026

| Version | Link |
|---------|------|
| PML | https://docs.google.com/document/d/1VurgqAe_qZlMieK8pA4S2yJjWBd7cnoO8cuvh4zmNZs/edit |
| OCL | https://docs.google.com/document/d/1Y23tu2ePPexkBhh_G0RCK1fNio_NQ3EZuTbgWa_UyPA/edit |

## Secondary Reference (patterns only)

RepoLens `capability-matrix.md` — static analysis agent patterns reused where applicable (inventory, API map, flow trace, ER diagram). CAC-OS task IDs follow the **PML/OCL eval**, not the RepoLens matrix.

## Self-Eval Categories (motivation, not separate tasks)

| Category | Mapped Task |
|----------|-------------|
| Repo discovery | B1 |
| Data model | I1 |
| API mapping | B2 |
| Flow tracing | I2 |
| Testing | B3 |
| Greenfield build (FastAPI) | B4 |
| Node.js build | B5 |
| Rust build | B6 |
| Parallel work | A1, A2 |
| Verification | I3, I6, A5 (verification_log fields) |

## Migration Note (RepoLens → PML/OCL)

Previous CAC-OS version mapped RepoLens B1–B8, I1–I7, A1–A6, D1–D6 (27 tasks, repo-intelligence focus).

Current version maps PML/OCL B1–B6, I1–I6, A1–A6, D1–D6 (24 tasks, coding-agent skill journey focus):

| Removed (RepoLens-only) | Replaced By (PML/OCL) |
|-------------------------|------------------------|
| B7 Documentation Generation | I1 + I2 deliverables |
| B8 Verification (standalone) | verification_log in I3, I6, A5 |
| I7 Patch Specification | I3 Safe Change |
| Old D1 CI Intelligence | D3 CI Pipeline |
| Old D3 Incremental Analysis | — (out of PML/OCL scope) |
| Old D4 Health Report | — |
| Old D6 Platform Readiness | — |
| — | B3 Test Discovery (new) |
| — | B4/B5/B6 Greenfield builds (new) |
| — | I4 Polyglot pair (new) |
| — | I5 Dockerize (new) |
| — | A2 Worktree execution (new) |
| — | A3 Fraud mini-system (new) |
| — | D1 Terraform (new) |
| — | D2 Compose stack (new) |
| — | D4 Kubernetes (new) |
| — | D6 Observability (new) |
