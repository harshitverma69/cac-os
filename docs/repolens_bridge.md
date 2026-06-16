# RepoLens Bridge

> Maps RepoLens runtime agents to CAC-OS PML/OCL eval tasks. Use RepoLens for **static repo analysis**; use CAC-OS agent specs for **skill eval execution** (build, docker, CI, worktrees).

## When to Use Which

| Goal | Use |
|------|-----|
| Scan unfamiliar Java/Python/Node repo | RepoLens `RepoDiscoveryAgent` → CAC-OS **B1** |
| Map HTTP endpoints | RepoLens `ApiMappingAgent` → CAC-OS **B2** |
| ER diagram from ORM | RepoLens `ErDiagramAgent` → CAC-OS **I1** |
| Trace endpoint flow | RepoLens `FlowTraceAgent` → CAC-OS **I2** |
| Bug diagnosis (static) | RepoLens `BugDiagnosisAgent` → CAC-OS **I6** (add fix + proof) |
| Build FastAPI/Node/Rust from scratch | CAC-OS **B4/B5/B6** only (not RepoLens) |
| Docker, Terraform, K8s, CI | CAC-OS **I5, D1–D6** only |
| Parallel worktrees | CAC-OS **A1/A2** only |

---

## Agent Mapping Table

| CAC-OS Task | RepoLens Agent | Overlap |
|-------------|----------------|---------|
| B1 Repo inventory | `RepoDiscoveryAgent` | High — use RepoLens output as B1 input |
| B2 API map | `ApiMappingAgent` | High |
| B3 Test discovery | `TestDiscoveryAgent` | High |
| B4 FastAPI greenfield | — | None — greenfield build |
| B5 Node greenfield | — | None |
| B6 Rust greenfield | — | None |
| I1 ER diagram | `ErDiagramAgent` | High — add Mermaid + source citations |
| I2 Flow trace | `FlowTraceAgent` | High — add sequence diagram |
| I3 Safe change | `AutoRefactorAgent` (plan only) | Partial — I3 requires actual diff + test |
| I4 Polyglot pair | — | None |
| I5 Dockerize | — | None |
| I6 Bug fix | `BugDiagnosisAgent` | Partial — I6 requires reproduction + fix |
| A1 Worktree plan | `ParallelWorktreePlanner` | Partial |
| A2 Worktree execute | — | None — git operations |
| A3 Fraud system | — | None — multi-language build |
| A4 Modernization | `ModernizationAgent` + `AutoRefactorAgent` | Partial — A4 requires implemented first step |
| A5 Code review | `VerificationAgent` | Partial — A5 is adversarial PR review |
| A6 Performance | `PerformanceAgent` | Partial — A6 requires measured before/after |
| D1–D6 Infra | `ArtifactValidationRunner`, etc. | Low — CAC-OS infra tasks are platform artifacts |

---

## Example: B2 Using RepoLens

```python
from pathlib import Path
from app.agents.api_mapping_agent import ApiMappingAgent

report = ApiMappingAgent().scan(Path("./target-repo"))
# Transform ApiMapReport → CAC-OS B2 api_map_report.json schema
# Write to generated_projects/{run_id}/B2/api_map_report.json
```

Schema mapping: see `verification/output_contracts.md` (B2 section) and RepoLens `ApiMapReport`.

---

## Example: I2 Using RepoLens

```python
from app.agents.flow_trace_agent import FlowTraceAgent

trace = FlowTraceAgent().trace("./target-repo", "POST:/sip/create")
# Map trace.nodes/edges → I2 flow_trace_report.json
# Add sequence_diagram_mermaid from structured steps
```

---

## RepoLens-Only Capabilities (Not in PML/OCL Eval)

These exist in RepoLens but are **not** separate CAC-OS eval tasks:

- `DocumentationGeneratorAgent` — absorbed into I1/I2 deliverables
- `CodeModificationAgent` / `PatchExecutionAgent` — patch specs (planning)
- `PullRequestAgent` — PR generation
- `RepositoryHealthAgent` — metrics (partial overlap with B1/B2/I1)
- Unified A1–D6 platform pipeline — see old RepoLens registry; CAC-OS uses PML/OCL task set instead

---

## Running Against RepoLens Backend

Target repo for practice scans (from capability-matrix):

```bash
cd repolens/backend
python -c "
from pathlib import Path
from app.agents.repo_discovery_agent import RepoDiscoveryAgent
print(RepoDiscoveryAgent().scan(Path('../path-to-repo')).to_json())
"
```

CAC-OS outputs always land in `generated_projects/{run_id}/` regardless of whether RepoLens or Cursor produces them.
