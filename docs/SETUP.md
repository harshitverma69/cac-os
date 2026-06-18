# Repo-Analyser — Setup Guide

Complete setup so **Cursor skills**, the **terminal CLI**, and the **local frontend** all work together automatically.

---

## 1. Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Python 3.10+** | `python3 --version` |
| **Git** | Clone the repo |
| **Cursor** | For running `/repo-analyser-*` slash commands |
| **Browser** | Chrome, Safari, or Firefox (for the local UI) |
| **Network (first load)** | Mermaid ER diagrams load from jsDelivr CDN once |

Optional — for running tests locally:

```bash
cd Repo-Analyser
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install pytest pytest-cov
```

---

## 2. One-command setup

From a fresh clone:

```bash
git clone https://github.com/harshitverma69/Repo-Analyser.git
cd Repo-Analyser
make build-skills
make install-cursor-skills   # installs 24 /repo-analyser-* into ~/.cursor/skills/
make build-frontend
```

Or run `make setup` once (same three targets plus `make validate`).

**Restart Cursor completely** after install so `/repo-analyser-*` slash commands appear in chat.

---

## 3. What runs automatically

You do **not** need to keep a terminal open for the frontend. When any skill finishes, Repo-Analyser:

```
skill_finish write
       │
       ├─► generated_projects/<run_id>/<skill>/output.json
       ├─► generated_projects/<run_id>/<skill>/output.md
       ├─► Terminal CLI report (in Cursor terminal)
       ├─► frontend/data/live.json + runs/<run_id>/<skill>.*  (sync)
       ├─► Starts local UI server if not already running (port 8765)
       └─► Opens browser → Live runs tab with your report
```

### Example — analyze a repo with I1 (ER diagram)

In Cursor chat:

```
/repo-analyser-er-diagram @my-repo
```

When the agent finishes, it runs:

```bash
python3 -m runtime.skill_finish write \
  --run-id my-repo \
  --skill I1 \
  --payload-file payload.json
```

You get:

- **Terminal** — structured CLI summary
- **Browser** — `http://127.0.0.1:8765/?run=my-repo&skill=I1&live=1`
- **Live runs tab** — full markdown report + rendered Mermaid ER diagram
- **Files** — `generated_projects/my-repo/I1/output.json` and `output.md`

---

## 4. Local frontend UI

### Automatic (default)

The UI starts itself when a skill completes. No extra step required.

### Manual (optional)

Keep the UI open before you start working:

```bash
make serve-frontend
```

Opens `http://127.0.0.1:8765` with three tabs:

| Tab | Purpose |
|-----|---------|
| **Agents** | Browse all 24 skills, copy slash commands and file paths |
| **Pipeline** | Step through all 24 agents on one target folder (see below) |
| **Live runs** | Latest skill reports; auto-updates when `skill_finish write` runs |

**Important:** Open the UI via `make serve-frontend` (not by double-clicking `frontend/index.html`). The **Run all 24** wizard needs the local API at `POST /api/pipeline/plan`.

### Frontend options

```bash
make serve-frontend PORT=9000      # custom port
make serve-frontend NO_OPEN=1      # start server without opening browser
```

### Environment variables

| Variable | Default | Effect |
|----------|---------|--------|
| `REPO_ANALYSER_AUTO_FRONTEND` | `1` | Open browser when a skill finishes |
| `REPO_ANALYSER_AUTO_START_FRONTEND` | `1` | Start UI server in background if not running |
| `REPO_ANALYSER_FRONTEND_PORT` | `8765` | Port for the local UI |

Disable auto-open:

```bash
export REPO_ANALYSER_AUTO_FRONTEND=0
```

Disable auto-start (only open browser if server is already running):

```bash
export REPO_ANALYSER_AUTO_START_FRONTEND=0
make serve-frontend   # start manually first
```

---

## 5. Daily workflow

### Run all 24 agents on one folder (Pipeline wizard)

Use this when you want to analyze a whole repository end-to-end in dependency order.

1. Start the UI: `make serve-frontend` (leave the terminal open).
2. Open **http://127.0.0.1:8765** → click **Run all 24** (or open the **Pipeline** tab).
3. Enter the **full path** to the target repo (e.g. `/Users/you/projects/my-app`).
4. For each agent shown:
   - Copy the slash command (e.g. `/repo-analyser-er-diagram @/Users/you/projects/my-app`)
   - Paste and run it in **Cursor chat**
   - When finished, click **Mark done & next** (or let **Live runs** auto-advance when `skill_finish write` completes)
