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

Start the local UI (required for **Run all 24** pipeline wizard):

```bash
make serve-frontend         # http://127.0.0.1:8765 — keep this terminal open
```

The UI also auto-starts when a skill finishes via `skill_finish write`.

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

Type `/` in chat → search `repo-analyser` → e.g. `/repo-analyser-repo-inventory`, `/repo-analyser-er-diagram @/path/to/repo`

### Run all 24 agents on one folder

1. Run `make serve-frontend` and open **http://127.0.0.1:8765**
2. Click **Run all 24** → enter the full path to your target repo
3. For each step: copy the slash command, run it in Cursor, then click **Mark done & next**

Agents run in Cursor — the UI guides you; it does not execute them automatically. See **[docs/SETUP.md](docs/SETUP.md)** §5.

## More docs

| Doc | Description |
|-----|-------------|
| [docs/OVERVIEW.md](docs/OVERVIEW.md) | Architecture overview |
| [docs/STATUS.md](docs/STATUS.md) | Project status |
| [frontend/README.md](frontend/README.md) | Local UI and Pipeline wizard |
| [core/capability_registry.md](core/capability_registry.md) | Task registry with dependencies |
