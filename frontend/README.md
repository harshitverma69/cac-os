# Repo-Analyser local UI

Static browser guide for all 24 agents. **No deployment** — runs on your machine only.

See **[docs/SETUP.md](../docs/SETUP.md)** for the full setup guide (Cursor skills + auto-open flow).

## Quick start

```bash
cd Repo-Analyser
make build-skills
make install-cursor-skills   # installs 24 /repo-analyser-* skills → ~/.cursor/skills/
make build-frontend
```

Or one command: `make setup` (runs all three above plus `make validate`).

**Restart Cursor completely** after `install-cursor-skills` — then type `/` and search `repo-analyser`.

Optional — keep the UI open while you work:

```bash
make serve-frontend     # http://127.0.0.1:8765
```

Press `Ctrl+C` to stop the server.

## What happens automatically

When a skill finishes (`skill_finish write` or Cursor slash commands):

1. Report JSON + markdown written to `generated_projects/<run_id>/<skill>/`
2. Copy synced to `frontend/data/runs/<run_id>/<skill>.*`
3. Local server started on port 8765 (if not already running)
4. Browser opens to `/?run=<run_id>&skill=<skill>&live=1`
5. **Live runs** tab shows the report; I1/I2 Mermaid diagrams render as graphics

## Tabs

| Tab | Purpose |
|-----|---------|
| **Agents** | Browse all 24 skills, copy slash commands and file paths |
| **Pipeline** | Walk through all 24 agents on one target folder (Run all 24 button) |
| **Live runs** | Latest skill reports with auto-refresh |

## Run all 24 (Pipeline wizard)

1. Run `make serve-frontend` — **required** (provides `/api/pipeline/plan`).
2. Click **Run all 24** in the header or **Choose target folder** on the Pipeline tab.
3. Enter the full path to the repo you want to analyze.
4. For each step: copy the slash command → run in Cursor → **Mark done & next**.

Progress is stored in browser `localStorage`. Agents are **not** executed by the browser — only guided.

## Options

```bash
make serve-frontend PORT=9000      # custom port
make serve-frontend NO_OPEN=1      # start server without opening browser

export REPO_ANALYSER_AUTO_FRONTEND=0           # disable browser auto-open
export REPO_ANALYSER_AUTO_START_FRONTEND=0     # don't auto-start server
export REPO_ANALYSER_FRONTEND_PORT=9000        # custom port for auto-start
```

## Regenerate after spec changes

```bash
make build-skills
make build-frontend
```

## Note

This UI is a **guide and report viewer**. Agents still run in Cursor (real analysis) or via `make run-skill` (deterministic golden copy for testing).