5. Progress is saved in your browser (`localStorage`) until you click **Reset**.

The wizard does **not** run agents for you — it tracks which step you are on and which command to run next.

### Run one skill on a target repo

1. Open Cursor in any workspace (Repo-Analyser or the target repo).
2. Type a slash command, e.g. `/repo-analyser-repo-inventory @../my-app`.
3. Let the agent complete the task and call `skill_finish write`.
4. Review the report in the browser (Live runs) or terminal.

### Re-view a past report

```bash
# Terminal CLI
make skill-done RUN_ID=my-repo SKILL=I1

# Browser (if server is running or will auto-start)
python3 -m runtime.skill_finish --run-id my-repo --skill I1

# Files directly
open generated_projects/my-repo/I1/output.md
```

### Run the deterministic test pipeline

```bash
make run-skill SKILL=B1 RUN_ID=demo
make run-pipeline RUN_ID=full-run
make validate-pipeline RUN_ID=full-run
```

---

## 6. After you change agent specs

Regenerate derived artifacts:

```bash
make build-skills      # skills/, registry, HOW_TO_RUN.md
make build-frontend    # frontend/data/skills.json
make install-cursor-skills   # if slash command names changed
```

---

## 7. Verify everything works

```bash
make validate          # specs + DAG
make test              # runtime unit tests
make harden            # full check (tests + determinism)
```

Quick smoke test for the frontend auto-open path:

```bash
# Uses existing golden output — no Cursor needed
make skill-done RUN_ID=repo-analyser SKILL=I1
```

You should see `Opened report → http://127.0.0.1:8765/...` in the terminal and the browser should open.

---

## 8. Troubleshooting

### Slash commands not in Cursor

```bash
make install-cursor-skills
```

Then **restart Cursor** completely.

### Browser does not open

- Check terminal for `Opened report → http://127.0.0.1:8765/...`
- Ensure `REPO_ANALYSER_AUTO_FRONTEND` is not `0`
- Open manually: `http://127.0.0.1:8765/?live=1`
- Or run `make serve-frontend` and refresh

### Run all 24 stuck on "Validating…" or connection refused

- The UI must be served by `make serve-frontend` — not opened as a `file://` URL or via a plain static server.
- Start the server: `cd Repo-Analyser && make serve-frontend`
- Refresh the browser and try again.

### Pipeline shows 0% and nothing happens

- Expected until you run the current agent in Cursor and click **Mark done & next**.
- Copy the command from the Pipeline tab, run it in chat, then advance manually.

### Port 8765 already in use

```bash
make serve-frontend PORT=9000
export REPO_ANALYSER_FRONTEND_PORT=9000
```

### ER diagram shows as raw text

- Hard-refresh the browser (`Cmd+Shift+R` / `Ctrl+Shift+R`)
- Ensure you have network access (Mermaid loads from CDN on first visit)
- Re-run `make skill-done RUN_ID=<run> SKILL=I1` to re-sync frontend data

### `frontend/data/skills.json` missing

```bash
make build-frontend
```

### Terminal CLI works but Live runs tab is empty

Re-publish the report:

```bash
python3 -m runtime.skill_finish --run-id <run_id> --skill <SKILL>
```

### `make validate` fails after editing specs

```bash
make build-skills
make validate
```

---

## 9. Repository layout (quick reference)

| Path | Role |
|------|------|
| `agents/` | Source agent specs |
| `skills/` | Compiled `.skill.md` execution specs |
| `runtime/skill_finish.py` | Write JSON + open CLI + sync frontend |
| `runtime/frontend_sync.py` | Publish runs to `frontend/data/` + auto-open browser |
| `frontend/` | Local browser UI (Agents + Live runs) |
| `generated_projects/{run_id}/` | Your skill outputs (`output.json`, `output.md`) |
| `generated_projects/_golden/` | Reference outputs for validation |

---

## 10. Related docs

| Doc | Contents |
|-----|----------|
| [HOW_TO_RUN.md](HOW_TO_RUN.md) | All 24 skills with file paths and commands |
| [OVERVIEW.md](OVERVIEW.md) | Architecture overview |
| [../frontend/README.md](../frontend/README.md) | Frontend UI details |
| [../README.md](../README.md) | Project summary |
