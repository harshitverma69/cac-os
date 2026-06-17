# Repo-Analyser

**Repo-Analyser** is a deterministic repository analysis framework: Markdown agent specs → structured JSON outputs. No runtime AI inside the framework itself.

24 skills aligned with the **PML/OCL Coding Agent Eval** (May 2026).

## Quick start

**Full setup guide:** **[docs/SETUP.md](docs/SETUP.md)** — frontend auto-open, Cursor skills, and daily workflow.

```bash
git clone https://github.com/harshitverma69/Repo-Analyser.git
cd Repo-Analyser
make build-skills
make install-cursor-skills   # 24 /repo-analyser-* skills → ~/.cursor/skills/
make build-frontend
make validate                # optional but recommended
```

Or: `make setup` (runs build-skills, install-cursor-skills, build-frontend, and validate).

**Restart Cursor completely** after install — slash commands appear under `/` → search `repo-analyser`.

Optional — keep the UI open before you start:

```bash
make serve-frontend         # http://127.0.0.1:8765
make validate               # verify specs and DAG
```

## Main guides

| Doc | Contents |
|-----|----------|
| **[docs/SETUP.md](docs/SETUP.md)** | **Start here** — full setup, auto-open flow, troubleshooting |
| **[docs/HOW_TO_RUN.md](docs/HOW_TO_RUN.md)** | All 24 skills with file paths and commands |

## Repository structure

| Path | Purpose |
|------|---------|
| `agents/` | Agent specs (source of truth) |
| `skills/` | Compiled `.skill.md` execution specs |
| `core/skill_registry.json` | Machine-readable skill index |
| `runtime/` | Orchestrator, runner, validator |
| `eval_blueprints/` | Eval runbooks |
| `generated_projects/_golden/` | Reference JSON outputs |
| `tools/install_cursor_skills.py` | Cursor `/` menu installer |
| `frontend/` | Local browser guide for all 24 agents (`make serve-frontend`) |

## Common commands

```bash
make run-skill SKILL=B1 RUN_ID=demo    # run one skill
make run-pipeline RUN_ID=full-run      # run all 24 skills
make validate-dag                      # check dependency graph
make harden                            # full production check
make test                              # test suite
```

## Cursor usage

Type `/` in chat → search `repo-analyser` → e.g. `/repo-analyser-repo-inventory`, `/repo-analyser-api-mapping`

## Other docs

| Doc | Description |
|-----|-------------|
| [docs/SETUP.md](docs/SETUP.md) | **Start here** — setup, frontend auto-open, troubleshooting |
| [docs/HOW_TO_RUN.md](docs/HOW_TO_RUN.md) | All 24 skills with commands and file paths |
| [docs/OVERVIEW.md](docs/OVERVIEW.md) | Architecture overview |
| [docs/STATUS.md](docs/STATUS.md) | Project status |
| [core/capability_registry.md](core/capability_registry.md) | Task registry with dependencies |

## Eval sources

- [PML Eval](https://docs.google.com/document/d/1VurgqAe_qZlMieK8pA4S2yJjWBd7cnoO8cuvh4zmNZs/edit)
- [OCL Eval](https://docs.google.com/document/d/1Y23tu2ePPexkBhh_G0RCK1fNio_NQ3EZuTbgWa_UyPA/edit)
