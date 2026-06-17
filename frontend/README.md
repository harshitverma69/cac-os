# Repo-Analyser local UI

Static browser guide for all 24 agents. **No deployment** — runs on your machine only.

See **[docs/SETUP.md](../docs/SETUP.md)** for the full setup guide (Cursor skills + auto-open flow).

## Quick start

```bash
cd Repo-Analyser
make setup              # first time only (includes build-frontend)
```

After setup, **you do not need to start this server manually**. Every `skill_finish write` auto-starts it and opens your browser to the **Live runs** tab.

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
| **Live runs** | Latest skill reports with auto-refresh |

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
