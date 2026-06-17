# Repo-Analyser local UI

Static browser guide for all 24 agents. **No deployment** — runs on your machine only.

## Run the frontend

```bash
cd Repo-Analyser
make build-frontend    # generate frontend/data/skills.json from registry
make serve-frontend    # optional — UI also auto-starts when a skill finishes
```

**While the server is running**, every skill you finish with `skill_finish write` (or Cursor slash commands) automatically appears under the **Live runs** tab.

Press `Ctrl+C` to stop the server.

### Options

```bash
make serve-frontend PORT=9000      # custom port
make serve-frontend NO_OPEN=1      # do not auto-open browser
```

## What you get

- All **24 agents** (B1–B6, I1–I6, A1–A6, D1–D6) as browsable cards
- **Run guide** per agent: Cursor slash command, file paths, finish commands
- **Search** and **filter by level**
- **Copy** buttons for setup and shell commands

## Regenerate after spec changes

```bash
make build-skills
make build-frontend
```

## Note

This UI is a **guide only**. Agents still run in Cursor (real work) or via `make run-skill` (deterministic golden copy for testing).
