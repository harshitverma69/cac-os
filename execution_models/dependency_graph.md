# Dependency Graph

> PML/OCL eval — 24 tasks, acyclic.

```mermaid
graph TD
    B1[B1 Repo Inventory] --> B2[B2 API Map]
    B1 --> I1[I1 ER Diagram]
    B2 --> I2[I2 Flow Trace]
    I2 --> I6[I6 Bug Fix]

    B3[B3 Test Discovery] --> I3[I3 Safe Change]
    B3 --> A4[A4 Modernization]
    B3 --> D3[D3 CI Pipeline]
    B3 --> D5[D5 Bootstrap]

    B4[B4 FastAPI] --> B5[B5 Node.js]
    B4 --> I4[I4 Polyglot Pair]
    B5 --> I4
    B4 --> A3[A3 Fraud System]
    B5 --> A3
    B6[B6 Rust CLI] --> A3

    I5[I5 Dockerize] --> D2[D2 Compose Stack]
    I5 --> D3
    I5 --> D4[D4 Kubernetes]
    I5 --> D6[D6 Observability]

    A1[A1 Worktree Plan] --> A2[A2 Worktree Execute]

    D1[D1 Terraform]
```

## Topological Waves

| Wave | Tasks | Parallel? |
|------|-------|-----------|
| 0 | B1, B3, B4, B6, A1, A5, A6, D1, I5 | ✓ (independent) |
| 1 | B2, B5, A2, I1, D5 | partial |
| 2 | I2, I3, I4, A4, D2, D3, D4, D6 | partial |
| 3 | I6, A3 | — |

## Full Sequential Order (tie-break by task ID)

```
B1 → B2 → B3 → B4 → B5 → B6 → I1 → I2 → I3 → I4 → I5 → I6 → A1 → A2 → A3 → A4 → A5 → A6 → D1 → D2 → D3 → D4 → D5 → D6
```

(Dependencies still enforced — this is max ordering under constraints.)

## Parallel-Safe Groups

| Group | Tasks | Condition |
|-------|-------|-----------|
| Greenfield | B4, B6 | No shared output dir |
| Post-B1 | B2, I1 | Both read B1 only |
| Infra (post-I5) | D2, D4, D6 | Disjoint manifests |

See `execution_models/parallel_execution_model.md`
